"""Persistence helpers for cross-source inconsistencies in the core."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Mapping, Sequence

import sqlalchemy as sa

from ._contracts import Severity
from ._db_protocols import SessionLike


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_positive_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def persist_cross_source_inconsistencies(session: SessionLike, *, ingestion_id: int | None, check_id: str, severity: Severity, findings: Sequence[Mapping[str, Any]], replace_existing: bool = True) -> int:
    """Persist cross-source inconsistencies using SQLAlchemy Core only."""

    if ingestion_id is None:
        return 0

    table = sa.Table(
        "dq_inconsistency",
        sa.MetaData(),
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("check_id", sa.String(length=220), nullable=False),
        sa.Column("dataset_id", sa.String(length=120), nullable=False),
        sa.Column("metric_key", sa.String(length=220), nullable=False),
        sa.Column("unit", sa.String(length=40)),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("values_json", sa.Text(), nullable=False),
        sa.Column("sources_json", sa.Text(), nullable=False),
        sa.Column("lineage_refs_json", sa.Text()),
        sa.Column("evidence_json", sa.Text()),
        sa.Column("suggested_action", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    persisted_count = 0
    with session.get_bind().begin() as conn:
        if replace_existing:
            conn.execute(
                sa.delete(table).where(
                    table.c.ingestion_id == int(ingestion_id),
                    table.c.check_id == check_id,
                )
            )
        for finding in findings:
            source_values = list(finding.get("source_values", []))
            source_ids = sorted({str(item.get("source_id")).strip() for item in source_values if item.get("source_id")})
            lineage_ids = sorted({int(item) for source_item in source_values for item in (source_item.get("lineage_ref_ids") or []) if _parse_positive_int(item) is not None})
            conn.execute(
                sa.insert(table).values(
                    ingestion_id=int(ingestion_id),
                    check_id=check_id,
                    dataset_id=str(finding.get("dataset_id") or "").strip(),
                    metric_key=str(finding.get("metric_key") or "").strip(),
                    unit=_normalize_optional_text(finding.get("unit")),
                    status="inconsistente",
                    severity=severity.value,
                    values_json=json.dumps(source_values, ensure_ascii=False, sort_keys=True),
                    sources_json=json.dumps(source_ids, ensure_ascii=False, sort_keys=True),
                    lineage_refs_json=json.dumps(lineage_ids, ensure_ascii=False, sort_keys=True) if lineage_ids else None,
                    evidence_json=json.dumps(finding, ensure_ascii=False, sort_keys=True),
                    suggested_action=str(finding.get("suggested_action") or "").strip() or "Revisar divergencia entre fontes e aplicar regra de precedencia.",
                    created_at=_now_utc(),
                )
            )
            persisted_count += 1
    return persisted_count

