"""Tests for session coverage report generation (Markdown/JSON)."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from datetime import date

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import (  # noqa: E402
    CoverageDataset,
    IngestionRun,
    IngestionStatus,
    Source,
    SourceKind,
)
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.models.stg_access_control import StgAccessControlSession  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402
from etl.validate import session_coverage_report  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for report tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimum schema required by session coverage report tests."""
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


def _seed_report_data(engine) -> None:  # noqa: ANN001
    """Seed one fully observed session and one session with coverage gaps."""
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

        src_access = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/acesso_12.pdf",
        )
        src_optin = Source(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_12.xlsx",
        )
        src_orphan = Source(
            source_id="SRC_OPTIN_NOTURNO_TREZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_13.xlsx",
        )
        session.add(src_access)
        session.add(src_optin)
        session.add(src_orphan)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_optin)
        session.refresh(src_orphan)

        run_access = IngestionRun(
            source_pk=src_access.id,
            status=IngestionStatus.SUCCESS,
            extractor_name="extract_pdf_access",
        )
        run_optin = IngestionRun(
            source_pk=src_optin.id,
            status=IngestionStatus.SUCCESS,
            extractor_name="extract_xlsx_optin",
        )
        run_orphan = IngestionRun(
            source_pk=src_orphan.id,
            status=IngestionStatus.PARTIAL,
            extractor_name="extract_xlsx_optin",
        )
        session.add(run_access)
        session.add(run_optin)
        session.add(run_orphan)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_optin)
        session.refresh(run_orphan)

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
            evidence_text="Linha opt-in",
        )
        lineage_orphan = LineageRef(
            source_id=src_orphan.source_id,
            ingestion_id=run_orphan.id,
            location_type=LineageLocationType.RANGE,
            location_value="range:A7:I7",
            evidence_text="Linha sem sessao",
        )
        session.add(lineage_access)
        session.add(lineage_optin)
        session.add(lineage_orphan)
        session.commit()
        session.refresh(lineage_access)
        session.refresh(lineage_optin)
        session.refresh(lineage_orphan)

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
                source_id=src_orphan.source_id,
                ingestion_id=run_orphan.id,
                lineage_ref_id=int(lineage_orphan.id),
                session_id=None,
                sheet_name="OptIn",
                header_row=4,
                row_number=2,
                source_range="A7:I7",
                raw_payload_json="{}",
            )
        )
        session.commit()


def test_build_session_coverage_report_payload_is_consumable() -> None:
    """Report payload should expose session statuses and unresolved staging counts."""
    engine = _make_engine()
    _create_required_tables(engine)
    _seed_report_data(engine)

    with Session(engine) as session:
        payload = session_coverage_report.build_session_coverage_report_payload(
            session,
            expected_datasets=[CoverageDataset.ACCESS_CONTROL, CoverageDataset.OPTIN],
        )

    assert payload["summary"]["total_sessions"] == 2
    assert payload["summary"]["ok_sessions"] == 1
    assert payload["summary"]["gap_sessions"] == 1

    by_key = {row["session_key"]: row for row in payload["sessions"]}
    assert by_key["TMJ2025_20251212_SHOW"]["status"] == "ok"
    assert by_key["TMJ2025_20251213_SHOW"]["status"] == "gap"
    assert set(by_key["TMJ2025_20251213_SHOW"]["missing_datasets"]) == {
        "access_control",
        "optin",
    }
    assert payload["unresolved_without_session"]["optin"] == 1


def test_write_session_coverage_report_writes_markdown_and_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Writer should persist Markdown and JSON report artifacts."""
    engine = _make_engine()
    _create_required_tables(engine)
    _seed_report_data(engine)
    monkeypatch.setattr(session_coverage_report, "engine", engine)

    out_md = tmp_path / "coverage.md"
    out_json = tmp_path / "coverage.json"
    payload = session_coverage_report.write_session_coverage_report(
        out_md=out_md,
        out_json=out_json,
        expected_datasets=[CoverageDataset.ACCESS_CONTROL, CoverageDataset.OPTIN],
    )

    assert payload["summary"]["total_sessions"] == 2
    assert out_md.exists()
    assert out_json.exists()

    markdown = out_md.read_text(encoding="utf-8")
    assert "Session Coverage Report" in markdown
    assert "TMJ2025_20251213_SHOW" in markdown
    assert "access_control, optin" in markdown

    loaded_payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert loaded_payload["summary"]["gap_sessions"] == 1
