"""Operational catalog queries for ETL source/ingestion audit.

This module exposes read-only query helpers used by API/CLI layers to answer:
- what sources exist
- what was the latest ingestion run per source
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func
from sqlmodel import Session, select

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind


@dataclass(frozen=True)
class LatestIngestionBySourceRow:
    """Stable output contract for latest-ingestion catalog query.

    Attributes:
        source_id: Stable source identifier.
        source_kind: Source type (pdf/xlsx/pptx/etc.).
        source_uri: Source URI/path.
        source_display_name: Optional source display name.
        source_is_active: Source active flag.
        latest_ingestion_id: Latest run ID for this source (None when no runs).
        latest_status: Latest run status (None when no runs).
        latest_started_at: Latest run start timestamp (None when no runs).
        latest_finished_at: Latest run finish timestamp (None when no runs).
        latest_extractor_name: Extractor/loader name of latest run.
        latest_notes: Operational notes of latest run.
        latest_created_at: Latest run creation timestamp.
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
    latest_extractor_name: Optional[str]
    latest_notes: Optional[str]
    latest_created_at: Optional[datetime]


@dataclass(frozen=True)
class CatalogSummary:
    """Aggregate counters for operational catalog reporting.

    Attributes:
        total_sources: Number of source rows in the result set.
        sources_with_ingestion: Sources with at least one ingestion run.
        sources_without_ingestion: Sources without ingestion history.
        latest_status_counts: Latest-run status counts keyed by status value.
    """

    total_sources: int
    sources_with_ingestion: int
    sources_without_ingestion: int
    latest_status_counts: dict[str, int]


@dataclass(frozen=True)
class IngestionCatalogRow:
    """Stable output contract for ingestion-run catalog queries.

    Attributes:
        ingestion_id: Ingestion run primary key.
        source_id: Stable source identifier linked to the run.
        source_kind: Source type (pdf/xlsx/pptx/etc.).
        source_uri: Source URI/path.
        source_display_name: Optional source display name.
        source_is_active: Source active flag.
        status: Ingestion status value.
        started_at: Run start timestamp.
        finished_at: Run finish timestamp.
        extractor_name: Extractor/loader name for the run.
        notes: Optional notes persisted for the run.
        created_at: Run creation timestamp.
    """

    ingestion_id: int
    source_id: str
    source_kind: SourceKind
    source_uri: str
    source_display_name: Optional[str]
    source_is_active: bool
    status: IngestionStatus
    started_at: datetime
    finished_at: Optional[datetime]
    extractor_name: Optional[str]
    notes: Optional[str]
    created_at: datetime


def latest_ingestion_by_source(
    session: Session,
    *,
    statuses: Iterable[IngestionStatus] | None = None,
    source_kinds: Iterable[SourceKind] | None = None,
) -> list[LatestIngestionBySourceRow]:
    """Return latest ingestion run per source, with deterministic tie-break.

    Ordering and tie-break rules:
    1. For each source, latest run is chosen by `started_at` descending.
    2. If two runs have same `started_at`, higher `id` wins.
    3. Output list is ordered by `source_id` ascending.

    The query includes sources with no runs when `statuses` filter is not used.
    When `statuses` is provided, only sources whose latest status is in the
    requested domain are returned.

    Args:
        session: Open database session.
        statuses: Optional status domain filter for latest runs.
        source_kinds: Optional source kind filter.

    Returns:
        One row per source with latest ingestion metadata.
    """
    status_filter = tuple(dict.fromkeys(statuses or ()))
    source_kind_filter = tuple(dict.fromkeys(source_kinds or ()))

    ranked_runs = (
        select(
            IngestionRun.id.label("ingestion_id"),
            IngestionRun.source_pk.label("source_pk"),
            IngestionRun.status.label("status"),
            IngestionRun.started_at.label("started_at"),
            IngestionRun.finished_at.label("finished_at"),
            IngestionRun.extractor_name.label("extractor_name"),
            IngestionRun.notes.label("notes"),
            IngestionRun.created_at.label("created_at"),
            func.row_number()
            .over(
                partition_by=IngestionRun.source_pk,
                order_by=(IngestionRun.started_at.desc(), IngestionRun.id.desc()),
            )
            .label("run_rank"),
        )
        .subquery("ranked_ingestion_runs")
    )

    stmt = (
        select(
            Source.source_id,
            Source.kind,
            Source.uri,
            Source.display_name,
            Source.is_active,
            ranked_runs.c.ingestion_id,
            ranked_runs.c.status,
            ranked_runs.c.started_at,
            ranked_runs.c.finished_at,
            ranked_runs.c.extractor_name,
            ranked_runs.c.notes,
            ranked_runs.c.created_at,
        )
        .outerjoin(
            ranked_runs,
            and_(
                ranked_runs.c.source_pk == Source.id,
                ranked_runs.c.run_rank == 1,
            ),
        )
        .order_by(Source.source_id.asc())
    )
    if source_kind_filter:
        stmt = stmt.where(Source.kind.in_(source_kind_filter))
    if status_filter:
        stmt = stmt.where(ranked_runs.c.status.in_(status_filter))

    rows = session.exec(stmt).all()
    results: list[LatestIngestionBySourceRow] = []
    for (
        source_id,
        source_kind,
        source_uri,
        source_display_name,
        source_is_active,
        latest_ingestion_id,
        latest_status,
        latest_started_at,
        latest_finished_at,
        latest_extractor_name,
        latest_notes,
        latest_created_at,
    ) in rows:
        results.append(
            LatestIngestionBySourceRow(
                source_id=source_id,
                source_kind=source_kind,
                source_uri=source_uri,
                source_display_name=source_display_name,
                source_is_active=source_is_active,
                latest_ingestion_id=latest_ingestion_id,
                latest_status=latest_status,
                latest_started_at=latest_started_at,
                latest_finished_at=latest_finished_at,
                latest_extractor_name=latest_extractor_name,
                latest_notes=latest_notes,
                latest_created_at=latest_created_at,
            )
        )
    return results


def summarize_latest_ingestion_rows(rows: Iterable[LatestIngestionBySourceRow]) -> CatalogSummary:
    """Build summary counters from latest-ingestion rows.

    Args:
        rows: Rows returned by `latest_ingestion_by_source`.

    Returns:
        Catalog summary with total, ingestion coverage and status counters.
    """

    rows_list = list(rows)
    with_ingestion = 0
    status_counter: Counter[str] = Counter()
    for row in rows_list:
        if row.latest_ingestion_id is None:
            continue
        with_ingestion += 1
        if row.latest_status is not None:
            status_counter[row.latest_status.value] += 1

    total_sources = len(rows_list)
    return CatalogSummary(
        total_sources=total_sources,
        sources_with_ingestion=with_ingestion,
        sources_without_ingestion=total_sources - with_ingestion,
        latest_status_counts=dict(status_counter),
    )


def list_ingestion_runs(
    session: Session,
    *,
    statuses: Iterable[IngestionStatus] | None = None,
    source_kinds: Iterable[SourceKind] | None = None,
    source_ids: Iterable[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[IngestionCatalogRow]:
    """List ingestion runs with optional status/source filters.

    Ordering rule:
    1. `started_at` descending.
    2. `id` descending as deterministic tie-break.

    Args:
        session: Open database session.
        statuses: Optional status domain filter.
        source_kinds: Optional source kind filter.
        source_ids: Optional source ID filter.
        limit: Max rows to return.
        offset: Offset for pagination.

    Returns:
        Ingestion run rows enriched with source metadata.
    """

    status_filter = tuple(dict.fromkeys(statuses or ()))
    source_kind_filter = tuple(dict.fromkeys(source_kinds or ()))
    source_id_filter = tuple(dict.fromkeys(source_ids or ()))

    stmt = (
        select(
            IngestionRun.id,
            Source.source_id,
            Source.kind,
            Source.uri,
            Source.display_name,
            Source.is_active,
            IngestionRun.status,
            IngestionRun.started_at,
            IngestionRun.finished_at,
            IngestionRun.extractor_name,
            IngestionRun.notes,
            IngestionRun.created_at,
        )
        .join(Source, Source.id == IngestionRun.source_pk)
        .order_by(IngestionRun.started_at.desc(), IngestionRun.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if status_filter:
        stmt = stmt.where(IngestionRun.status.in_(status_filter))
    if source_kind_filter:
        stmt = stmt.where(Source.kind.in_(source_kind_filter))
    if source_id_filter:
        stmt = stmt.where(Source.source_id.in_(source_id_filter))

    rows = session.exec(stmt).all()
    return [
        IngestionCatalogRow(
            ingestion_id=ingestion_id,
            source_id=source_id,
            source_kind=source_kind,
            source_uri=source_uri,
            source_display_name=source_display_name,
            source_is_active=source_is_active,
            status=status_value,
            started_at=started_at,
            finished_at=finished_at,
            extractor_name=extractor_name,
            notes=notes,
            created_at=created_at,
        )
        for (
            ingestion_id,
            source_id,
            source_kind,
            source_uri,
            source_display_name,
            source_is_active,
            status_value,
            started_at,
            finished_at,
            extractor_name,
            notes,
            created_at,
        ) in rows
    ]
