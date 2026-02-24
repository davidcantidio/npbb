"""Coverage matrix by session/day using required datasets per session type.

This module loads configurable dataset requirements from `datasets.yml` and
builds a session x dataset matrix with normalized status:
- `ok`: dataset observed for the session
- `partial`: observed with partial ingestion status
- `gap`: missing/failed/unknown coverage
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

import sqlalchemy as sa
from sqlmodel import Session, select
import yaml

from .coverage_contract import (
    DEFAULT_COVERAGE_CONTRACT_PATH,
    CoverageContractError,
    coverage_requirements_from_contract,
    load_coverage_contract,
)

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.etl_registry import CoverageDataset, CoverageStatus, IngestionStatus
    from app.models.models import EventSession, EventSessionType
    from app.services.etl_catalog_queries import LatestIngestionBySourceRow
    from app.services.etl_coverage_queries import (
        DEFAULT_COVERAGE_DATASETS,
        build_session_coverage_matrix,
        unresolved_staging_records_by_dataset,
    )
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.etl_registry import CoverageDataset, CoverageStatus, IngestionStatus
    from app.models.models import EventSession, EventSessionType
    from app.services.etl_catalog_queries import LatestIngestionBySourceRow
    from app.services.etl_coverage_queries import (
        DEFAULT_COVERAGE_DATASETS,
        build_session_coverage_matrix,
        unresolved_staging_records_by_dataset,
    )


DEFAULT_DATASETS_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "datasets.yml"


class CoverageMatrixConfigError(ValueError):
    """Raised when coverage requirements configuration is invalid."""


@dataclass(frozen=True)
class CoverageRequirementsConfig:
    """Coverage requirements configuration by session type.

    Args:
        default_required_datasets: Datasets required when session type has no
            explicit mapping.
        required_datasets_by_session_type: Explicit requirement mapping by
            canonical session type (`DIURNO_GRATUITO`, `NOTURNO_SHOW`, `OUTRO`).
    """

    default_required_datasets: tuple[CoverageDataset, ...]
    required_datasets_by_session_type: dict[EventSessionType, tuple[CoverageDataset, ...]]


@dataclass(frozen=True)
class CoverageMatrixRow:
    """One coverage matrix row for session x required dataset.

    Args:
        session_id: Session identifier.
        session_key: Stable session key.
        session_date: Session date.
        session_type: Canonical session type.
        dataset: Required dataset.
        coverage_status: Raw backend coverage status.
        matrix_status: Normalized matrix status (`ok`/`partial`/`gap`).
        sources_present: Observed sources for the cell.
        ingestion_ids: Observed ingestion IDs for the cell.
        latest_statuses: Observed latest ingestion statuses for the cell.
    """

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    dataset: CoverageDataset
    coverage_status: CoverageStatus
    matrix_status: str
    sources_present: tuple[str, ...]
    ingestion_ids: tuple[int, ...]
    latest_statuses: tuple[IngestionStatus, ...]


@dataclass(frozen=True)
class CoverageMatrixSummaryRow:
    """Session-level summary derived from required-dataset coverage matrix."""

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    status: str
    observed_datasets: tuple[CoverageDataset, ...]
    partial_datasets: tuple[CoverageDataset, ...]
    missing_datasets: tuple[CoverageDataset, ...]


def _normalize_session_type(value: Any) -> EventSessionType:
    """Normalize raw session type input into canonical enum.

    Args:
        value: Raw session type from config or model.

    Returns:
        Canonical `EventSessionType` value.

    Raises:
        CoverageMatrixConfigError: If session type is unsupported.
    """

    if isinstance(value, EventSessionType):
        return value
    text = str(value or "").strip().upper()
    if not text:
        raise CoverageMatrixConfigError(
            "session_type invalido em coverage_requirements. Como corrigir: informar valor nao vazio."
        )
    if text in EventSessionType.__members__:
        return EventSessionType[text]
    for session_type in EventSessionType:
        if session_type.value.upper() == text:
            return session_type
    raise CoverageMatrixConfigError(
        "session_type invalido em coverage_requirements. "
        "Como corrigir: usar DIURNO_GRATUITO|NOTURNO_SHOW|OUTRO."
    )


def _normalize_dataset(value: Any) -> CoverageDataset:
    """Normalize raw dataset identifier to canonical enum.

    Args:
        value: Raw dataset string.

    Returns:
        Canonical `CoverageDataset` value.

    Raises:
        CoverageMatrixConfigError: If dataset is unsupported.
    """

    text = str(value or "").strip().lower()
    if not text:
        raise CoverageMatrixConfigError(
            "dataset invalido em coverage_requirements. Como corrigir: informar valor nao vazio."
        )
    aliases = {
        "access": "access_control",
        "sales": "ticket_sales",
    }
    normalized = aliases.get(text, text)
    try:
        return CoverageDataset(normalized)
    except ValueError as exc:
        raise CoverageMatrixConfigError(
            "dataset invalido em coverage_requirements. "
            "Como corrigir: usar access_control|ticket_sales|optin|leads."
        ) from exc


def _normalize_dataset_list(raw: Any, *, field_name: str) -> tuple[CoverageDataset, ...]:
    """Parse one dataset-list field from config payload."""

    if not isinstance(raw, list):
        raise CoverageMatrixConfigError(
            f"Campo {field_name!r} deve ser lista em coverage_requirements."
        )
    values: list[CoverageDataset] = []
    seen: set[CoverageDataset] = set()
    for item in raw:
        dataset = _normalize_dataset(item)
        if dataset in seen:
            continue
        seen.add(dataset)
        values.append(dataset)
    if not values:
        raise CoverageMatrixConfigError(
            f"Campo {field_name!r} nao pode ser vazio em coverage_requirements."
        )
    return tuple(values)


def _default_coverage_requirements() -> CoverageRequirementsConfig:
    """Return safe default requirements when config section is missing."""

    return CoverageRequirementsConfig(
        default_required_datasets=tuple(DEFAULT_COVERAGE_DATASETS),
        required_datasets_by_session_type={},
    )


def _requirements_from_contract_path(path: Path) -> CoverageRequirementsConfig:
    """Load and convert `coverage_contract.yml` into matrix requirement view."""

    try:
        contract = load_coverage_contract(path)
    except CoverageContractError as exc:
        raise CoverageMatrixConfigError(str(exc)) from exc

    requirements = coverage_requirements_from_contract(contract)
    return CoverageRequirementsConfig(
        default_required_datasets=requirements.default_required_datasets,
        required_datasets_by_session_type=requirements.required_datasets_by_session_type,
    )


def load_coverage_requirements_config(
    path: Path | str | None = None,
) -> CoverageRequirementsConfig:
    """Load coverage requirements from YAML config.

    Args:
        path: Optional YAML path. Defaults to bundled `datasets.yml`.

    Returns:
        Parsed coverage requirements config. When section is absent, returns
        default requirements (`DEFAULT_COVERAGE_DATASETS` for all session types).

    Raises:
        FileNotFoundError: If config path does not exist.
        CoverageMatrixConfigError: If section is malformed.
    """

    config_path: Path
    if path is None:
        if DEFAULT_COVERAGE_CONTRACT_PATH.exists():
            return _requirements_from_contract_path(DEFAULT_COVERAGE_CONTRACT_PATH)
        config_path = DEFAULT_DATASETS_CONFIG_PATH
    else:
        config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Dataset config YAML not found: {config_path}")

    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, Mapping):
        raise CoverageMatrixConfigError(
            "datasets.yml invalido. Como corrigir: estrutura raiz deve ser objeto YAML."
        )

    # New format: dedicated coverage contract by session type.
    if "session_types" in payload:
        return _requirements_from_contract_path(config_path)

    section = payload.get("coverage_requirements")
    if section in (None, ""):
        return _default_coverage_requirements()
    if not isinstance(section, Mapping):
        raise CoverageMatrixConfigError(
            "Campo 'coverage_requirements' invalido. Como corrigir: usar objeto YAML."
        )

    default_required_raw = section.get("default_required_datasets")
    if default_required_raw is None:
        default_required = tuple(DEFAULT_COVERAGE_DATASETS)
    else:
        default_required = _normalize_dataset_list(
            default_required_raw,
            field_name="default_required_datasets",
        )

    mapping_raw = section.get("required_datasets_by_session_type", {})
    if mapping_raw is None:
        mapping_raw = {}
    if not isinstance(mapping_raw, Mapping):
        raise CoverageMatrixConfigError(
            "Campo 'required_datasets_by_session_type' invalido. "
            "Como corrigir: usar objeto YAML (session_type -> [datasets])."
        )

    mapping: dict[EventSessionType, tuple[CoverageDataset, ...]] = {}
    for raw_session_type, raw_datasets in mapping_raw.items():
        session_type = _normalize_session_type(raw_session_type)
        mapping[session_type] = _normalize_dataset_list(
            raw_datasets,
            field_name=f"required_datasets_by_session_type.{session_type.value}",
        )

    return CoverageRequirementsConfig(
        default_required_datasets=default_required,
        required_datasets_by_session_type=mapping,
    )


def required_datasets_for_session_type(
    session_type: EventSessionType | str,
    config: CoverageRequirementsConfig,
) -> tuple[CoverageDataset, ...]:
    """Resolve required datasets for one session type.

    Args:
        session_type: Session type enum or string.
        config: Coverage requirements config.

    Returns:
        Required dataset tuple for the given session type.
    """

    normalized = _normalize_session_type(session_type)
    return config.required_datasets_by_session_type.get(
        normalized,
        config.default_required_datasets,
    )


def _normalize_matrix_status(status: CoverageStatus) -> str:
    """Normalize backend coverage status into matrix contract status."""

    if status == CoverageStatus.OBSERVED:
        return "ok"
    if status == CoverageStatus.OBSERVED_PARTIAL:
        return "partial"
    return "gap"


def _table_exists(session: Session, table_name: str) -> bool:
    """Return whether table exists on current DB bind."""

    bind = session.get_bind()
    if bind is None:
        return False
    return bool(sa.inspect(bind).has_table(table_name))


def build_coverage_matrix(
    session: Session,
    *,
    event_id: int | None = None,
    config: CoverageRequirementsConfig | None = None,
    config_path: Path | str | None = None,
    latest_rows: Iterable[LatestIngestionBySourceRow] | None = None,
) -> list[CoverageMatrixRow]:
    """Build required-dataset coverage matrix by session type.

    Args:
        session: Open database session.
        event_id: Optional event filter.
        config: Optional preloaded coverage config.
        config_path: Optional config path when `config` is not supplied.
        latest_rows: Optional latest-source rows for deterministic tests.

    Returns:
        Coverage matrix rows filtered by required datasets for each session type.
        Returns empty list when `event_sessions` table is missing.
    """

    if not _table_exists(session, "event_sessions"):
        return []

    cfg = config or load_coverage_requirements_config(config_path)
    stmt_sessions = select(EventSession)
    if event_id is not None:
        stmt_sessions = stmt_sessions.where(EventSession.event_id == event_id)
    stmt_sessions = stmt_sessions.order_by(
        EventSession.session_date,
        EventSession.session_type,
        EventSession.session_key,
    )
    sessions = session.exec(stmt_sessions).all()
    if not sessions:
        return []

    required_by_session_id: dict[int, tuple[CoverageDataset, ...]] = {}
    required_union: set[CoverageDataset] = set()
    for sess in sessions:
        session_id = int(sess.id)
        required = required_datasets_for_session_type(sess.session_type, cfg)
        required_by_session_id[session_id] = required
        required_union.update(required)

    if not required_union:
        return []

    base_rows = build_session_coverage_matrix(
        session,
        event_id=event_id,
        expected_datasets=tuple(sorted(required_union, key=lambda dataset: dataset.value)),
        latest_rows=latest_rows,
    )
    output: list[CoverageMatrixRow] = []
    for row in base_rows:
        required = required_by_session_id.get(int(row.session_id), ())
        if row.dataset not in required:
            continue
        output.append(
            CoverageMatrixRow(
                session_id=int(row.session_id),
                session_key=row.session_key,
                session_date=row.session_date,
                session_type=row.session_type,
                dataset=row.dataset,
                coverage_status=row.status,
                matrix_status=_normalize_matrix_status(row.status),
                sources_present=tuple(row.sources_present),
                ingestion_ids=tuple(row.ingestion_ids),
                latest_statuses=tuple(row.latest_statuses),
            )
        )

    return sorted(
        output,
        key=lambda item: (
            item.session_date,
            item.session_type.value,
            item.session_key,
            item.dataset.value,
        ),
    )


def build_coverage_matrix_summary(
    rows: Sequence[CoverageMatrixRow],
) -> list[CoverageMatrixSummaryRow]:
    """Aggregate coverage matrix rows into session-level summary."""

    grouped: dict[int, list[CoverageMatrixRow]] = defaultdict(list)
    for row in rows:
        grouped[row.session_id].append(row)

    summary_rows: list[CoverageMatrixSummaryRow] = []
    for session_id, session_rows in grouped.items():
        first = session_rows[0]
        observed = tuple(
            sorted(
                {
                    item.dataset
                    for item in session_rows
                    if item.matrix_status in {"ok", "partial"}
                },
                key=lambda dataset: dataset.value,
            )
        )
        partial = tuple(
            sorted(
                {item.dataset for item in session_rows if item.matrix_status == "partial"},
                key=lambda dataset: dataset.value,
            )
        )
        missing = tuple(
            sorted(
                {item.dataset for item in session_rows if item.matrix_status == "gap"},
                key=lambda dataset: dataset.value,
            )
        )
        if missing:
            status = "gap"
        elif partial:
            status = "partial"
        else:
            status = "ok"

        summary_rows.append(
            CoverageMatrixSummaryRow(
                session_id=session_id,
                session_key=first.session_key,
                session_date=first.session_date,
                session_type=first.session_type,
                status=status,
                observed_datasets=observed,
                partial_datasets=partial,
                missing_datasets=missing,
            )
        )

    return sorted(
        summary_rows,
        key=lambda item: (item.session_date, item.session_type.value, item.session_key),
    )


def coverage_matrix_rows_to_dicts(
    rows: Iterable[CoverageMatrixRow],
) -> list[dict[str, Any]]:
    """Serialize matrix rows to JSON-friendly dictionaries."""

    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append(
            {
                "session_id": row.session_id,
                "session_key": row.session_key,
                "session_date": row.session_date.isoformat(),
                "session_type": row.session_type.value,
                "dataset": row.dataset.value,
                "status": row.matrix_status,
                "coverage_status": row.coverage_status.value,
                "sources_present": list(row.sources_present),
                "ingestion_ids": list(row.ingestion_ids),
                "latest_statuses": [item.value for item in row.latest_statuses],
            }
        )
    return payload


def coverage_matrix_summary_to_dicts(
    rows: Iterable[CoverageMatrixSummaryRow],
) -> list[dict[str, Any]]:
    """Serialize summary rows to JSON-friendly dictionaries."""

    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append(
            {
                "session_id": row.session_id,
                "session_key": row.session_key,
                "session_date": row.session_date.isoformat(),
                "session_type": row.session_type.value,
                "status": row.status,
                "observed_datasets": [dataset.value for dataset in row.observed_datasets],
                "partial_datasets": [dataset.value for dataset in row.partial_datasets],
                "missing_datasets": [dataset.value for dataset in row.missing_datasets],
            }
        )
    return payload


def build_coverage_matrix_payload(
    session: Session,
    *,
    event_id: int | None = None,
    config: CoverageRequirementsConfig | None = None,
    config_path: Path | str | None = None,
    latest_rows: Iterable[LatestIngestionBySourceRow] | None = None,
) -> dict[str, Any]:
    """Build JSON-friendly coverage payload for DQ/report integration.

    Args:
        session: Open database session.
        event_id: Optional event filter.
        config: Optional preloaded config.
        config_path: Optional config path when `config` is not supplied.
        latest_rows: Optional latest-source rows for deterministic tests.

    Returns:
        Payload with summary, session status list and coverage matrix list.
        When required tables are unavailable, returns `status=skipped`.
    """

    cfg = config or load_coverage_requirements_config(config_path)
    generated_at = datetime.now(timezone.utc).isoformat()

    if not _table_exists(session, "event_sessions"):
        return {
            "generated_at": generated_at,
            "event_id": event_id,
            "status": "skipped",
            "reason": "Tabela event_sessions nao encontrada.",
            "summary": {
                "total_sessions": 0,
                "ok_sessions": 0,
                "partial_sessions": 0,
                "gap_sessions": 0,
            },
            "sessions": [],
            "matrix": [],
            "unresolved_without_session": {},
            "config": {
                "default_required_datasets": [
                    dataset.value for dataset in cfg.default_required_datasets
                ],
                "required_datasets_by_session_type": {
                    session_type.value: [dataset.value for dataset in datasets]
                    for session_type, datasets in cfg.required_datasets_by_session_type.items()
                },
            },
        }

    matrix_rows = build_coverage_matrix(
        session,
        event_id=event_id,
        config=cfg,
        latest_rows=latest_rows,
    )
    summary_rows = build_coverage_matrix_summary(matrix_rows)

    datasets_domain: set[CoverageDataset] = set(cfg.default_required_datasets)
    for datasets in cfg.required_datasets_by_session_type.values():
        datasets_domain.update(datasets)

    unresolved = unresolved_staging_records_by_dataset(
        session,
        event_id=event_id,
        expected_datasets=tuple(sorted(datasets_domain, key=lambda dataset: dataset.value)),
    )

    summary_payload = coverage_matrix_summary_to_dicts(summary_rows)
    matrix_payload = coverage_matrix_rows_to_dicts(matrix_rows)

    total_sessions = len(summary_payload)
    ok_sessions = sum(1 for row in summary_payload if row["status"] == "ok")
    partial_sessions = sum(1 for row in summary_payload if row["status"] == "partial")
    gap_sessions = total_sessions - ok_sessions - partial_sessions

    return {
        "generated_at": generated_at,
        "event_id": event_id,
        "status": "ok",
        "summary": {
            "total_sessions": total_sessions,
            "ok_sessions": ok_sessions,
            "partial_sessions": partial_sessions,
            "gap_sessions": gap_sessions,
        },
        "sessions": summary_payload,
        "matrix": matrix_payload,
        "unresolved_without_session": {
            dataset.value: int(count) for dataset, count in unresolved.items()
        },
        "config": {
            "default_required_datasets": [
                dataset.value for dataset in cfg.default_required_datasets
            ],
            "required_datasets_by_session_type": {
                session_type.value: [dataset.value for dataset in datasets]
                for session_type, datasets in cfg.required_datasets_by_session_type.items()
            },
        },
    }
