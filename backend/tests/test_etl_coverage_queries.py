"""Unit tests for session expected-vs-observed coverage query."""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.etl_lineage import LineageLocationType, LineageRef
from app.models.etl_registry import (
    CoverageDataset,
    CoverageStatus,
    IngestionRun as RegistryIngestionRun,
    IngestionStatus,
    Source as RegistrySource,
    SourceKind,
)
from app.models.models import EventSession, EventSessionType, Source as LegacySource
from app.models.stg_access_control import StgAccessControlSession
from app.models.stg_optin import StgOptinTransaction
from app.services.etl_coverage_queries import (
    build_session_dataset_source_candidates,
    build_session_coverage_matrix,
    build_session_coverage_summary,
    coverage_rows_to_dicts,
    unresolved_staging_records_by_dataset,
)


def make_engine():
    """Create isolated in-memory SQLite engine for coverage query tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal table set required by coverage query tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            RegistrySource.__table__,
            RegistryIngestionRun.__table__,
        ],
    )


def create_required_tables_with_staging(engine) -> None:  # noqa: ANN001
    """Create minimal table set required for staging-aware coverage tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            RegistrySource.__table__,
            RegistryIngestionRun.__table__,
            LineageRef.__table__,
            StgAccessControlSession.__table__,
            StgOptinTransaction.__table__,
        ],
    )


def _seed_sessions(session: Session) -> None:
    session.add(
        EventSession(
            event_id=None,
            session_key="TMJ2025_20251212_SHOW",
            session_name="Noturno show - 2025-12-12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 12),
        )
    )
    session.add(
        EventSession(
            event_id=None,
            session_key="TMJ2025_20251213_SHOW",
            session_name="Noturno show - 2025-12-13",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 13),
        )
    )
    session.commit()


def _seed_registry_sources_and_runs(session: Session) -> None:
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
    src_sales = RegistrySource(
        source_id="SRC_VENDAS_NOTURNO_TREZE",
        kind=SourceKind.CSV,
        uri="file:///tmp/vendas_13.csv",
    )
    src_ignored = RegistrySource(
        source_id="SRC_SEM_DATA_RECONHECIVEL",
        kind=SourceKind.PPTX,
        uri="file:///tmp/sem_data.pptx",
    )
    session.add(src_access)
    session.add(src_optin)
    session.add(src_sales)
    session.add(src_ignored)
    session.commit()
    session.refresh(src_access)
    session.refresh(src_optin)
    session.refresh(src_sales)
    session.refresh(src_ignored)

    t0 = datetime(2025, 12, 12, 19, 0, tzinfo=timezone.utc)
    t1 = datetime(2025, 12, 12, 20, 0, tzinfo=timezone.utc)
    t2 = datetime(2025, 12, 12, 21, 0, tzinfo=timezone.utc)

    # access_control source has two runs; latest is SUCCESS.
    session.add(
        RegistryIngestionRun(
            source_pk=src_access.id,
            status=IngestionStatus.FAILED,
            started_at=t0,
            extractor_name="extract_pdf_access",
        )
    )
    session.add(
        RegistryIngestionRun(
            source_pk=src_access.id,
            status=IngestionStatus.SUCCESS,
            started_at=t1,
            extractor_name="extract_pdf_access",
        )
    )
    # optin source only FAILED run.
    session.add(
        RegistryIngestionRun(
            source_pk=src_optin.id,
            status=IngestionStatus.FAILED,
            started_at=t2,
            extractor_name="extract_xlsx_optin",
        )
    )
    # ticket_sales source with PARTIAL run.
    session.add(
        RegistryIngestionRun(
            source_pk=src_sales.id,
            status=IngestionStatus.PARTIAL,
            started_at=t2,
            extractor_name="extract_sales_summary",
        )
    )
    # ignored source has data but no parsable TMJ date in source_id.
    session.add(
        RegistryIngestionRun(
            source_pk=src_ignored.id,
            status=IngestionStatus.SUCCESS,
            started_at=t2,
            extractor_name="extract_misc",
        )
    )
    session.commit()


def test_build_session_coverage_matrix_expected_vs_observed() -> None:
    """Coverage matrix returns one row per session+dataset with basic status resolution."""
    engine = make_engine()
    create_required_tables(engine)

    with Session(engine) as session:
        _seed_sessions(session)
        _seed_registry_sources_and_runs(session)

        rows = build_session_coverage_matrix(
            session,
            expected_datasets=[
                CoverageDataset.ACCESS_CONTROL,
                CoverageDataset.TICKET_SALES,
                CoverageDataset.OPTIN,
            ],
        )

    assert len(rows) == 6
    by_key = {(row.session_key, row.dataset): row for row in rows}

    show12_access = by_key[("TMJ2025_20251212_SHOW", CoverageDataset.ACCESS_CONTROL)]
    assert show12_access.status == CoverageStatus.OBSERVED
    assert show12_access.sources_present == ["SRC_ACESSO_NOTURNO_DOZE"]
    assert show12_access.latest_statuses == [IngestionStatus.SUCCESS]

    show12_optin = by_key[("TMJ2025_20251212_SHOW", CoverageDataset.OPTIN)]
    assert show12_optin.status == CoverageStatus.INGESTION_FAILED
    assert show12_optin.sources_present == ["SRC_OPTIN_NOTURNO_DOZE"]
    assert show12_optin.latest_statuses == [IngestionStatus.FAILED]

    show13_sales = by_key[("TMJ2025_20251213_SHOW", CoverageDataset.TICKET_SALES)]
    assert show13_sales.status == CoverageStatus.OBSERVED_PARTIAL
    assert show13_sales.sources_present == ["SRC_VENDAS_NOTURNO_TREZE"]
    assert show13_sales.latest_statuses == [IngestionStatus.PARTIAL]

    show13_access = by_key[("TMJ2025_20251213_SHOW", CoverageDataset.ACCESS_CONTROL)]
    assert show13_access.status == CoverageStatus.MISSING
    assert show13_access.sources_present == []
    assert show13_access.latest_statuses == []


def test_build_session_dataset_source_candidates_lists_considered_sources() -> None:
    """Candidate helper should expose which sources were considered per cell."""
    engine = make_engine()
    create_required_tables(engine)

    with Session(engine) as session:
        _seed_sessions(session)
        _seed_registry_sources_and_runs(session)
        candidates = build_session_dataset_source_candidates(
            session,
            expected_datasets=[
                CoverageDataset.ACCESS_CONTROL,
                CoverageDataset.TICKET_SALES,
                CoverageDataset.OPTIN,
            ],
        )

    by_cell: dict[tuple[str, CoverageDataset], list[str]] = {}
    for item in candidates:
        key = (item.session_key, item.dataset)
        by_cell.setdefault(key, []).append(item.source_id)

    assert by_cell[("TMJ2025_20251212_SHOW", CoverageDataset.ACCESS_CONTROL)] == [
        "SRC_ACESSO_NOTURNO_DOZE"
    ]
    assert by_cell[("TMJ2025_20251212_SHOW", CoverageDataset.OPTIN)] == [
        "SRC_OPTIN_NOTURNO_DOZE"
    ]
    assert by_cell[("TMJ2025_20251213_SHOW", CoverageDataset.TICKET_SALES)] == [
        "SRC_VENDAS_NOTURNO_TREZE"
    ]
    assert ("TMJ2025_20251213_SHOW", CoverageDataset.ACCESS_CONTROL) not in by_cell


def test_coverage_rows_to_dicts_is_consumable_for_other_layers() -> None:
    """Serialized coverage rows keep stable keys and JSON-friendly values."""
    engine = make_engine()
    create_required_tables(engine)

    with Session(engine) as session:
        _seed_sessions(session)
        _seed_registry_sources_and_runs(session)
        rows = build_session_coverage_matrix(
            session,
            expected_datasets=[CoverageDataset.ACCESS_CONTROL],
        )
        payload = coverage_rows_to_dicts(rows)

    assert len(payload) == 2
    first = payload[0]
    assert set(first.keys()) == {
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
    assert isinstance(first["session_id"], int)
    assert isinstance(first["sources_present"], list)
    assert first["dataset"] == "access_control"


def test_staging_coverage_summary_lists_missing_datasets_and_unresolved_rows() -> None:
    """Coverage summary must use staging `session_id` and expose unresolved rows."""
    engine = make_engine()
    create_required_tables_with_staging(engine)

    with Session(engine) as session:
        session_12 = EventSession(
            event_id=None,
            session_key="TMJ2025_20251212_SHOW",
            session_name="Show 12/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 12),
        )
        session_13 = EventSession(
            event_id=None,
            session_key="TMJ2025_20251213_SHOW",
            session_name="Show 13/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 13),
        )
        session.add(session_12)
        session.add(session_13)
        session.commit()
        session.refresh(session_12)
        session.refresh(session_13)

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
        src_optin_orphan = RegistrySource(
            source_id="SRC_OPTIN_NOTURNO_TREZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_13.xlsx",
        )
        session.add(src_access)
        session.add(src_optin)
        session.add(src_optin_orphan)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_optin)
        session.refresh(src_optin_orphan)

        run_access = RegistryIngestionRun(
            source_pk=src_access.id,
            status=IngestionStatus.SUCCESS,
            extractor_name="extract_pdf_access",
        )
        run_optin = RegistryIngestionRun(
            source_pk=src_optin.id,
            status=IngestionStatus.SUCCESS,
            extractor_name="extract_xlsx_optin",
        )
        run_optin_orphan = RegistryIngestionRun(
            source_pk=src_optin_orphan.id,
            status=IngestionStatus.PARTIAL,
            extractor_name="extract_xlsx_optin",
        )
        session.add(run_access)
        session.add(run_optin)
        session.add(run_optin_orphan)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_optin)
        session.refresh(run_optin_orphan)

        lineage_access = LineageRef(
            source_id=src_access.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela de acesso",
        )
        lineage_optin = LineageRef(
            source_id=src_optin.source_id,
            ingestion_id=run_optin.id,
            location_type=LineageLocationType.RANGE,
            location_value="range:A6:I6",
            evidence_text="Linha de opt-in",
        )
        lineage_optin_orphan = LineageRef(
            source_id=src_optin_orphan.source_id,
            ingestion_id=run_optin_orphan.id,
            location_type=LineageLocationType.RANGE,
            location_value="range:A7:I7",
            evidence_text="Linha sem sessao",
        )
        session.add(lineage_access)
        session.add(lineage_optin)
        session.add(lineage_optin_orphan)
        session.commit()
        session.refresh(lineage_access)
        session.refresh(lineage_optin)
        session.refresh(lineage_optin_orphan)

        session.add(
            StgAccessControlSession(
                source_id=src_access.source_id,
                ingestion_id=run_access.id,
                lineage_ref_id=int(lineage_access.id),
                session_id=int(session_12.id),
                pdf_page=1,
                session_name="Show 12/12",
                raw_payload_json="{}",
            )
        )
        session.add(
            StgOptinTransaction(
                source_id=src_optin.source_id,
                ingestion_id=run_optin.id,
                lineage_ref_id=int(lineage_optin.id),
                session_id=int(session_12.id),
                sheet_name="OptIn",
                header_row=4,
                row_number=1,
                source_range="A6:I6",
                raw_payload_json="{}",
            )
        )
        session.add(
            StgOptinTransaction(
                source_id=src_optin_orphan.source_id,
                ingestion_id=run_optin_orphan.id,
                lineage_ref_id=int(lineage_optin_orphan.id),
                session_id=None,
                sheet_name="OptIn",
                header_row=4,
                row_number=2,
                source_range="A7:I7",
                raw_payload_json="{}",
            )
        )
        session.commit()

        matrix = build_session_coverage_matrix(
            session,
            expected_datasets=[CoverageDataset.ACCESS_CONTROL, CoverageDataset.OPTIN],
        )
        summary = build_session_coverage_summary(matrix)
        unresolved = unresolved_staging_records_by_dataset(
            session,
            expected_datasets=[CoverageDataset.ACCESS_CONTROL, CoverageDataset.OPTIN],
        )

    assert len(summary) == 2
    by_session = {row.session_key: row for row in summary}

    assert by_session["TMJ2025_20251212_SHOW"].status == "ok"
    assert by_session["TMJ2025_20251212_SHOW"].missing_datasets == []

    assert by_session["TMJ2025_20251213_SHOW"].status == "gap"
    assert set(by_session["TMJ2025_20251213_SHOW"].missing_datasets) == {
        CoverageDataset.ACCESS_CONTROL,
        CoverageDataset.OPTIN,
    }

    assert unresolved[CoverageDataset.ACCESS_CONTROL] == 0
    assert unresolved[CoverageDataset.OPTIN] == 1
