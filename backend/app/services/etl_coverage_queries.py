"""Session coverage queries (expected vs observed) for operational audit.

This module provides a base matrix for TMJ session coverage by dataset.
It uses two observation layers:
- primary: staging tables with resolved `session_id`,
- fallback: latest ingestions grouped by source with source-id inference.

This strategy allows coverage reports to:
- reflect real staging coverage per session when available,
- still return actionable statuses when staging is not populated yet.

Lightweight fallback rules:
- expected sessions come from `event_sessions`,
- observed datasets come from latest ingestions grouped by source,
- session and dataset mapping is inferred from source tags (source_id/uri/extractor).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
import re
from typing import Any

from sqlalchemy import inspect
from sqlmodel import Session, select

from app.models.etl_registry import CoverageDataset, CoverageStatus, IngestionStatus
from app.models.models import EventSession, EventSessionType
from app.models.stg_access_control import StgAccessControlSession
from app.models.stg_leads import StgLead
from app.models.stg_optin import StgOptinTransaction
from app.services.etl_catalog_queries import (
    LatestIngestionBySourceRow,
    latest_ingestion_by_source,
)
from app.services.tmj_sessions import (
    infer_session_type_from_source_id,
    tmj2025_date_from_source_id,
    tmj2025_session_key,
)


DEFAULT_COVERAGE_DATASETS: tuple[CoverageDataset, ...] = (
    CoverageDataset.ACCESS_CONTROL,
    CoverageDataset.TICKET_SALES,
    CoverageDataset.OPTIN,
    CoverageDataset.LEADS,
)

_DATASET_RULES: tuple[tuple[CoverageDataset, tuple[str, ...]], ...] = (
    (
        CoverageDataset.ACCESS_CONTROL,
        (
            "ACESSO",
            "ACCESS",
            "CATRACA",
            "TURNSTILE",
        ),
    ),
    (
        CoverageDataset.TICKET_SALES,
        (
            "VENDA",
            "VENDAS",
            "SALE",
            "SALES",
            "SOLD",
        ),
    ),
    (
        CoverageDataset.OPTIN,
        (
            "OPTIN",
            "OPT_IN",
        ),
    ),
    (
        CoverageDataset.LEADS,
        (
            "LEAD",
            "LEADS",
        ),
    ),
)


_STAGING_DATASET_MODELS: tuple[tuple[CoverageDataset, type[Any]], ...] = (
    (CoverageDataset.ACCESS_CONTROL, StgAccessControlSession),
    (CoverageDataset.OPTIN, StgOptinTransaction),
    (CoverageDataset.LEADS, StgLead),
)


@dataclass(frozen=True)
class SessionCoverageRow:
    """Output contract for one session x dataset coverage item.

    Attributes:
        session_id: Event session identifier.
        session_key: Stable session key.
        session_date: Session date.
        session_type: Session type.
        dataset: Dataset tag expected for the session.
        status: Coverage status for this session+dataset cell.
        sources_present: Source IDs observed for this cell.
        ingestion_ids: Latest ingestion IDs observed for this cell.
        latest_statuses: Latest ingestion statuses observed for this cell.
    """

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    dataset: CoverageDataset
    status: CoverageStatus
    sources_present: list[str]
    ingestion_ids: list[int]
    latest_statuses: list[IngestionStatus]


@dataclass(frozen=True)
class SessionCoverageSummaryRow:
    """Output contract for one session-level coverage summary row.

    Attributes:
        session_id: Event session identifier.
        session_key: Stable session key.
        session_date: Session date.
        session_type: Session type.
        status: Session status (`ok` when all required datasets are observed).
        observed_datasets: Datasets observed for the session.
        missing_datasets: Datasets missing/failing for the session.
    """

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    status: str
    observed_datasets: list[CoverageDataset]
    missing_datasets: list[CoverageDataset]


@dataclass(frozen=True)
class SessionDatasetSourceCandidate:
    """Fallback source candidate considered for one session x dataset cell.

    This contract is intentionally explicit so downstream evaluators can explain
    why a dataset is marked as gap/partial and which sources were considered.

    Attributes:
        session_id: Event session identifier.
        session_key: Stable session key.
        session_date: Session date.
        session_type: Session type.
        dataset: Dataset inferred for the source.
        source_id: Candidate source identifier.
        source_uri: Source URI/path for traceability.
        latest_ingestion_id: Latest run id for the candidate source.
        latest_status: Latest run status for the candidate source.
        latest_extractor_name: Extractor name for the latest run.
        match_scope: Match strategy used (`session_key` or `day_type`).
    """

    session_id: int
    session_key: str
    session_date: date
    session_type: EventSessionType
    dataset: CoverageDataset
    source_id: str
    source_uri: str
    latest_ingestion_id: int | None
    latest_status: IngestionStatus | None
    latest_extractor_name: str | None
    match_scope: str


def infer_coverage_dataset(
    *,
    source_id: str,
    extractor_name: str | None = None,
    source_uri: str | None = None,
) -> CoverageDataset:
    """Infer dataset tag from source metadata using simple keyword rules.

    Args:
        source_id: Stable source identifier.
        extractor_name: Optional extractor name of latest run.
        source_uri: Optional source URI/path.

    Returns:
        Inferred dataset tag from lightweight keyword matching.
    """

    tokens = " ".join(
        part for part in ((source_id or ""), (extractor_name or ""), (source_uri or "")) if part
    ).upper()
    tokens = re.sub(r"[^A-Z0-9_]+", " ", tokens)

    for dataset, keywords in _DATASET_RULES:
        if any(keyword in tokens for keyword in keywords):
            return dataset
    return CoverageDataset.OTHER


def infer_session_key_from_source_id(source_id: str) -> str | None:
    """Infer TMJ session key from a source identifier.

    Args:
        source_id: Stable source identifier.

    Returns:
        Session key when day and session type can be inferred; otherwise `None`.
    """

    session_date = tmj2025_date_from_source_id(source_id)
    if session_date is None:
        return None
    session_type = infer_session_type_from_source_id(source_id)
    return tmj2025_session_key(session_date, session_type)


def _resolve_coverage_status(
    matches: list[LatestIngestionBySourceRow],
) -> CoverageStatus:
    """Resolve coverage status from latest-ingestion matches.

    Args:
        matches: Latest source rows mapped to one session+dataset cell.

    Returns:
        Coverage status for the cell.
    """

    if not matches:
        return CoverageStatus.MISSING

    statuses = [row.latest_status for row in matches if row.latest_status is not None]
    if not statuses:
        return CoverageStatus.UNKNOWN
    if any(st == IngestionStatus.SUCCESS for st in statuses):
        return CoverageStatus.OBSERVED
    if any(st == IngestionStatus.PARTIAL for st in statuses):
        return CoverageStatus.OBSERVED_PARTIAL
    if all(st == IngestionStatus.FAILED for st in statuses):
        return CoverageStatus.INGESTION_FAILED
    return CoverageStatus.UNKNOWN


def _table_exists(session: Session, table_name: str) -> bool:
    """Return whether a table exists in the current database bind."""

    bind = session.get_bind()
    if bind is None:
        return False
    return bool(inspect(bind).has_table(table_name))


def _collect_staging_session_dataset_sources(
    session: Session,
    *,
    event_id: int | None = None,
) -> tuple[
    dict[tuple[int, CoverageDataset], set[str]],
    dict[CoverageDataset, int],
    set[CoverageDataset],
]:
    """Collect observed datasets from staging tables by `session_id`.

    Args:
        session: Open database session.
        event_id: Optional event filter when staging model provides `event_id`.

    Returns:
        Tuple containing:
        - mapping `(session_id, dataset) -> {source_id,...}`
        - unresolved counts per dataset (rows/sources without `session_id`)
        - datasets that have a staging table available in the current DB
    """

    by_cell: dict[tuple[int, CoverageDataset], set[str]] = defaultdict(set)
    unresolved_counts: dict[CoverageDataset, int] = defaultdict(int)
    datasets_with_staging: set[CoverageDataset] = set()

    for dataset, model in _STAGING_DATASET_MODELS:
        table_name = getattr(model, "__tablename__", "")
        if not table_name or not _table_exists(session, table_name):
            continue

        if not hasattr(model, "source_id"):
            continue

        has_session_id = hasattr(model, "session_id")
        has_event_id = hasattr(model, "event_id")
        if has_session_id:
            datasets_with_staging.add(dataset)

        if has_session_id:
            stmt = select(model.session_id, model.source_id).distinct()
            if event_id is not None and has_event_id:
                stmt = stmt.where(model.event_id == event_id)
            rows = session.exec(stmt).all()
            for session_id, source_id in rows:
                src = str(source_id or "").strip().upper()
                if not src:
                    continue
                if session_id is None:
                    unresolved_counts[dataset] += 1
                    continue
                by_cell[(int(session_id), dataset)].add(src)
            continue

        # Staging model has no explicit session_id (count as unresolved by source).
        src_rows = session.exec(select(model.source_id).distinct()).all()
        for source_id in src_rows:
            src = str(source_id or "").strip().upper()
            if src:
                unresolved_counts[dataset] += 1

    return by_cell, unresolved_counts, datasets_with_staging


def unresolved_staging_records_by_dataset(
    session: Session,
    *,
    event_id: int | None = None,
    expected_datasets: Iterable[CoverageDataset] | None = None,
) -> dict[CoverageDataset, int]:
    """Return unresolved staging counts by dataset.

    Args:
        session: Open database session.
        event_id: Optional event filter used where available.
        expected_datasets: Optional dataset domain to prefill zero-values.

    Returns:
        Mapping from dataset to unresolved counts (`session_id` not resolved).
    """

    _, unresolved, _ = _collect_staging_session_dataset_sources(session, event_id=event_id)
    datasets = tuple(dict.fromkeys(expected_datasets or DEFAULT_COVERAGE_DATASETS))
    out = {dataset: 0 for dataset in datasets}
    for dataset, count in unresolved.items():
        out[dataset] = int(count)
    return out


def build_session_dataset_source_candidates(
    session: Session,
    *,
    event_id: int | None = None,
    expected_datasets: Iterable[CoverageDataset] | None = None,
    latest_rows: Iterable[LatestIngestionBySourceRow] | None = None,
) -> list[SessionDatasetSourceCandidate]:
    """List fallback source candidates for each expected session x dataset cell.

    Matching strategy mirrors the fallback logic used by
    `build_session_coverage_matrix`:
    - direct match by inferred `session_key`;
    - fallback by `(session_date, session_type)`.

    Args:
        session: Open database session.
        event_id: Optional event filter for expected sessions.
        expected_datasets: Optional dataset domain.
        latest_rows: Optional latest-source rows for deterministic tests.

    Returns:
        Deterministically ordered candidate rows.
    """

    datasets = tuple(dict.fromkeys(expected_datasets or DEFAULT_COVERAGE_DATASETS))
    stmt_sessions = select(EventSession)
    if event_id is not None:
        stmt_sessions = stmt_sessions.where(EventSession.event_id == event_id)
    stmt_sessions = stmt_sessions.order_by(
        EventSession.session_date,
        EventSession.session_type,
        EventSession.session_key,
    )
    sessions = session.exec(stmt_sessions).all()

    sources = list(latest_rows) if latest_rows is not None else latest_ingestion_by_source(session)
    by_session_dataset: dict[tuple[str, CoverageDataset], list[LatestIngestionBySourceRow]] = (
        defaultdict(list)
    )
    by_day_type_dataset: dict[
        tuple[date, EventSessionType, CoverageDataset],
        list[LatestIngestionBySourceRow],
    ] = defaultdict(list)

    for row in sources:
        dataset = infer_coverage_dataset(
            source_id=row.source_id,
            extractor_name=row.latest_extractor_name,
            source_uri=row.source_uri,
        )
        session_key = infer_session_key_from_source_id(row.source_id)
        if session_key:
            by_session_dataset[(session_key, dataset)].append(row)

        session_date = tmj2025_date_from_source_id(row.source_id)
        if session_date is not None:
            session_type = infer_session_type_from_source_id(row.source_id)
            by_day_type_dataset[(session_date, session_type, dataset)].append(row)

    output: list[SessionDatasetSourceCandidate] = []
    for sess in sessions:
        session_id = int(sess.id)
        for dataset in datasets:
            seen_source_ids: set[str] = set()
            direct_matches = by_session_dataset.get((sess.session_key, dataset), [])
            for row in direct_matches:
                sid = str(row.source_id)
                if sid in seen_source_ids:
                    continue
                seen_source_ids.add(sid)
                output.append(
                    SessionDatasetSourceCandidate(
                        session_id=session_id,
                        session_key=sess.session_key,
                        session_date=sess.session_date,
                        session_type=sess.session_type,
                        dataset=dataset,
                        source_id=sid,
                        source_uri=row.source_uri,
                        latest_ingestion_id=(
                            int(row.latest_ingestion_id)
                            if row.latest_ingestion_id is not None
                            else None
                        ),
                        latest_status=row.latest_status,
                        latest_extractor_name=row.latest_extractor_name,
                        match_scope="session_key",
                    )
                )

            day_matches = by_day_type_dataset.get((sess.session_date, sess.session_type, dataset), [])
            for row in day_matches:
                sid = str(row.source_id)
                if sid in seen_source_ids:
                    continue
                seen_source_ids.add(sid)
                output.append(
                    SessionDatasetSourceCandidate(
                        session_id=session_id,
                        session_key=sess.session_key,
                        session_date=sess.session_date,
                        session_type=sess.session_type,
                        dataset=dataset,
                        source_id=sid,
                        source_uri=row.source_uri,
                        latest_ingestion_id=(
                            int(row.latest_ingestion_id)
                            if row.latest_ingestion_id is not None
                            else None
                        ),
                        latest_status=row.latest_status,
                        latest_extractor_name=row.latest_extractor_name,
                        match_scope="day_type",
                    )
                )

    return sorted(
        output,
        key=lambda item: (
            item.session_date,
            item.session_type.value,
            item.session_key,
            item.dataset.value,
            item.source_id,
            item.match_scope,
        ),
    )


def build_session_coverage_matrix(
    session: Session,
    *,
    event_id: int | None = None,
    expected_datasets: Iterable[CoverageDataset] | None = None,
    latest_rows: Iterable[LatestIngestionBySourceRow] | None = None,
) -> list[SessionCoverageRow]:
    """Build session coverage matrix crossing expected sessions and observed sources.

    Args:
        session: Open database session.
        event_id: Optional event filter for expected sessions.
        expected_datasets: Datasets expected for each session row.
        latest_rows: Optional latest-source rows (injected by caller/tests).

    Returns:
        Coverage matrix rows consumable by data-quality and report layers.
    """

    datasets = tuple(dict.fromkeys(expected_datasets or DEFAULT_COVERAGE_DATASETS))
    stmt_sessions = select(EventSession)
    if event_id is not None:
        stmt_sessions = stmt_sessions.where(EventSession.event_id == event_id)
    stmt_sessions = stmt_sessions.order_by(
        EventSession.session_date,
        EventSession.session_type,
        EventSession.session_key,
    )
    sessions = session.exec(stmt_sessions).all()

    sources = list(latest_rows) if latest_rows is not None else latest_ingestion_by_source(session)
    latest_by_source = {row.source_id.upper(): row for row in sources}
    by_session_dataset: dict[tuple[str, CoverageDataset], list[LatestIngestionBySourceRow]] = (
        defaultdict(list)
    )
    by_day_type_dataset: dict[
        tuple[date, EventSessionType, CoverageDataset],
        list[LatestIngestionBySourceRow],
    ] = defaultdict(list)
    for row in sources:
        dataset = infer_coverage_dataset(
            source_id=row.source_id,
            extractor_name=row.latest_extractor_name,
            source_uri=row.source_uri,
        )
        session_key = infer_session_key_from_source_id(row.source_id)
        if session_key:
            by_session_dataset[(session_key, dataset)].append(row)

        session_date = tmj2025_date_from_source_id(row.source_id)
        if session_date is not None:
            session_type = infer_session_type_from_source_id(row.source_id)
            by_day_type_dataset[(session_date, session_type, dataset)].append(row)

    staging_by_cell, _, datasets_with_staging = _collect_staging_session_dataset_sources(
        session,
        event_id=event_id,
    )

    results: list[SessionCoverageRow] = []
    for sess in sessions:
        session_id = int(sess.id)
        for dataset in datasets:
            fallback_matches = list(by_session_dataset.get((sess.session_key, dataset), []))
            fallback_matches.extend(
                by_day_type_dataset.get((sess.session_date, sess.session_type, dataset), [])
            )
            fallback_matches = list({item.source_id: item for item in fallback_matches}.values())
            staging_sources = staging_by_cell.get((session_id, dataset), set())

            staging_matches = [
                latest_by_source[source_id]
                for source_id in sorted(staging_sources)
                if source_id in latest_by_source
            ]
            if dataset in datasets_with_staging:
                matches = list({row.source_id: row for row in staging_matches}.values())
                status = CoverageStatus.OBSERVED if staging_sources else CoverageStatus.MISSING
                sources_present = sorted(staging_sources)
            else:
                merged_by_source = {
                    row.source_id: row
                    for row in (*fallback_matches, *staging_matches)
                }
                matches = list(merged_by_source.values())
                if staging_sources:
                    status = CoverageStatus.OBSERVED
                else:
                    status = _resolve_coverage_status(matches)
                sources_present = (
                    sorted(staging_sources)
                    if staging_sources
                    else sorted({row.source_id for row in matches})
                )
            results.append(
                SessionCoverageRow(
                    session_id=session_id,
                    session_key=sess.session_key,
                    session_date=sess.session_date,
                    session_type=sess.session_type,
                    dataset=dataset,
                    status=status,
                    sources_present=sources_present,
                    ingestion_ids=sorted(
                        {
                            int(row.latest_ingestion_id)
                            for row in matches
                            if row.latest_ingestion_id is not None
                        }
                    ),
                    latest_statuses=sorted(
                        {row.latest_status for row in matches if row.latest_status is not None},
                        key=lambda st: st.value,
                    ),
                )
            )
    return results


def build_session_coverage_summary(
    rows: Iterable[SessionCoverageRow],
) -> list[SessionCoverageSummaryRow]:
    """Aggregate matrix rows into one summary row per session.

    Args:
        rows: Coverage rows produced by `build_session_coverage_matrix`.

    Returns:
        Session-level summary rows with `ok`/`gap` and missing datasets list.
    """

    grouped: dict[int, list[SessionCoverageRow]] = defaultdict(list)
    for row in rows:
        grouped[row.session_id].append(row)

    summaries: list[SessionCoverageSummaryRow] = []
    for session_id, session_rows in grouped.items():
        first = session_rows[0]
        observed = sorted(
            {
                item.dataset
                for item in session_rows
                if item.status in (CoverageStatus.OBSERVED, CoverageStatus.OBSERVED_PARTIAL)
            },
            key=lambda dataset: dataset.value,
        )
        missing = sorted(
            {
                item.dataset
                for item in session_rows
                if item.status not in (CoverageStatus.OBSERVED, CoverageStatus.OBSERVED_PARTIAL)
            },
            key=lambda dataset: dataset.value,
        )
        summaries.append(
            SessionCoverageSummaryRow(
                session_id=session_id,
                session_key=first.session_key,
                session_date=first.session_date,
                session_type=first.session_type,
                status="ok" if not missing else "gap",
                observed_datasets=observed,
                missing_datasets=missing,
            )
        )

    return sorted(
        summaries,
        key=lambda row: (row.session_date, row.session_type.value, row.session_key),
    )


def coverage_rows_to_dicts(rows: Iterable[SessionCoverageRow]) -> list[dict[str, Any]]:
    """Serialize coverage rows into dictionaries for API/report consumers.

    Args:
        rows: Coverage rows produced by `build_session_coverage_matrix`.

    Returns:
        JSON-friendly list of dictionaries.
    """

    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append(
            {
                "session_id": row.session_id,
                "session_key": row.session_key,
                "session_date": row.session_date.isoformat(),
                "session_type": row.session_type.value,
                "dataset": row.dataset.value,
                "status": row.status.value,
                "sources_present": list(row.sources_present),
                "ingestion_ids": list(row.ingestion_ids),
                "latest_statuses": [status.value for status in row.latest_statuses],
            }
        )
    return payload


def coverage_summary_rows_to_dicts(
    rows: Iterable[SessionCoverageSummaryRow],
) -> list[dict[str, Any]]:
    """Serialize session summary rows into dictionaries.

    Args:
        rows: Rows returned by `build_session_coverage_summary`.

    Returns:
        JSON-friendly list of session summary dictionaries.
    """

    payload: list[dict[str, Any]] = []
    for row in rows:
        payload.append(
            {
                "session_id": row.session_id,
                "session_key": row.session_key,
                "session_date": row.session_date.isoformat(),
                "session_type": row.session_type.value,
                "status": row.status,
                "observed_datasets": [item.value for item in row.observed_datasets],
                "missing_datasets": [item.value for item in row.missing_datasets],
            }
        )
    return payload
