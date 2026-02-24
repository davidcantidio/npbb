"""Unit tests for ETL source-health operational queries."""

from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.dq_results import DQCheckResult, DQCheckSeverity, DQCheckStatus
from app.models.etl_lineage import LineageRef
from app.models.etl_registry import (
    IngestionRun,
    IngestionStatus,
    Source,
    SourceHealthStatus,
    SourceKind,
)
from app.services.etl_health_queries import (
    list_source_health_status,
    source_health_rows_to_dicts,
    summarize_source_health,
)


def make_engine():
    """Create isolated in-memory SQLite engine for health query tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry/lineage/dq tables required by health queries."""

    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            DQCheckResult.__table__,
        ],
    )

    metadata = sa.MetaData()
    sa.Table(
        "stg_optin_transactions",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
    )
    sa.Table(
        "attendance_access_control",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
    )
    metadata.create_all(engine)


def test_list_source_health_status_returns_deterministic_rows_and_counts() -> None:
    """Health query should return deterministic rows with load/failure counts."""

    engine = make_engine()
    create_required_tables(engine)

    t0 = datetime(2025, 12, 12, 18, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 19, 0, tzinfo=timezone.utc)
    t2 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)

    run_a_id: int
    run_b_id: int
    with Session(engine) as session:
        src_a = Source(source_id="SRC_A", kind=SourceKind.XLSX, uri="file:///a.xlsx")
        src_b = Source(source_id="SRC_B", kind=SourceKind.XLSX, uri="file:///b.xlsx")
        src_c = Source(source_id="SRC_C", kind=SourceKind.PDF, uri="file:///c.pdf")
        src_d = Source(source_id="SRC_D", kind=SourceKind.PPTX, uri="file:///d.pptx")
        session.add(src_a)
        session.add(src_b)
        session.add(src_c)
        session.add(src_d)
        session.commit()
        session.refresh(src_a)
        session.refresh(src_b)
        session.refresh(src_c)

        run_a = IngestionRun(
            source_pk=src_a.id,
            status=IngestionStatus.SUCCESS,
            started_at=t2,
            finished_at=t2,
            extractor_name="extract_a",
            records_read=12,
            records_loaded=10,
            notes="Execucao concluida",
        )
        run_b = IngestionRun(
            source_pk=src_b.id,
            status=IngestionStatus.PARTIAL,
            started_at=t1,
            finished_at=t1,
            extractor_name="extract_b",
            records_read=8,
            records_loaded=5,
            notes="Faltou aba de leads",
        )
        run_c = IngestionRun(
            source_pk=src_c.id,
            status=IngestionStatus.FAILED,
            started_at=t0,
            finished_at=t0,
            extractor_name="extract_c",
            records_read=4,
            records_loaded=0,
            notes="Erro no parser",
            error_message="Arquivo invalido",
        )
        session.add(run_a)
        session.add(run_b)
        session.add(run_c)
        session.commit()
        session.refresh(run_a)
        session.refresh(run_b)
        session.refresh(run_c)
        run_a_id = int(run_a.id)
        run_b_id = int(run_b.id)

        session.add(
            DQCheckResult(
                ingestion_id=run_a_id,
                source_id=src_a.source_id,
                lineage_ref_id=None,
                check_id="dq.sample.warning",
                severity=DQCheckSeverity.WARNING,
                status=DQCheckStatus.FAIL,
                message="Warning de schema",
                details_json=None,
            )
        )
        session.add(
            DQCheckResult(
                ingestion_id=run_b_id,
                source_id=src_b.source_id,
                lineage_ref_id=None,
                check_id="dq.sample.error",
                severity=DQCheckSeverity.ERROR,
                status=DQCheckStatus.FAIL,
                message="Erro critico de reconciliacao",
                details_json=None,
            )
        )
        session.commit()

    with engine.begin() as conn:
        stg_table = sa.Table("stg_optin_transactions", sa.MetaData(), autoload_with=engine)
        canonical_table = sa.Table("attendance_access_control", sa.MetaData(), autoload_with=engine)
        conn.execute(
            stg_table.insert(),
                [
                    {"id": 1, "ingestion_id": run_a_id},
                    {"id": 2, "ingestion_id": run_a_id},
                    {"id": 3, "ingestion_id": run_a_id},
                    {"id": 4, "ingestion_id": run_b_id},
                ],
            )
        conn.execute(
            canonical_table.insert(),
            [
                {"id": 1, "ingestion_id": run_a_id},
                {"id": 2, "ingestion_id": run_a_id},
            ],
        )

    with Session(engine) as session:
        rows = list_source_health_status(session)
        summary = summarize_source_health(rows)
        payload = source_health_rows_to_dicts(rows)

    assert [row.source_id for row in rows] == ["SRC_A", "SRC_B", "SRC_C", "SRC_D"]

    by_source = {row.source_id: row for row in rows}

    assert by_source["SRC_A"].health_status == SourceHealthStatus.DEGRADED
    assert by_source["SRC_A"].dq_warning_fail_count == 1
    assert by_source["SRC_A"].dq_error_fail_count == 0
    assert by_source["SRC_A"].staging_rows_loaded == 3
    assert by_source["SRC_A"].canonical_rows_loaded == 2
    assert by_source["SRC_A"].records_loaded == 10

    assert by_source["SRC_B"].health_status == SourceHealthStatus.PARTIAL
    assert by_source["SRC_B"].health_reason == "Faltou aba de leads"
    assert by_source["SRC_B"].dq_error_fail_count == 1
    assert by_source["SRC_B"].staging_rows_loaded == 1
    assert by_source["SRC_B"].canonical_rows_loaded == 0

    assert by_source["SRC_C"].health_status == SourceHealthStatus.FAILED
    assert by_source["SRC_C"].health_reason == "Arquivo invalido"

    assert by_source["SRC_D"].health_status == SourceHealthStatus.NO_RUN
    assert by_source["SRC_D"].health_reason == "Sem ingestao registrada para a fonte."

    assert summary.total_sources == 4
    assert summary.status_counts["degraded"] == 1
    assert summary.status_counts["partial"] == 1
    assert summary.status_counts["failed"] == 1
    assert summary.status_counts["no_run"] == 1

    assert payload[0]["source_id"] == "SRC_A"
    assert payload[0]["health_status"] == "degraded"
    assert payload[0]["staging_rows_loaded"] == 3
    assert payload[0]["canonical_rows_loaded"] == 2


def test_list_source_health_status_supports_latest_status_and_kind_filters() -> None:
    """Health query should apply status and source-kind filters deterministically."""

    engine = make_engine()
    create_required_tables(engine)

    with Session(engine) as session:
        src_ok = Source(source_id="SRC_OK", kind=SourceKind.XLSX, uri="file:///ok.xlsx")
        src_partial = Source(source_id="SRC_PARTIAL", kind=SourceKind.XLSX, uri="file:///p.xlsx")
        src_pdf = Source(source_id="SRC_PDF", kind=SourceKind.PDF, uri="file:///pdf.pdf")
        session.add(src_ok)
        session.add(src_partial)
        session.add(src_pdf)
        session.commit()
        session.refresh(src_ok)
        session.refresh(src_partial)
        session.refresh(src_pdf)

        session.add(
            IngestionRun(source_pk=src_ok.id, status=IngestionStatus.SUCCESS, extractor_name="extract_ok")
        )
        session.add(
            IngestionRun(
                source_pk=src_partial.id,
                status=IngestionStatus.PARTIAL,
                extractor_name="extract_partial",
            )
        )
        session.add(
            IngestionRun(source_pk=src_pdf.id, status=IngestionStatus.SUCCESS, extractor_name="extract_pdf")
        )
        session.commit()

        success_xlsx = list_source_health_status(
            session,
            statuses=[IngestionStatus.SUCCESS],
            source_kinds=[SourceKind.XLSX],
        )

    assert [row.source_id for row in success_xlsx] == ["SRC_OK"]
    assert success_xlsx[0].latest_status == IngestionStatus.SUCCESS
    assert success_xlsx[0].source_kind == SourceKind.XLSX
