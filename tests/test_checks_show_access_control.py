"""Unit tests for missing show access-control coverage check."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from etl.validate.checks_show_access_control import MissingShowAccessControlCheck
from etl.validate.framework import CheckContext, CheckStatus, Severity

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for show-coverage check tests."""

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
    """Create minimum schema required by show-access coverage check tests."""

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


def _write_show_agenda(path: Path) -> Path:
    """Write agenda fixture with expected show sessions (12/12 and 14/12)."""

    path.write_text(
        "\n".join(
            [
                "version: 1",
                "sessions:",
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


def _insert_show_session(
    session: Session,
    *,
    event_id: int,
    session_key: str,
    session_date: date,
) -> int:
    """Insert one show session row and return its identifier."""

    row = EventSession(
        event_id=event_id,
        session_key=session_key,
        session_name=session_key,
        session_type=EventSessionType.NOTURNO_SHOW,
        session_date=session_date,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return int(row.id)


def _insert_access_control_observed(
    session: Session,
    *,
    source_id: str,
    source_uri: str,
    session_id: int,
) -> None:
    """Insert source/run/lineage/staging row indicating observed access coverage."""

    source = Source(
        source_id=source_id,
        kind=SourceKind.PDF,
        uri=source_uri,
    )
    session.add(source)
    session.commit()
    session.refresh(source)

    run = IngestionRun(source_pk=source.id, status=IngestionStatus.SUCCESS)
    session.add(run)
    session.commit()
    session.refresh(run)

    lineage = LineageRef(
        source_id=source.source_id,
        ingestion_id=run.id,
        location_type=LineageLocationType.PAGE,
        location_value="page:1",
        evidence_text="Tabela controle de acesso",
    )
    session.add(lineage)
    session.commit()
    session.refresh(lineage)

    session.add(
        StgAccessControlSession(
            source_id=source.source_id,
            ingestion_id=run.id,
            lineage_ref_id=int(lineage.id),
            event_id=2025,
            session_id=session_id,
            pdf_page=1,
            session_name="Show",
            raw_payload_json="{}",
        )
    )
    session.commit()


def test_missing_show_access_control_check_flags_gap_for_expected_show_day(tmp_path: Path) -> None:
    """Check should fail when expected show day has no access-control coverage."""

    engine = _make_engine()
    _create_required_tables(engine)
    agenda_path = _write_show_agenda(tmp_path / "agenda_master.yml")

    with Session(engine) as session:
        id_show_12 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251214_SHOW",
            session_date=date(2025, 12, 14),
        )
        _insert_access_control_observed(
            session,
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            source_uri="file:///tmp/access_12.pdf",
            session_id=id_show_12,
        )

        result = MissingShowAccessControlCheck(
            event_id=2025,
            agenda_path=agenda_path,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["finding_count"] >= 1
    sample = result.evidence["findings_sample"][0]
    assert sample["session_date"] == "2025-12-14"
    assert "PDF de controle de acesso" in sample["expected_artifact"]
    assert "show" in sample["critical_reason"].lower()


def test_missing_show_access_control_check_passes_when_focus_days_have_coverage(
    tmp_path: Path,
) -> None:
    """Check should pass when both focus show days have observed access coverage."""

    engine = _make_engine()
    _create_required_tables(engine)
    agenda_path = _write_show_agenda(tmp_path / "agenda_master.yml")

    with Session(engine) as session:
        id_show_12 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        id_show_14 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251214_SHOW",
            session_date=date(2025, 12, 14),
        )
        _insert_access_control_observed(
            session,
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            source_uri="file:///tmp/access_12.pdf",
            session_id=id_show_12,
        )
        _insert_access_control_observed(
            session,
            source_id="SRC_ACESSO_NOTURNO_QUATORZE",
            source_uri="file:///tmp/access_14.pdf",
            session_id=id_show_14,
        )

        result = MissingShowAccessControlCheck(
            event_id=2025,
            agenda_path=agenda_path,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.PASS
    assert result.severity == Severity.INFO
    assert result.evidence["finding_count"] == 0


def test_missing_show_access_control_check_flags_missing_expected_session_from_agenda(
    tmp_path: Path,
) -> None:
    """Check should fail when agenda expects show day absent from event_sessions."""

    engine = _make_engine()
    _create_required_tables(engine)
    agenda_path = _write_show_agenda(tmp_path / "agenda_master.yml")

    with Session(engine) as session:
        id_show_12 = _insert_show_session(
            session,
            event_id=2025,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
        )
        _insert_access_control_observed(
            session,
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            source_uri="file:///tmp/access_12.pdf",
            session_id=id_show_12,
        )

        result = MissingShowAccessControlCheck(
            event_id=2025,
            agenda_path=agenda_path,
        ).run(CheckContext(ingestion_id=None, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    codes = {item["reason_code"] for item in result.evidence["findings_sample"]}
    assert "missing_show_session_in_event_sessions" in codes
