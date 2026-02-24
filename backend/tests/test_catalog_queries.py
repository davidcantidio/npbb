"""Tests for operational catalog queries (registry + session coverage)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.etl_registry import (
    CoverageDataset,
    CoverageStatus,
    IngestionRun as RegistryIngestionRun,
    IngestionStatus,
    Source as RegistrySource,
    SourceKind,
)
from app.models.models import EventSession, EventSessionType, Source as LegacySource
from app.services.etl_catalog_queries import latest_ingestion_by_source, list_ingestion_runs
from app.services.etl_coverage_queries import build_session_coverage_matrix, coverage_rows_to_dicts


def make_engine():
    """Create isolated in-memory SQLite engine for operational query tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal table set used by catalog and coverage query tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            RegistrySource.__table__,
            RegistryIngestionRun.__table__,
        ],
    )


def test_latest_ingestion_by_source_and_run_list_have_deterministic_order() -> None:
    """Catalog queries must return deterministic ordering with stable tie-break."""
    engine = make_engine()
    create_required_tables(engine)

    t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        src_a = RegistrySource(source_id="SRC_A", kind=SourceKind.PDF, uri="file:///a.pdf")
        src_b = RegistrySource(source_id="SRC_B", kind=SourceKind.XLSX, uri="file:///b.xlsx")
        src_c = RegistrySource(source_id="SRC_C", kind=SourceKind.CSV, uri="file:///c.csv")
        session.add(src_a)
        session.add(src_b)
        session.add(src_c)
        session.commit()
        session.refresh(src_a)
        session.refresh(src_b)

        # Source A: tie on started_at, higher id should win.
        run_a_1 = RegistryIngestionRun(
            source_pk=src_a.id,
            status=IngestionStatus.PARTIAL,
            started_at=t1,
            extractor_name="extract_a_1",
        )
        run_a_2 = RegistryIngestionRun(
            source_pk=src_a.id,
            status=IngestionStatus.SUCCESS,
            started_at=t1,
            extractor_name="extract_a_2",
        )
        run_b = RegistryIngestionRun(
            source_pk=src_b.id,
            status=IngestionStatus.FAILED,
            started_at=t0,
            extractor_name="extract_b",
        )
        session.add(run_a_1)
        session.add(run_a_2)
        session.add(run_b)
        session.commit()
        session.refresh(run_a_1)
        session.refresh(run_a_2)

        latest_rows = latest_ingestion_by_source(session)
        run_rows = list_ingestion_runs(session, limit=10, offset=0)

    assert [row.source_id for row in latest_rows] == ["SRC_A", "SRC_B", "SRC_C"]
    by_source = {row.source_id: row for row in latest_rows}
    assert by_source["SRC_A"].latest_ingestion_id == max(run_a_1.id, run_a_2.id)
    assert by_source["SRC_A"].latest_status == IngestionStatus.SUCCESS
    assert by_source["SRC_C"].latest_ingestion_id is None

    assert [row.source_id for row in run_rows] == ["SRC_A", "SRC_A", "SRC_B"]
    assert run_rows[0].ingestion_id == max(run_a_1.id, run_a_2.id)


def test_coverage_matrix_returns_expected_vs_observed_contract() -> None:
    """Coverage query must produce one row per session+dataset and JSON-friendly payload."""
    engine = make_engine()
    create_required_tables(engine)

    with Session(engine) as session:
        # Expected sessions.
        session.add(
            EventSession(
                event_id=None,
                session_key="TMJ2025_20251212_SHOW",
                session_name="Show 12/12",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 12),
            )
        )
        session.add(
            EventSession(
                event_id=None,
                session_key="TMJ2025_20251213_SHOW",
                session_name="Show 13/12",
                session_type=EventSessionType.NOTURNO_SHOW,
                session_date=date(2025, 12, 13),
            )
        )

        # Observed sources.
        src_access = RegistrySource(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/acesso_12.pdf",
        )
        src_optin = RegistrySource(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_12.xlsx",
        )
        session.add(src_access)
        session.add(src_optin)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_optin)

        t0 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
        session.add(
            RegistryIngestionRun(
                source_pk=src_access.id,
                status=IngestionStatus.SUCCESS,
                started_at=t0,
                extractor_name="extract_pdf_access",
            )
        )
        session.add(
            RegistryIngestionRun(
                source_pk=src_optin.id,
                status=IngestionStatus.FAILED,
                started_at=t0,
                extractor_name="extract_xlsx_optin",
            )
        )
        session.commit()

        rows = build_session_coverage_matrix(
            session,
            expected_datasets=[CoverageDataset.ACCESS_CONTROL, CoverageDataset.OPTIN],
        )
        payload = coverage_rows_to_dicts(rows)

    assert len(rows) == 4
    by_cell = {(row.session_key, row.dataset): row for row in rows}

    assert by_cell[("TMJ2025_20251212_SHOW", CoverageDataset.ACCESS_CONTROL)].status == CoverageStatus.OBSERVED
    assert by_cell[("TMJ2025_20251212_SHOW", CoverageDataset.OPTIN)].status == CoverageStatus.INGESTION_FAILED
    assert by_cell[("TMJ2025_20251213_SHOW", CoverageDataset.ACCESS_CONTROL)].status == CoverageStatus.MISSING

    assert len(payload) == 4
    assert set(payload[0].keys()) == {
        "session_id",
        "session_key",
        "session_date",
        "session_type",
        "dataset",
        "status",
        "sources_present",
        "ingestion_ids",
        "latest_statuses",
    }
