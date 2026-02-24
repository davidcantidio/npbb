"""Evaluate session/day coverage with actionable missing-input output.

This evaluator is focused on TMJ closure risks (especially show-day omissions)
and builds a report that differentiates:
- missing file/source in catalog (`gap`),
- extraction/resolution issues when source exists (`partial`).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import sys
from typing import Any, Iterable

from sqlmodel import Session

from .coverage_contract import (
    DEFAULT_COVERAGE_CONTRACT_PATH,
    CoverageContract,
    DatasetCoverageRule,
    coverage_requirements_from_contract,
    load_coverage_contract,
)
from .coverage_matrix import CoverageRequirementsConfig, CoverageMatrixRow, build_coverage_matrix
from .framework import Severity

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.etl_registry import CoverageDataset, IngestionStatus
    from app.models.models import EventSessionType
    from app.services.etl_coverage_queries import (
        SessionDatasetSourceCandidate,
        build_session_dataset_source_candidates,
    )
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.etl_registry import CoverageDataset, IngestionStatus
    from app.models.models import EventSessionType
    from app.services.etl_coverage_queries import (
        SessionDatasetSourceCandidate,
        build_session_dataset_source_candidates,
    )


_VALID_MISSING_STATUSES = {"gap", "partial"}


@dataclass(frozen=True)
class CoverageMissingInput:
    """One actionable missing-input item for one session+dataset."""

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    dataset: CoverageDataset
    status: str
    severity: Severity
    reason_code: str
    reason: str
    expected_artifact: str
    request_action: str
    sources_considered: tuple[str, ...]
    source_statuses: tuple[str, ...]
    source_match_scopes: tuple[str, ...]
    lineage_note: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize missing-input item into JSON-friendly dictionary."""

        return {
            "session_id": self.session_id,
            "session_key": self.session_key,
            "session_date": self.session_date.isoformat(),
            "session_type": self.session_type.value,
            "dataset": self.dataset.value,
            "status": self.status,
            "severity": self.severity.value,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "expected_artifact": self.expected_artifact,
            "request_action": self.request_action,
            "sources_considered": list(self.sources_considered),
            "source_statuses": list(self.source_statuses),
            "source_match_scopes": list(self.source_match_scopes),
            "lineage_note": self.lineage_note,
        }


@dataclass(frozen=True)
class SessionCoverageStatus:
    """Coverage status summary for one session."""

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    status: str
    observed_datasets: tuple[CoverageDataset, ...]
    partial_datasets: tuple[CoverageDataset, ...]
    missing_datasets: tuple[CoverageDataset, ...]
    missing_inputs: tuple[CoverageMissingInput, ...]

    def to_dict(self) -> dict[str, Any]:
        """Serialize session coverage summary to JSON-friendly dictionary."""

        return {
            "session_id": self.session_id,
            "session_key": self.session_key,
            "session_date": self.session_date.isoformat(),
            "session_type": self.session_type.value,
            "status": self.status,
            "observed_datasets": [dataset.value for dataset in self.observed_datasets],
            "partial_datasets": [dataset.value for dataset in self.partial_datasets],
            "missing_datasets": [dataset.value for dataset in self.missing_datasets],
            "missing_inputs": [item.to_dict() for item in self.missing_inputs],
        }


@dataclass(frozen=True)
class CoverageReport:
    """Top-level coverage evaluator output contract."""

    generated_at: datetime
    event_id: int | None
    contract_version: int
    status: str
    summary: dict[str, int]
    sessions: tuple[SessionCoverageStatus, ...]
    missing_inputs: tuple[CoverageMissingInput, ...]

    def to_dict(self) -> dict[str, Any]:
        """Serialize report as JSON-friendly mapping."""

        return {
            "generated_at": self.generated_at.isoformat(),
            "event_id": self.event_id,
            "contract_version": self.contract_version,
            "status": self.status,
            "summary": dict(self.summary),
            "sessions": [item.to_dict() for item in self.sessions],
            "missing_inputs": [item.to_dict() for item in self.missing_inputs],
        }


def _normalize_focus_dates(focus_dates: Iterable[date] | None) -> tuple[date, ...]:
    """Normalize and deduplicate optional date filter for report helpers."""

    if focus_dates is None:
        return ()
    return tuple(sorted({item for item in focus_dates}))


def find_show_access_control_missing_inputs(
    report: CoverageReport,
    *,
    include_partial: bool = True,
    focus_dates: Iterable[date] | None = None,
) -> tuple[CoverageMissingInput, ...]:
    """Return show-session `access_control` missing items from one report.

    Args:
        report: Coverage report generated by `evaluate_coverage`.
        include_partial: Include `partial` status items in addition to `gap`.
        focus_dates: Optional date filter (for example: 12/12 and 14/12 focus).

    Returns:
        Sorted tuple of show-session missing-input rows for `access_control`.
    """

    allowed_status = {"gap", "partial"} if include_partial else {"gap"}
    scoped_dates = set(_normalize_focus_dates(focus_dates))

    selected: list[CoverageMissingInput] = []
    for item in report.missing_inputs:
        if item.session_type != EventSessionType.NOTURNO_SHOW:
            continue
        if item.dataset != CoverageDataset.ACCESS_CONTROL:
            continue
        if item.status not in allowed_status:
            continue
        if scoped_dates and item.session_date not in scoped_dates:
            continue
        selected.append(item)

    return tuple(
        sorted(
            selected,
            key=lambda item: (
                item.session_date,
                item.session_key,
                item.status,
                item.reason_code,
            ),
        )
    )


def find_show_optin_missing_inputs(
    report: CoverageReport,
    *,
    include_partial: bool = True,
    focus_dates: Iterable[date] | None = None,
) -> tuple[CoverageMissingInput, ...]:
    """Return show-session `optin` missing items from one report.

    Args:
        report: Coverage report generated by `evaluate_coverage`.
        include_partial: Include `partial` status items in addition to `gap`.
        focus_dates: Optional date filter (for example: 12/12 and 14/12 focus).

    Returns:
        Sorted tuple of show-session missing-input rows for `optin`.
    """

    allowed_status = {"gap", "partial"} if include_partial else {"gap"}
    scoped_dates = set(_normalize_focus_dates(focus_dates))

    selected: list[CoverageMissingInput] = []
    for item in report.missing_inputs:
        if item.session_type != EventSessionType.NOTURNO_SHOW:
            continue
        if item.dataset != CoverageDataset.OPTIN:
            continue
        if item.status not in allowed_status:
            continue
        if scoped_dates and item.session_date not in scoped_dates:
            continue
        selected.append(item)

    return tuple(
        sorted(
            selected,
            key=lambda item: (
                item.session_date,
                item.session_key,
                item.status,
                item.reason_code,
            ),
        )
    )


def _build_requirements_config(contract: CoverageContract) -> CoverageRequirementsConfig:
    """Convert full contract into matrix requirements configuration."""

    requirements = coverage_requirements_from_contract(contract)
    return CoverageRequirementsConfig(
        default_required_datasets=requirements.default_required_datasets,
        required_datasets_by_session_type=requirements.required_datasets_by_session_type,
    )


def _rule_for_dataset(
    contract: CoverageContract,
    *,
    session_type: EventSessionType,
    dataset: CoverageDataset,
) -> DatasetCoverageRule:
    """Return coverage rule for one session-type/dataset with deterministic fallback."""

    session_contract = contract.session_types.get(session_type)
    if session_contract is not None:
        for rule in session_contract.datasets:
            if rule.dataset == dataset:
                return rule

    return DatasetCoverageRule(
        dataset=dataset,
        required=(dataset in contract.default_required_datasets),
        severity=Severity.WARNING,
        status_on_missing="gap",
        description=None,
    )


def _expected_artifact(dataset: CoverageDataset, session_type: EventSessionType) -> str:
    """Return a short expected-artifact description for one dataset."""

    show_hint = " da sessao de show" if session_type == EventSessionType.NOTURNO_SHOW else ""
    mapping = {
        CoverageDataset.ACCESS_CONTROL: (
            f"PDF de controle de acesso{show_hint} com ingressos_validos/presentes/ausentes."
        ),
        CoverageDataset.TICKET_SALES: (
            f"Base de vendas{show_hint} com sold_total e net_sold_total por sessao."
        ),
        CoverageDataset.OPTIN: f"XLSX de opt-in/Eventim{show_hint} em granularidade transacional.",
        CoverageDataset.LEADS: f"XLSX de leads{show_hint} com colunas canonicas de captura.",
        CoverageDataset.OTHER: "Arquivo fonte catalogado para o dataset esperado.",
    }
    return mapping[dataset]


def _candidate_status_values(
    candidates: list[SessionDatasetSourceCandidate],
) -> tuple[str, ...]:
    """Return deterministic latest-status tuple from candidate rows."""

    values = sorted(
        {
            candidate.latest_status.value if candidate.latest_status is not None else "no_run"
            for candidate in candidates
        }
    )
    return tuple(values)


def _resolve_missing_status(
    *,
    matrix_row: CoverageMatrixRow,
    rule: DatasetCoverageRule,
    candidates: list[SessionDatasetSourceCandidate],
) -> tuple[str, str, str]:
    """Resolve missing status, reason code and reason message.

    Returns:
        Tuple (`status`, `reason_code`, `reason`).
    """

    if matrix_row.matrix_status == "partial":
        return (
            "partial",
            "ingestion_partial",
            "Cobertura parcial observada para o dataset na sessao.",
        )

    if matrix_row.matrix_status != "gap":
        return ("gap", "unexpected_status", "Status de cobertura nao reconhecido no evaluator.")

    if not candidates:
        status = rule.status_on_missing if rule.status_on_missing in _VALID_MISSING_STATUSES else "gap"
        return (
            status,
            "missing_in_catalog",
            "Nenhuma fonte correspondente foi encontrada no catalogo para sessao+dataset.",
        )

    has_failed = any(candidate.latest_status == IngestionStatus.FAILED for candidate in candidates)
    has_partial = any(candidate.latest_status == IngestionStatus.PARTIAL for candidate in candidates)
    has_success = any(candidate.latest_status == IngestionStatus.SUCCESS for candidate in candidates)

    if has_failed:
        reason_code = "ingestion_failed"
        reason = "Fonte encontrada, mas a ultima ingestao terminou como failed."
    elif has_partial:
        reason_code = "ingestion_partial"
        reason = "Fonte encontrada, mas a ultima ingestao terminou como partial."
    elif has_success:
        reason_code = "session_resolution_gap"
        reason = "Fonte encontrada com success, mas sem cobertura efetiva na sessao."
    else:
        reason_code = "catalog_without_run"
        reason = "Fonte catalogada sem status de ingestao concluido."
    return ("partial", reason_code, reason)


def _build_request_action(
    *,
    missing_status: str,
    expected_artifact: str,
    candidates: list[SessionDatasetSourceCandidate],
) -> str:
    """Build one short actionable request/recovery message."""

    if missing_status == "gap":
        return f"Solicitar: {expected_artifact}"

    source_ids = sorted({candidate.source_id for candidate in candidates})
    if source_ids:
        joined = ", ".join(source_ids)
        return (
            "Reprocessar/validar extractor para as fontes catalogadas "
            f"({joined}) e confirmar cobertura da sessao."
        )
    return f"Reprocessar ingestao e validar cobertura do artefato esperado: {expected_artifact}"


def _build_lineage_note(
    *,
    matrix_row: CoverageMatrixRow,
    candidates: list[SessionDatasetSourceCandidate],
) -> str:
    """Build lineage note explaining how missing reason was derived."""

    if not candidates:
        return (
            "Motivo derivado de ausencia no catalogo: nenhuma fonte encontrada em "
            "latest_ingestion_by_source apos inferencia por session_key/dia+tipo."
        )
    return (
        "Motivo derivado de divergencia entre coverage_matrix e catalogo: fontes "
        "foram encontradas, mas a celula sessao+dataset permaneceu sem cobertura efetiva."
    )


def evaluate_coverage(
    session: Session,
    *,
    event_id: int | None = None,
    contract_path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
) -> CoverageReport:
    """Evaluate session coverage and generate actionable missing-input report.

    Args:
        session: Open SQLModel session.
        event_id: Optional event filter.
        contract_path: Coverage contract YAML path.

    Returns:
        Coverage report with session status and `missing_inputs` details.

    Raises:
        FileNotFoundError: If contract file does not exist.
        ValueError: If contract content is invalid.
    """

    contract = load_coverage_contract(contract_path)
    cfg = _build_requirements_config(contract)

    matrix_rows = build_coverage_matrix(
        session,
        event_id=event_id,
        config=cfg,
    )

    dataset_domain: set[CoverageDataset] = set(cfg.default_required_datasets)
    for datasets in cfg.required_datasets_by_session_type.values():
        dataset_domain.update(datasets)

    candidates = build_session_dataset_source_candidates(
        session,
        event_id=event_id,
        expected_datasets=tuple(sorted(dataset_domain, key=lambda item: item.value)),
    )
    candidates_by_cell: dict[tuple[int, CoverageDataset], list[SessionDatasetSourceCandidate]] = (
        defaultdict(list)
    )
    for candidate in candidates:
        candidates_by_cell[(candidate.session_id, candidate.dataset)].append(candidate)

    by_session_rows: dict[int, list[CoverageMatrixRow]] = defaultdict(list)
    for row in matrix_rows:
        by_session_rows[row.session_id].append(row)

    missing_inputs_all: list[CoverageMissingInput] = []
    sessions_output: list[SessionCoverageStatus] = []

    for session_id, rows in sorted(
        by_session_rows.items(),
        key=lambda item: (
            item[1][0].session_date,
            item[1][0].session_type.value,
            item[1][0].session_key,
        ),
    ):
        ordered_rows = sorted(rows, key=lambda item: item.dataset.value)
        observed: set[CoverageDataset] = set()
        partial_datasets: set[CoverageDataset] = set()
        missing_datasets: set[CoverageDataset] = set()
        session_missing_inputs: list[CoverageMissingInput] = []

        first_row = ordered_rows[0]
        for row in ordered_rows:
            if row.matrix_status in {"ok", "partial"}:
                observed.add(row.dataset)
            if row.matrix_status == "partial":
                partial_datasets.add(row.dataset)

            if row.matrix_status == "ok":
                continue

            candidates_for_cell = candidates_by_cell.get((row.session_id, row.dataset), [])
            rule = _rule_for_dataset(
                contract,
                session_type=row.session_type,
                dataset=row.dataset,
            )
            missing_status, reason_code, reason = _resolve_missing_status(
                matrix_row=row,
                rule=rule,
                candidates=candidates_for_cell,
            )
            if missing_status == "gap":
                missing_datasets.add(row.dataset)
            if missing_status == "partial":
                partial_datasets.add(row.dataset)

            expected_artifact = _expected_artifact(row.dataset, row.session_type)
            source_ids = tuple(sorted({candidate.source_id for candidate in candidates_for_cell}))
            match_scopes = tuple(
                sorted({candidate.match_scope for candidate in candidates_for_cell})
            )
            missing_item = CoverageMissingInput(
                session_id=row.session_id,
                session_key=row.session_key,
                session_date=row.session_date,
                session_type=row.session_type,
                dataset=row.dataset,
                status=missing_status,
                severity=rule.severity,
                reason_code=reason_code,
                reason=reason,
                expected_artifact=expected_artifact,
                request_action=_build_request_action(
                    missing_status=missing_status,
                    expected_artifact=expected_artifact,
                    candidates=candidates_for_cell,
                ),
                sources_considered=source_ids,
                source_statuses=_candidate_status_values(candidates_for_cell),
                source_match_scopes=match_scopes,
                lineage_note=_build_lineage_note(
                    matrix_row=row,
                    candidates=candidates_for_cell,
                ),
            )
            session_missing_inputs.append(missing_item)
            missing_inputs_all.append(missing_item)

        session_status = "ok"
        if missing_datasets:
            session_status = "gap"
        elif partial_datasets:
            session_status = "partial"

        sessions_output.append(
            SessionCoverageStatus(
                session_id=session_id,
                session_key=first_row.session_key,
                session_date=first_row.session_date,
                session_type=first_row.session_type,
                status=session_status,
                observed_datasets=tuple(sorted(observed, key=lambda item: item.value)),
                partial_datasets=tuple(sorted(partial_datasets, key=lambda item: item.value)),
                missing_datasets=tuple(sorted(missing_datasets, key=lambda item: item.value)),
                missing_inputs=tuple(
                    sorted(session_missing_inputs, key=lambda item: item.dataset.value)
                ),
            )
        )

    total_sessions = len(sessions_output)
    ok_sessions = sum(1 for row in sessions_output if row.status == "ok")
    partial_sessions = sum(1 for row in sessions_output if row.status == "partial")
    gap_sessions = sum(1 for row in sessions_output if row.status == "gap")

    report_status = "ok"
    if gap_sessions:
        report_status = "gap"
    elif partial_sessions:
        report_status = "partial"

    summary = {
        "total_sessions": total_sessions,
        "ok_sessions": ok_sessions,
        "partial_sessions": partial_sessions,
        "gap_sessions": gap_sessions,
        "total_missing_inputs": len(missing_inputs_all),
        "gap_missing_inputs": sum(1 for item in missing_inputs_all if item.status == "gap"),
        "partial_missing_inputs": sum(
            1 for item in missing_inputs_all if item.status == "partial"
        ),
    }

    return CoverageReport(
        generated_at=datetime.now(timezone.utc),
        event_id=event_id,
        contract_version=contract.version,
        status=report_status,
        summary=summary,
        sessions=tuple(sessions_output),
        missing_inputs=tuple(
            sorted(
                missing_inputs_all,
                key=lambda item: (
                    item.session_date,
                    item.session_type.value,
                    item.session_key,
                    item.dataset.value,
                ),
            )
        ),
    )


def evaluate_coverage_payload(
    session: Session,
    *,
    event_id: int | None = None,
    contract_path: Path | str = DEFAULT_COVERAGE_CONTRACT_PATH,
) -> dict[str, Any]:
    """Evaluate coverage and return JSON-friendly payload."""

    return evaluate_coverage(
        session,
        event_id=event_id,
        contract_path=contract_path,
    ).to_dict()
