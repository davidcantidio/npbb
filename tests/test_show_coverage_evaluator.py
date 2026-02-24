"""Tests for show/day coverage evaluator with actionable missing-input output."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402
from etl.validate.show_coverage_evaluator import (  # noqa: E402
    evaluate_coverage,
    evaluate_coverage_payload,
)


def _make_engine():
    """Create isolated in-memory SQLite engine for evaluator tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _dedupe_event_session_indexes() -> None:
    """Remove duplicated indexes for `event_sessions` table in test metadata."""

    table = EventSession.__table__
    seen: set[tuple[str, tuple[str, ...]]] = set()
    duplicates = []
    for index in list(table.indexes):
        key = (str(index.name), tuple(column.name for column in index.columns))
        if key in seen:
            duplicates.append(index)
            continue
        seen.add(key)
    for index in duplicates:
        table.indexes.discard(index)


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimum schema needed by evaluator tests."""

    _dedupe_event_session_indexes()
    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            StgAccessControlSession.__table__,
            StgOptinTransaction.__table__,
        ],
    )


def _seed_show_coverage_fixture(engine) -> None:  # noqa: ANN001
    """Seed one partial show day (12/12) and one gap show day (14/12)."""

    with Session(engine) as session:
        show_12 = EventSession(
            event_id=1,
            session_key="TMJ2025_20251212_SHOW",
            session_name="Show 12/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 12),
        )
        show_14 = EventSession(
            event_id=1,
            session_key="TMJ2025_20251214_SHOW",
            session_name="Show 14/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 14),
        )
        session.add(show_12)
        session.add(show_14)
        session.commit()
        session.refresh(show_12)

        src_access_12 = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/acesso_12.pdf",
        )
        src_sales_12 = Source(
            source_id="SRC_VENDAS_NOTURNO_DOZE",
            kind=SourceKind.CSV,
            uri="file:///tmp/vendas_12.csv",
        )
        src_optin_12 = Source(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_12.xlsx",
        )
        session.add(src_access_12)
        session.add(src_sales_12)
        session.add(src_optin_12)
        session.commit()
        session.refresh(src_access_12)
        session.refresh(src_sales_12)
        session.refresh(src_optin_12)

        run_access = IngestionRun(source_pk=src_access_12.id, status=IngestionStatus.SUCCESS)
        run_sales = IngestionRun(source_pk=src_sales_12.id, status=IngestionStatus.PARTIAL)
        run_optin = IngestionRun(source_pk=src_optin_12.id, status=IngestionStatus.FAILED)
        session.add(run_access)
        session.add(run_sales)
        session.add(run_optin)
        session.commit()
        session.refresh(run_access)

        lineage_access = LineageRef(
            source_id=src_access_12.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela de acesso show 12/12",
        )
        session.add(lineage_access)
        session.commit()
        session.refresh(lineage_access)

        session.add(
            StgAccessControlSession(
                source_id=src_access_12.source_id,
                ingestion_id=run_access.id,
                lineage_ref_id=int(lineage_access.id),
                event_id=1,
                session_id=int(show_12.id),
                pdf_page=1,
                session_name="Show 12/12",
                raw_payload_json="{}",
            )
        )
        session.commit()


def test_evaluate_coverage_differentiates_missing_file_vs_partial_extraction() -> None:
    """Evaluator should mark catalog-missing as gap and extraction failures as partial."""

    engine = _make_engine()
    _create_required_tables(engine)
    _seed_show_coverage_fixture(engine)

    with Session(engine) as session:
        report = evaluate_coverage(session, event_id=1)

    assert report.summary["total_sessions"] == 2
    assert report.summary["partial_sessions"] == 1
    assert report.summary["gap_sessions"] == 1

    by_session = {item.session_key: item for item in report.sessions}
    assert by_session["TMJ2025_20251212_SHOW"].status == "partial"
    assert by_session["TMJ2025_20251214_SHOW"].status == "gap"

    by_cell = {(item.session_key, item.dataset.value): item for item in report.missing_inputs}

    missing_access_14 = by_cell[("TMJ2025_20251214_SHOW", "access_control")]
    assert missing_access_14.status == "gap"
    assert missing_access_14.reason_code == "missing_in_catalog"
    assert missing_access_14.request_action.startswith("Solicitar:")

    missing_optin_12 = by_cell[("TMJ2025_20251212_SHOW", "optin")]
    assert missing_optin_12.status == "partial"
    assert missing_optin_12.reason_code == "ingestion_failed"
    assert missing_optin_12.sources_considered == ("SRC_OPTIN_NOTURNO_DOZE",)

    missing_sales_12 = by_cell[("TMJ2025_20251212_SHOW", "ticket_sales")]
    assert missing_sales_12.status == "partial"
    assert missing_sales_12.reason_code == "ingestion_partial"

    missing_optin_14 = by_cell[("TMJ2025_20251214_SHOW", "optin")]
    assert missing_optin_14.status == "partial"
    assert missing_optin_14.reason_code == "missing_in_catalog"


def test_evaluate_coverage_payload_contains_lineage_and_sources_considered() -> None:
    """Payload serializer should expose lineage notes and considered source IDs."""

    engine = _make_engine()
    _create_required_tables(engine)
    _seed_show_coverage_fixture(engine)

    with Session(engine) as session:
        payload = evaluate_coverage_payload(session, event_id=1)

    assert payload["status"] == "gap"
    assert payload["summary"]["total_missing_inputs"] >= 1
    items = payload["missing_inputs"]
    assert items
    first = items[0]
    assert "lineage_note" in first
    assert "sources_considered" in first
