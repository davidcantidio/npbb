"""Tests for agenda master, idempotent session upsert and coverage evaluation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import (  # noqa: E402
    IngestionRun,
    IngestionStatus,
    Source,
    SourceKind,
)
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402
from app.services.session_seed_from_agenda import upsert_event_sessions_from_agenda  # noqa: E402
from etl.transform.agenda_loader import load_agenda_master  # noqa: E402
from etl.validate.show_coverage_evaluator import evaluate_coverage  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for agenda/coverage tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _dedupe_event_session_indexes() -> None:
    """Remove duplicated indexes created by dual event_sessions ORM mappings.

    The project currently maps `event_sessions` in two modules. In tests that
    import both, SQLAlchemy metadata may contain duplicated index objects with
    the same name. This helper keeps one index per `(name, columns)` pair so
    in-memory schema creation remains deterministic.
    """

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
    """Create minimum schema needed by parser/upsert/evaluator tests."""

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
        ],
    )


def _write_agenda_fixture(path: Path) -> Path:
    """Write agenda fixture with day and show sessions for 12/12 and 14/12."""

    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T10:00:00-03:00",
                "    type: diurno_gratuito",
                "    name: Programacao Diurna 12/12",
                "    session_key: TMJ2025_20251212_DIURNO",
                "  - event_id: 2025",
                "    session_date: 2025-12-12",
                "    start_at: 2025-12-12T20:00:00-03:00",
                "    type: noturno_show",
                "    name: Show 12/12",
                "    session_key: TMJ2025_20251212_SHOW",
                "  - event_id: 2025",
                "    session_date: 2025-12-14",
                "    start_at: 2025-12-14T20:00:00-03:00",
                "    type: noturno_show",
                "    name: Show 14/12",
                "    session_key: TMJ2025_20251214_SHOW",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_show_coverage_agenda_parser_fixture_contains_day_and_show_sessions(tmp_path: Path) -> None:
    """Agenda fixture parser should expose both day and show session types."""

    agenda_path = _write_agenda_fixture(tmp_path / "agenda_master.yml")
    agenda = load_agenda_master(agenda_path)

    assert agenda.version == 1
    assert len(agenda.sessions) == 3
    session_types = {session.session_type.value for session in agenda.sessions}
    assert "diurno_gratuito" in session_types
    assert "noturno_show" in session_types


def test_show_coverage_upsert_idempotent_and_missing_inputs_are_actionable(tmp_path: Path) -> None:
    """Upsert should be idempotent and evaluator should report actionable missing_inputs."""

    engine = _make_engine()
    _create_required_tables(engine)
    agenda_path = _write_agenda_fixture(tmp_path / "agenda_master.yml")
    agenda = load_agenda_master(agenda_path)

    with Session(engine) as session:
        first = upsert_event_sessions_from_agenda(session, agenda, actor="qa")
        second = upsert_event_sessions_from_agenda(session, agenda, actor="qa")

        assert first.created_count == 3
        assert second.created_count == 0
        assert second.updated_count == 0
        assert second.unchanged_count == 3

        sessions = session.exec(select(EventSession).order_by(EventSession.session_key)).all()
        assert [item.session_key for item in sessions] == [
            "TMJ2025_20251212_DIURNO",
            "TMJ2025_20251212_SHOW",
            "TMJ2025_20251214_SHOW",
        ]
        session_by_key = {item.session_key: item for item in sessions}

        src_access = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/access_12.pdf",
        )
        src_sales = Source(
            source_id="SRC_VENDAS_NOTURNO_DOZE",
            kind=SourceKind.CSV,
            uri="file:///tmp/sales_12.csv",
        )
        session.add(src_access)
        session.add(src_sales)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_sales)

        run_access = IngestionRun(source_pk=src_access.id, status=IngestionStatus.SUCCESS)
        run_sales = IngestionRun(source_pk=src_sales.id, status=IngestionStatus.PARTIAL)
        session.add(run_access)
        session.add(run_sales)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_sales)

        lineage_access = LineageRef(
            source_id=src_access.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela controle de acesso show 12/12",
        )
        session.add(lineage_access)
        session.commit()
        session.refresh(lineage_access)

        session.add(
            StgAccessControlSession(
                source_id=src_access.source_id,
                ingestion_id=run_access.id,
                lineage_ref_id=int(lineage_access.id),
                event_id=2025,
                session_id=int(session_by_key["TMJ2025_20251212_SHOW"].id),
                pdf_page=1,
                session_name="Show 12/12",
                raw_payload_json="{}",
            )
        )
        session.commit()

        report = evaluate_coverage(session, event_id=2025)

    by_session = {item.session_key: item for item in report.sessions}
    assert by_session["TMJ2025_20251212_SHOW"].status == "partial"
    assert by_session["TMJ2025_20251214_SHOW"].status == "gap"

    by_cell = {(item.session_key, item.dataset.value): item for item in report.missing_inputs}
    assert ("TMJ2025_20251214_SHOW", "access_control") in by_cell
    assert ("TMJ2025_20251212_SHOW", "ticket_sales") in by_cell

    missing_access_14 = by_cell[("TMJ2025_20251214_SHOW", "access_control")]
    assert missing_access_14.status == "gap"
    assert missing_access_14.reason_code == "missing_in_catalog"
    assert missing_access_14.request_action.startswith("Solicitar:")

    missing_sales_12 = by_cell[("TMJ2025_20251212_SHOW", "ticket_sales")]
    assert missing_sales_12.status == "partial"
    assert missing_sales_12.reason_code == "ingestion_partial"
    assert missing_sales_12.session_key == "TMJ2025_20251212_SHOW"
    assert missing_sales_12.dataset.value == "ticket_sales"

