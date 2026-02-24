"""Unit tests for ETL operational catalog queries."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind
from app.services.etl_catalog_queries import (
    latest_ingestion_by_source,
    list_ingestion_runs,
    summarize_latest_ingestion_rows,
)


def make_engine():
    """Create isolated in-memory SQLite engine for catalog query tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_registry_tables(engine) -> None:  # noqa: ANN001
    """Create only ETL registry tables required for catalog query tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__],
    )


def test_latest_ingestion_by_source_returns_one_row_per_source_with_latest_run() -> None:
    """Query returns one row per source and picks latest run by started_at + id."""
    engine = make_engine()
    create_registry_tables(engine)

    t0 = datetime(2025, 12, 12, 10, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 11, 0, tzinfo=timezone.utc)
    t2 = datetime(2025, 12, 12, 12, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        src_a = Source(source_id="SRC_A", kind=SourceKind.CSV, uri="file:///a.csv")
        src_b = Source(source_id="SRC_B", kind=SourceKind.PDF, uri="file:///b.pdf")
        src_c = Source(source_id="SRC_C", kind=SourceKind.XLSX, uri="file:///c.xlsx")
        session.add(src_a)
        session.add(src_b)
        session.add(src_c)
        session.commit()
        session.refresh(src_a)
        session.refresh(src_b)
        session.refresh(src_c)

        run_a_old = IngestionRun(
            source_pk=src_a.id,
            status=IngestionStatus.PARTIAL,
            started_at=t0,
            finished_at=t0,
            extractor_name="extract_a_old",
        )
        run_a_new = IngestionRun(
            source_pk=src_a.id,
            status=IngestionStatus.SUCCESS,
            started_at=t2,
            finished_at=t2,
            extractor_name="extract_a_new",
        )

        # same started_at for source B; deterministic tie-break should pick higher ID
        run_b_first = IngestionRun(
            source_pk=src_b.id,
            status=IngestionStatus.FAILED,
            started_at=t1,
            finished_at=t1,
            extractor_name="extract_b_1",
        )
        run_b_second = IngestionRun(
            source_pk=src_b.id,
            status=IngestionStatus.SUCCESS,
            started_at=t1,
            finished_at=t1,
            extractor_name="extract_b_2",
        )
        session.add(run_a_old)
        session.add(run_a_new)
        session.add(run_b_first)
        session.add(run_b_second)
        session.commit()
        session.refresh(run_a_old)
        session.refresh(run_a_new)
        session.refresh(run_b_first)
        session.refresh(run_b_second)

        rows = latest_ingestion_by_source(session)

    assert [row.source_id for row in rows] == ["SRC_A", "SRC_B", "SRC_C"]
    by_source = {row.source_id: row for row in rows}

    # Source A -> latest by started_at
    assert by_source["SRC_A"].latest_ingestion_id == run_a_new.id
    assert by_source["SRC_A"].latest_status == IngestionStatus.SUCCESS
    assert by_source["SRC_A"].latest_extractor_name == "extract_a_new"
    # SQLite in-memory can return naive datetimes even when timezone-aware values
    # were inserted. Normalize both values to compare the instant in tests.
    assert by_source["SRC_A"].latest_started_at.replace(tzinfo=timezone.utc) == t2

    # Source B -> tie by started_at resolved by highest id
    winner_b = max(run_b_first.id, run_b_second.id)
    assert by_source["SRC_B"].latest_ingestion_id == winner_b
    assert by_source["SRC_B"].latest_extractor_name == "extract_b_2"

    # Source C -> no runs
    assert by_source["SRC_C"].latest_ingestion_id is None
    assert by_source["SRC_C"].latest_status is None
    assert by_source["SRC_C"].latest_started_at is None
    assert by_source["SRC_C"].latest_finished_at is None


def test_latest_ingestion_by_source_supports_filters_and_summary() -> None:
    """Query filters by source kind/status and exposes stable summary counters."""
    engine = make_engine()
    create_registry_tables(engine)

    t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        src_pdf_ok = Source(source_id="SRC_PDF_OK", kind=SourceKind.PDF, uri="file:///ok.pdf")
        src_pdf_fail = Source(source_id="SRC_PDF_FAIL", kind=SourceKind.PDF, uri="file:///fail.pdf")
        src_xlsx = Source(source_id="SRC_XLSX", kind=SourceKind.XLSX, uri="file:///a.xlsx")
        src_empty = Source(source_id="SRC_EMPTY", kind=SourceKind.PPTX, uri="file:///none.pptx")
        session.add(src_pdf_ok)
        session.add(src_pdf_fail)
        session.add(src_xlsx)
        session.add(src_empty)
        session.commit()
        session.refresh(src_pdf_ok)
        session.refresh(src_pdf_fail)
        session.refresh(src_xlsx)

        session.add(
            IngestionRun(
                source_pk=src_pdf_ok.id,
                status=IngestionStatus.SUCCESS,
                started_at=t1,
                finished_at=t1,
                extractor_name="extract_pdf_ok",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_pdf_fail.id,
                status=IngestionStatus.FAILED,
                started_at=t0,
                finished_at=t0,
                extractor_name="extract_pdf_fail",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_xlsx.id,
                status=IngestionStatus.PARTIAL,
                started_at=t0,
                finished_at=t0,
                extractor_name="extract_xlsx",
            )
        )
        session.commit()

        all_rows = latest_ingestion_by_source(session)
        summary = summarize_latest_ingestion_rows(all_rows)
        filtered = latest_ingestion_by_source(
            session,
            statuses=[IngestionStatus.SUCCESS],
            source_kinds=[SourceKind.PDF],
        )

    assert summary.total_sources == 4
    assert summary.sources_with_ingestion == 3
    assert summary.sources_without_ingestion == 1
    assert summary.latest_status_counts == {"failed": 1, "partial": 1, "success": 1}
    assert [row.source_id for row in filtered] == ["SRC_PDF_OK"]


def test_list_ingestion_runs_supports_filters_and_pagination() -> None:
    """Run-level query applies status/kind/source filters and pagination correctly."""
    engine = make_engine()
    create_registry_tables(engine)

    t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)
    t2 = datetime(2025, 12, 12, 22, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        src_pdf = Source(source_id="SRC_PDF", kind=SourceKind.PDF, uri="file:///a.pdf")
        src_xlsx = Source(source_id="SRC_XLSX", kind=SourceKind.XLSX, uri="file:///b.xlsx")
        session.add(src_pdf)
        session.add(src_xlsx)
        session.commit()
        session.refresh(src_pdf)
        session.refresh(src_xlsx)

        session.add(
            IngestionRun(
                source_pk=src_pdf.id,
                status=IngestionStatus.PARTIAL,
                started_at=t0,
                extractor_name="extract_pdf_old",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_pdf.id,
                status=IngestionStatus.SUCCESS,
                started_at=t1,
                extractor_name="extract_pdf_new",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_xlsx.id,
                status=IngestionStatus.FAILED,
                started_at=t2,
                extractor_name="extract_xlsx",
            )
        )
        session.commit()

        all_runs = list_ingestion_runs(session, limit=10, offset=0)
        pdf_only = list_ingestion_runs(
            session,
            source_kinds=[SourceKind.PDF],
            limit=10,
            offset=0,
        )
        failed_only = list_ingestion_runs(
            session,
            statuses=[IngestionStatus.FAILED],
            limit=10,
            offset=0,
        )
        src_pdf_page = list_ingestion_runs(
            session,
            source_ids=["SRC_PDF"],
            limit=1,
            offset=1,
        )

    assert [row.source_id for row in all_runs] == ["SRC_XLSX", "SRC_PDF", "SRC_PDF"]
    assert [row.status for row in pdf_only] == [IngestionStatus.SUCCESS, IngestionStatus.PARTIAL]
    assert [row.source_id for row in failed_only] == ["SRC_XLSX"]
    assert len(src_pdf_page) == 1
    assert src_pdf_page[0].source_id == "SRC_PDF"
    assert src_pdf_page[0].status == IngestionStatus.PARTIAL
