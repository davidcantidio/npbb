"""Tests for show-coverage checks and request-list generation."""

from __future__ import annotations

import csv
from datetime import date
import io
from pathlib import Path
import sys

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, Source  # noqa: E402
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402
from etl.validate.checks_show_access_control import MissingShowAccessControlCheck  # noqa: E402
from etl.validate.checks_show_optin import MissingShowOptInCheck  # noqa: E402
from etl.validate.framework import CheckContext, CheckStatus, Severity  # noqa: E402
from etl.validate.request_list import (  # noqa: E402
    build_missing_artifacts_list,
    render_missing_artifacts_csv,
    render_missing_artifacts_markdown,
)
from etl.validate.show_coverage_evaluator import evaluate_coverage  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for show-coverage tests."""

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
    """Create minimum schema required by show-coverage checks."""

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


def _insert_show_session(
    session: Session,
    *,
    event_id: int,
    session_key: str,
    session_date: date,
) -> None:
    """Insert one show session row."""

    session.add(
        EventSession(
            event_id=event_id,
            session_key=session_key,
            session_name=session_key,
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=session_date,
        )
    )
    session.commit()


def test_show_coverage_checks_and_request_list_for_12_and_14_december() -> None:
    """Checks should fail with actionable messages and request list should be generated."""

    engine = _make_engine()
    _create_required_tables(engine)

    with Session(engine) as session:
        _insert_show_session(
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

        context = CheckContext(ingestion_id=None, resources={"session": session})
        access_result = MissingShowAccessControlCheck(event_id=2025).run(context)
        optin_result = MissingShowOptInCheck(event_id=2025).run(context)
        coverage_report = evaluate_coverage(session, event_id=2025)

    assert access_result.status == CheckStatus.FAIL
    assert access_result.severity == Severity.ERROR
    assert "GAP critico" in access_result.message
    access_dates = {item["session_date"] for item in access_result.evidence["findings_sample"]}
    assert {"2025-12-12", "2025-12-14"}.issubset(access_dates)

    assert optin_result.status == CheckStatus.FAIL
    assert optin_result.severity == Severity.ERROR
    assert "opt-in" in optin_result.message.lower()
    optin_dates = {item["session_date"] for item in optin_result.evidence["findings_sample"]}
    assert {"2025-12-12", "2025-12-14"}.issubset(optin_dates)

    request_items = build_missing_artifacts_list(
        coverage_report,
        include_partial=True,
        focus_show_dates=(date(2025, 12, 12), date(2025, 12, 14)),
    )
    assert request_items
    dates = {item.dia.isoformat() for item in request_items}
    assert dates == {"2025-12-12", "2025-12-14"}
    datasets = {item.dataset for item in request_items}
    assert {"access_control", "ticket_sales", "optin"}.issubset(datasets)

    request_md = render_missing_artifacts_markdown(request_items)
    assert "| dia | sessao | dataset | artefato_esperado | justificativa |" in request_md
    assert "TMJ2025_20251212_SHOW" in request_md
    assert "TMJ2025_20251214_SHOW" in request_md

    request_csv = render_missing_artifacts_csv(request_items)
    parsed = list(csv.DictReader(io.StringIO(request_csv)))
    assert parsed
    assert {"dia", "sessao", "dataset", "artefato_esperado", "justificativa"} == set(
        parsed[0].keys()
    )

