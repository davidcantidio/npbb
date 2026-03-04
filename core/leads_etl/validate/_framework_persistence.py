"""Persistence helpers for core lead ETL validation results."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Mapping, Sequence

import sqlalchemy as sa

from ._contracts import CheckResult
from ._db_protocols import SessionLike


def _resolve_source_id(result: CheckResult, default_source_id: str | None) -> str | None:
    """Resolve best source identifier from lineage payload or fallback value."""

    lineage_source = result.lineage.get("source_id")
    if isinstance(lineage_source, str) and lineage_source.strip():
        return lineage_source.strip()

    if isinstance(default_source_id, str) and default_source_id.strip():
        return default_source_id.strip()
    return None


def _resolve_lineage_ref_id(lineage_payload: Mapping[str, Any]) -> int | None:
    """Extract optional lineage reference identifier from payload."""

    raw_value = lineage_payload.get("lineage_ref_id")
    if raw_value is None:
        raw_value = lineage_payload.get("lineage_id")
    try:
        if raw_value is None:
            return None
        parsed = int(raw_value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _now_utc() -> datetime:
    """Return UTC timestamp for persistence rows."""

    return datetime.now(timezone.utc)


def _dq_results_table(metadata: sa.MetaData) -> sa.Table:
    """Return lightweight reflected definition for `dq_check_result`."""

    return sa.Table(
        "dq_check_result",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(length=160)),
        sa.Column("lineage_ref_id", sa.Integer()),
        sa.Column("check_id", sa.String(length=200), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def persist_check_results(
    session: SessionLike,
    *,
    ingestion_id: int | None,
    results: Sequence[CheckResult],
    replace_existing: bool = True,
    default_source_id: str | None = None,
) -> int:
    """Persist DQ check results using SQLAlchemy Core only."""

    if ingestion_id is None:
        return 0

    table = _dq_results_table(sa.MetaData())
    persisted_count = 0
    with session.get_bind().begin() as conn:
        if replace_existing:
            conn.execute(
                sa.delete(table).where(table.c.ingestion_id == int(ingestion_id))
            )

        for result in results:
            row_ingestion_id = result.ingestion_id if result.ingestion_id is not None else ingestion_id
            if row_ingestion_id is None:
                continue
            conn.execute(
                sa.insert(table).values(
                    ingestion_id=int(row_ingestion_id),
                    source_id=_resolve_source_id(result, default_source_id=default_source_id),
                    lineage_ref_id=_resolve_lineage_ref_id(result.lineage),
                    check_id=result.check_id,
                    severity=result.severity.value,
                    status=result.status.value,
                    message=result.message,
                    details_json=json.dumps(
                        {"evidence": result.evidence, "lineage": result.lineage},
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    created_at=_now_utc(),
                )
            )
            persisted_count += 1
    return persisted_count

