"""Unit tests for cross-source inconsistency data-quality checks."""

from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import sys

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from etl.validate.checks_cross_source import (
    CrossSourceDatasetSpec,
    CrossSourceInconsistencyCheck,
)
from etl.validate.framework import CheckContext, CheckStatus, Severity

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.dq_inconsistency import DQInconsistency  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for cross-source tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_base_tables(engine) -> None:  # noqa: ANN001
    """Create minimal backend tables required by inconsistency persistence."""

    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            DQInconsistency.__table__,
        ],
    )


def _seed_ingestion(session: Session) -> int:
    """Insert one source and ingestion run for check execution scope."""

    source = Source(source_id="SRC_SCOPE", kind=SourceKind.XLSX, uri="file:///tmp/mock.xlsx")
    session.add(source)
    session.commit()
    session.refresh(source)

    run = IngestionRun(
        source_pk=int(source.id),
        extractor_name="extract_cross_source",
        status=IngestionStatus.SUCCESS,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return int(run.id)


def _create_cross_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic metrics table used by cross-source checks."""

    metadata = sa.MetaData()
    table = sa.Table(
        "stg_cross_source_metrics",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("metric_key", sa.String(200), nullable=False),
        sa.Column("metric_value", sa.Numeric(20, 6), nullable=True),
        sa.Column("unit", sa.String(40), nullable=True),
        sa.Column("status", sa.String(16), nullable=True),
    )
    metadata.create_all(engine)
    return table


def test_cross_source_check_detects_conflict_and_persists_inconsistency() -> None:
    """Check should fail and persist `INCONSISTENTE` row for conflicting sources."""

    engine = _make_engine()
    _create_base_tables(engine)
    table = _create_cross_table(engine)

    with Session(engine) as session:
        ingestion_id = _seed_ingestion(session)

    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_DIMAC_A",
                    "lineage_ref_id": 101,
                    "metric_key": "share_bb_total",
                    "metric_value": Decimal("60"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_DIMAC_B",
                    "lineage_ref_id": 202,
                    "metric_key": "share_bb_total",
                    "metric_value": Decimal("55"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 3,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_DIMAC_A",
                    "lineage_ref_id": 103,
                    "metric_key": "audiencia_total",
                    "metric_value": Decimal("1000"),
                    "unit": "count",
                    "status": "ok",
                },
                {
                    "id": 4,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_DIMAC_B",
                    "lineage_ref_id": 204,
                    "metric_key": "audiencia_total",
                    "metric_value": Decimal("1000"),
                    "unit": "count",
                    "status": "ok",
                },
            ],
        )

    spec = CrossSourceDatasetSpec(
        dataset_id="dimac_metrics",
        table="stg_cross_source_metrics",
        status_column="status",
        allowed_statuses=("ok",),
    )
    check = CrossSourceInconsistencyCheck(
        (spec,),
        severity=Severity.ERROR,
        tolerance=Decimal("0"),
        persist_inconsistencies=True,
    )

    with Session(engine) as session:
        result = check.run(CheckContext(ingestion_id=ingestion_id, resources={"session": session}))
        persisted = session.exec(
            select(DQInconsistency).where(DQInconsistency.ingestion_id == ingestion_id)
        ).all()

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["status"] == "INCONSISTENTE"
    assert result.evidence["finding_count"] == 1
    assert len(persisted) == 1
    row = persisted[0]
    assert row.metric_key == "share_bb_total"
    assert row.status.value == "inconsistente"
    assert row.severity.value == "error"
    assert row.dataset_id == "dimac_metrics"
    assert json.loads(row.sources_json) == ["SRC_DIMAC_A", "SRC_DIMAC_B"]


def test_cross_source_check_passes_when_values_are_consistent() -> None:
    """Check should pass when compared sources have the same metric value."""

    engine = _make_engine()
    _create_base_tables(engine)
    table = _create_cross_table(engine)

    with Session(engine) as session:
        ingestion_id = _seed_ingestion(session)

    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_SOCIAL_A",
                    "lineage_ref_id": 301,
                    "metric_key": "engajamento_total",
                    "metric_value": Decimal("42"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": ingestion_id,
                    "source_id": "SRC_SOCIAL_B",
                    "lineage_ref_id": 302,
                    "metric_key": "engajamento_total",
                    "metric_value": Decimal("42"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )

    spec = CrossSourceDatasetSpec(
        dataset_id="social_metrics",
        table="stg_cross_source_metrics",
        status_column="status",
        allowed_statuses=("ok",),
    )
    check = CrossSourceInconsistencyCheck(
        (spec,),
        severity=Severity.WARNING,
        tolerance=Decimal("0"),
        persist_inconsistencies=True,
    )

    with Session(engine) as session:
        result = check.run(CheckContext(ingestion_id=ingestion_id, resources={"session": session}))
        persisted = session.exec(
            select(DQInconsistency).where(DQInconsistency.ingestion_id == ingestion_id)
        ).all()

    assert result.status == CheckStatus.PASS
    assert result.severity == Severity.INFO
    assert result.evidence["finding_count"] == 0
    assert len(persisted) == 0


def test_cross_source_check_fails_when_required_columns_are_missing() -> None:
    """Check should fail with actionable schema evidence when config is invalid."""

    engine = _make_engine()
    _create_base_tables(engine)
    metadata = sa.MetaData()
    sa.Table(
        "stg_cross_source_bad_schema",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("metric_key", sa.String(200), nullable=False),
        sa.Column("unit", sa.String(40), nullable=True),
        sa.Column("status", sa.String(16), nullable=True),
    )
    metadata.create_all(engine)

    with Session(engine) as session:
        ingestion_id = _seed_ingestion(session)
        spec = CrossSourceDatasetSpec(
            dataset_id="bad_schema",
            table="stg_cross_source_bad_schema",
            status_column="status",
            allowed_statuses=("ok",),
        )
        result = CrossSourceInconsistencyCheck((spec,)).run(
            CheckContext(ingestion_id=ingestion_id, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.WARNING
    assert len(result.evidence["invalid_schema"]) == 1
    assert "metric_value" in result.evidence["invalid_schema"][0]["missing_columns"]

