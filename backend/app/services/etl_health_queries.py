"""Health queries for ETL operational status by source.

This module builds a deterministic source-health snapshot combining:
- latest ingestion status per source;
- loaded row counts (staging/canonical) by latest ingestion;
- DQ fail counts and operator notes for triage.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional

import sqlalchemy as sa
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.dq_results import DQCheckResult, DQCheckSeverity, DQCheckStatus
from app.models.etl_lineage import LineageRef  # noqa: F401
from app.models.etl_registry import (
    HEALTH_CANONICAL_TABLES,
    IngestionRun,
    IngestionStatus,
    SourceHealthStatus,
    SourceKind,
)
from app.services.etl_catalog_queries import latest_ingestion_by_source


@dataclass(frozen=True)
class SourceHealthRow:
    """Operational health snapshot row for one source.

    Attributes:
        source_id: Stable source identifier.
        source_kind: Source type (`pdf`, `xlsx`, `pptx`, etc.).
        source_uri: Source URI/path.
        source_display_name: Optional source display name.
        source_is_active: Source active flag.
        latest_ingestion_id: Latest ingestion run id for source.
        latest_status: Latest ingestion status.
        latest_started_at: Latest run start timestamp.
        latest_finished_at: Latest run finish timestamp.
        latest_notes: Notes from latest run.
        latest_error_message: Error text from latest run (when present).
        records_read: Registry records-read counter from latest run.
        records_loaded: Registry records-loaded counter from latest run.
        staging_rows_loaded: Count of staging rows loaded for latest run.
        canonical_rows_loaded: Count of canonical rows loaded for latest run.
        staging_table_row_counts: Staging counts per table.
        canonical_table_row_counts: Canonical counts per table.
        dq_error_fail_count: DQ fail count with severity `error`.
        dq_warning_fail_count: DQ fail count with severity `warning`.
        health_status: Consolidated health status for source.
        health_reason: Actionable reason for non-healthy statuses.
    """

    source_id: str
    source_kind: SourceKind
    source_uri: str
    source_display_name: Optional[str]
    source_is_active: bool
    latest_ingestion_id: Optional[int]
    latest_status: Optional[IngestionStatus]
    latest_started_at: Optional[datetime]
    latest_finished_at: Optional[datetime]
    latest_notes: Optional[str]
    latest_error_message: Optional[str]
    records_read: Optional[int]
    records_loaded: Optional[int]
    staging_rows_loaded: int
    canonical_rows_loaded: int
    staging_table_row_counts: dict[str, int]
    canonical_table_row_counts: dict[str, int]
    dq_error_fail_count: int
    dq_warning_fail_count: int
    health_status: SourceHealthStatus
    health_reason: Optional[str]


@dataclass(frozen=True)
class SourceHealthSummary:
    """Aggregate health summary for a source-health result set."""

    total_sources: int
    status_counts: dict[str, int]
    partial_sources: int
    failed_sources: int
    no_run_sources: int


@dataclass(frozen=True)
class _RowCountBundle:
    """Internal row-count bundle keyed by ingestion id."""

    staging_total: int
    canonical_total: int
    staging_by_table: dict[str, int]
    canonical_by_table: dict[str, int]


def _classify_table_domain(table_name: str) -> str | None:
    """Classify table into health count domain (`staging`/`canonical`)."""

    normalized = str(table_name or "").strip().lower()
    if not normalized:
        return None
    if normalized.startswith("stg_"):
        return "staging"
    if normalized in HEALTH_CANONICAL_TABLES:
        return "canonical"
    return None


def _collect_latest_run_details(
    session: Session,
    *,
    ingestion_ids: Iterable[int],
) -> dict[int, IngestionRun]:
    """Load latest ingestion runs by id into a dictionary."""

    ids = tuple(sorted({int(item) for item in ingestion_ids}))
    if not ids:
        return {}
    rows = session.exec(select(IngestionRun).where(IngestionRun.id.in_(ids))).all()
    return {int(row.id): row for row in rows if row.id is not None}


def _collect_row_counts_by_ingestion(
    session: Session,
    *,
    ingestion_ids: Iterable[int],
) -> dict[int, _RowCountBundle]:
    """Collect staging/canonical row counts by ingestion id.

    Args:
        session: Open database session.
        ingestion_ids: Ingestion ids used as scope.

    Returns:
        Mapping `ingestion_id -> row count bundle`.
    """

    ids = tuple(sorted({int(item) for item in ingestion_ids}))
    if not ids:
        return {}

    bind = session.get_bind()
    inspector = sa.inspect(bind)
    metadata = sa.MetaData()

    staging_totals: dict[int, int] = defaultdict(int)
    canonical_totals: dict[int, int] = defaultdict(int)
    staging_tables: dict[int, dict[str, int]] = defaultdict(dict)
    canonical_tables: dict[int, dict[str, int]] = defaultdict(dict)

    for table_name in sorted(inspector.get_table_names()):
        domain = _classify_table_domain(table_name)
        if domain is None:
            continue
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "ingestion_id" not in columns:
            continue

        table = sa.Table(table_name, metadata, autoload_with=bind)
        stmt = (
            select(
                table.c.ingestion_id.label("ingestion_id"),
                func.count().label("row_count"),
            )
            .select_from(table)
            .where(table.c.ingestion_id.in_(ids))
            .group_by(table.c.ingestion_id)
        )

        for ingestion_id, row_count in session.exec(stmt).all():
            if ingestion_id is None:
                continue
            ing_id = int(ingestion_id)
            count = int(row_count or 0)
            if count <= 0:
                continue
            if domain == "staging":
                staging_totals[ing_id] += count
                staging_tables[ing_id][table_name] = count
            else:
                canonical_totals[ing_id] += count
                canonical_tables[ing_id][table_name] = count

    bundles: dict[int, _RowCountBundle] = {}
    for ing_id in ids:
        bundles[ing_id] = _RowCountBundle(
            staging_total=int(staging_totals.get(ing_id, 0)),
            canonical_total=int(canonical_totals.get(ing_id, 0)),
            staging_by_table=dict(sorted(staging_tables.get(ing_id, {}).items())),
            canonical_by_table=dict(sorted(canonical_tables.get(ing_id, {}).items())),
        )
    return bundles


def _collect_dq_fail_counts(
    session: Session,
    *,
    ingestion_ids: Iterable[int],
) -> dict[int, tuple[int, int]]:
    """Collect DQ fail counts by ingestion id (`error_fail`, `warning_fail`)."""

    ids = tuple(sorted({int(item) for item in ingestion_ids}))
    if not ids:
        return {}

    bind = session.get_bind()
    inspector = sa.inspect(bind)
    if "dq_check_result" not in set(inspector.get_table_names()):
        return {}

    stmt = (
        select(
            DQCheckResult.ingestion_id,
            DQCheckResult.severity,
            func.count().label("finding_count"),
        )
        .where(
            DQCheckResult.ingestion_id.in_(ids),
            DQCheckResult.status == DQCheckStatus.FAIL,
        )
        .group_by(DQCheckResult.ingestion_id, DQCheckResult.severity)
    )
    counts: dict[int, dict[str, int]] = defaultdict(lambda: {"error": 0, "warning": 0})
    for ingestion_id, severity, finding_count in session.exec(stmt).all():
        if ingestion_id is None or severity is None:
            continue
        sev = str(severity.value if isinstance(severity, DQCheckSeverity) else severity).lower()
        if sev not in {"error", "warning"}:
            continue
        counts[int(ingestion_id)][sev] = int(finding_count or 0)

    return {
        ing_id: (int(values["error"]), int(values["warning"]))
        for ing_id, values in counts.items()
    }


def _resolve_health_status(
    *,
    latest_status: IngestionStatus | None,
    dq_error_fail_count: int,
    dq_warning_fail_count: int,
) -> SourceHealthStatus:
    """Resolve consolidated health status from ingestion + DQ context."""

    if latest_status is None:
        return SourceHealthStatus.NO_RUN
    if latest_status == IngestionStatus.FAILED:
        return SourceHealthStatus.FAILED
    if latest_status == IngestionStatus.PARTIAL:
        return SourceHealthStatus.PARTIAL
    if dq_error_fail_count > 0:
        return SourceHealthStatus.FAILED
    if dq_warning_fail_count > 0:
        return SourceHealthStatus.DEGRADED
    return SourceHealthStatus.HEALTHY


def _resolve_health_reason(
    *,
    health_status: SourceHealthStatus,
    latest_notes: str | None,
    latest_error_message: str | None,
    dq_error_fail_count: int,
    dq_warning_fail_count: int,
) -> str | None:
    """Resolve short actionable reason for source health status."""

    if health_status == SourceHealthStatus.NO_RUN:
        return "Sem ingestao registrada para a fonte."
    if health_status == SourceHealthStatus.FAILED:
        if latest_error_message:
            return latest_error_message
        if dq_error_fail_count > 0:
            return f"{dq_error_fail_count} falha(s) critica(s) de DQ."
        if latest_notes:
            return latest_notes
        return "Ultima ingestao em status failed."
    if health_status == SourceHealthStatus.PARTIAL:
        if latest_notes:
            return latest_notes
        return "Ultima ingestao em status partial."
    if health_status == SourceHealthStatus.DEGRADED:
        return f"{dq_warning_fail_count} warning(s) de DQ."
    return latest_notes or None


def list_source_health_status(
    session: Session,
    *,
    statuses: Iterable[IngestionStatus] | None = None,
    source_kinds: Iterable[SourceKind] | None = None,
) -> list[SourceHealthRow]:
    """List deterministic source-health rows with latest run and load counts.

    Args:
        session: Open database session.
        statuses: Optional filter by latest ingestion status.
        source_kinds: Optional filter by source kind.

    Returns:
        List of source-health rows ordered by `source_id`.
    """

    latest_rows = latest_ingestion_by_source(
        session,
        statuses=statuses,
        source_kinds=source_kinds,
    )
    latest_ingestion_ids = [
        int(row.latest_ingestion_id)
        for row in latest_rows
        if row.latest_ingestion_id is not None
    ]

    run_details = _collect_latest_run_details(session, ingestion_ids=latest_ingestion_ids)
    row_counts = _collect_row_counts_by_ingestion(session, ingestion_ids=latest_ingestion_ids)
    dq_fail_counts = _collect_dq_fail_counts(session, ingestion_ids=latest_ingestion_ids)

    output: list[SourceHealthRow] = []
    for row in latest_rows:
        latest_ingestion_id = int(row.latest_ingestion_id) if row.latest_ingestion_id is not None else None
        run = run_details.get(latest_ingestion_id) if latest_ingestion_id is not None else None
        counts = row_counts.get(latest_ingestion_id) if latest_ingestion_id is not None else None
        dq_error_fail_count, dq_warning_fail_count = (
            dq_fail_counts.get(latest_ingestion_id, (0, 0))
            if latest_ingestion_id is not None
            else (0, 0)
        )

        health_status = _resolve_health_status(
            latest_status=row.latest_status,
            dq_error_fail_count=dq_error_fail_count,
            dq_warning_fail_count=dq_warning_fail_count,
        )
        latest_notes = run.notes if run is not None else row.latest_notes
        latest_error_message = run.error_message if run is not None else None
        health_reason = _resolve_health_reason(
            health_status=health_status,
            latest_notes=latest_notes,
            latest_error_message=latest_error_message,
            dq_error_fail_count=dq_error_fail_count,
            dq_warning_fail_count=dq_warning_fail_count,
        )

        output.append(
            SourceHealthRow(
                source_id=row.source_id,
                source_kind=row.source_kind,
                source_uri=row.source_uri,
                source_display_name=row.source_display_name,
                source_is_active=row.source_is_active,
                latest_ingestion_id=latest_ingestion_id,
                latest_status=row.latest_status,
                latest_started_at=row.latest_started_at,
                latest_finished_at=row.latest_finished_at,
                latest_notes=latest_notes,
                latest_error_message=latest_error_message,
                records_read=(int(run.records_read) if run and run.records_read is not None else None),
                records_loaded=(int(run.records_loaded) if run and run.records_loaded is not None else None),
                staging_rows_loaded=int(counts.staging_total if counts else 0),
                canonical_rows_loaded=int(counts.canonical_total if counts else 0),
                staging_table_row_counts=dict(counts.staging_by_table if counts else {}),
                canonical_table_row_counts=dict(counts.canonical_by_table if counts else {}),
                dq_error_fail_count=int(dq_error_fail_count),
                dq_warning_fail_count=int(dq_warning_fail_count),
                health_status=health_status,
                health_reason=health_reason,
            )
        )

    return output


def summarize_source_health(rows: Iterable[SourceHealthRow]) -> SourceHealthSummary:
    """Aggregate source-health rows into status counters."""

    rows_list = list(rows)
    status_counts = Counter(row.health_status.value for row in rows_list)
    return SourceHealthSummary(
        total_sources=len(rows_list),
        status_counts=dict(status_counts),
        partial_sources=int(status_counts.get(SourceHealthStatus.PARTIAL.value, 0)),
        failed_sources=int(status_counts.get(SourceHealthStatus.FAILED.value, 0)),
        no_run_sources=int(status_counts.get(SourceHealthStatus.NO_RUN.value, 0)),
    )


def source_health_rows_to_dicts(rows: Iterable[SourceHealthRow]) -> list[dict[str, object]]:
    """Serialize source-health rows to JSON-friendly dictionaries."""

    payload: list[dict[str, object]] = []
    for row in rows:
        payload.append(
            {
                "source_id": row.source_id,
                "source_kind": row.source_kind.value,
                "source_uri": row.source_uri,
                "source_display_name": row.source_display_name,
                "source_is_active": row.source_is_active,
                "latest_ingestion_id": row.latest_ingestion_id,
                "latest_status": row.latest_status.value if row.latest_status else None,
                "latest_started_at": row.latest_started_at.isoformat() if row.latest_started_at else None,
                "latest_finished_at": row.latest_finished_at.isoformat() if row.latest_finished_at else None,
                "latest_notes": row.latest_notes,
                "latest_error_message": row.latest_error_message,
                "records_read": row.records_read,
                "records_loaded": row.records_loaded,
                "staging_rows_loaded": row.staging_rows_loaded,
                "canonical_rows_loaded": row.canonical_rows_loaded,
                "staging_table_row_counts": dict(row.staging_table_row_counts),
                "canonical_table_row_counts": dict(row.canonical_table_row_counts),
                "dq_error_fail_count": row.dq_error_fail_count,
                "dq_warning_fail_count": row.dq_warning_fail_count,
                "health_status": row.health_status.value,
                "health_reason": row.health_reason,
            }
        )
    return payload


def source_health_summary_to_dict(summary: SourceHealthSummary) -> dict[str, object]:
    """Serialize a source-health summary to a JSON-friendly dictionary.

    Args:
        summary: Aggregated source-health summary.

    Returns:
        Dictionary with deterministic health counters.
    """

    return {
        "total_sources": int(summary.total_sources),
        "status_counts": dict(summary.status_counts),
        "partial_sources": int(summary.partial_sources),
        "failed_sources": int(summary.failed_sources),
        "no_run_sources": int(summary.no_run_sources),
    }


def build_coverage_health_payload(
    session: Session,
    *,
    event_id: int | None = None,
) -> dict[str, object]:
    """Build a session coverage payload for internal health endpoints.

    Args:
        session: Open database session.
        event_id: Optional event scope filter.

    Returns:
        Coverage payload generated by `etl.validate.coverage_matrix`.

    Raises:
        ModuleNotFoundError: If coverage module cannot be imported after fallback.
    """

    from etl.validate.coverage_matrix import build_coverage_matrix_payload

    return build_coverage_matrix_payload(session, event_id=event_id)


def build_health_alerts(
    *,
    health_payload: Mapping[str, Any] | None,
    coverage_payload: Mapping[str, Any] | None,
) -> list[dict[str, object]]:
    """Build serialized observability alerts from health and coverage payloads.

    Args:
        health_payload: Source-health payload.
        coverage_payload: Session coverage payload.

    Returns:
        Serialized alerts as dictionaries.

    Raises:
        ModuleNotFoundError: If alert module cannot be imported after fallback.
    """

    from etl.validate.alerts import alerts_to_dicts, generate_alerts

    return alerts_to_dicts(generate_alerts(health_payload, coverage_payload))
