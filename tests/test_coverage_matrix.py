"""Tests for coverage matrix by session type and required datasets."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
from textwrap import dedent

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
from app.models.stg_leads import StgLead  # noqa: E402
from app.models.stg_optin import StgOptinTransaction  # noqa: E402
from etl.validate.coverage_matrix import (  # noqa: E402
    build_coverage_matrix,
    build_coverage_matrix_payload,
    build_coverage_matrix_summary,
    load_coverage_requirements_config,
    required_datasets_for_session_type,
)


def _make_engine():
    """Create in-memory SQLite engine for coverage-matrix tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimum schema required by coverage matrix tests."""

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
            StgLead.__table__,
        ],
    )


def _seed_matrix_data(engine) -> None:  # noqa: ANN001
    """Seed session/source/staging data to exercise required-dataset matrix logic."""

    with Session(engine) as session:
        sess_show = EventSession(
            event_id=None,
            session_key="TMJ2025_20251212_SHOW",
            session_name="Show 12/12",
            session_type=EventSessionType.NOTURNO_SHOW,
            session_date=date(2025, 12, 12),
        )
        sess_day = EventSession(
            event_id=None,
            session_key="TMJ2025_20251212_DAY",
            session_name="Diurno 12/12",
            session_type=EventSessionType.DIURNO_GRATUITO,
            session_date=date(2025, 12, 12),
        )
        session.add(sess_show)
        session.add(sess_day)
        session.commit()
        session.refresh(sess_show)
        session.refresh(sess_day)

        src_access_show = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/access_show.pdf",
        )
        src_optin_show = Source(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_show.xlsx",
        )
        src_sales_show = Source(
            source_id="SRC_VENDAS_NOTURNO_DOZE",
            kind=SourceKind.CSV,
            uri="file:///tmp/sales_show.csv",
        )
        src_leads_day = Source(
            source_id="SRC_LEADS_DIURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/leads_day.xlsx",
        )
        session.add(src_access_show)
        session.add(src_optin_show)
        session.add(src_sales_show)
        session.add(src_leads_day)
        session.commit()
        session.refresh(src_access_show)
        session.refresh(src_optin_show)
        session.refresh(src_sales_show)
        session.refresh(src_leads_day)

        run_access = IngestionRun(source_pk=src_access_show.id, status=IngestionStatus.SUCCESS)
        run_optin = IngestionRun(source_pk=src_optin_show.id, status=IngestionStatus.SUCCESS)
        run_sales = IngestionRun(source_pk=src_sales_show.id, status=IngestionStatus.PARTIAL)
        run_leads = IngestionRun(source_pk=src_leads_day.id, status=IngestionStatus.SUCCESS)
        session.add(run_access)
        session.add(run_optin)
        session.add(run_sales)
        session.add(run_leads)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_optin)
        session.refresh(run_sales)
        session.refresh(run_leads)

        lineage_access = LineageRef(
            source_id=src_access_show.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela acesso show",
        )
        lineage_optin = LineageRef(
            source_id=src_optin_show.source_id,
            ingestion_id=run_optin.id,
            location_type=LineageLocationType.SHEET,
            location_value="sheet:OptIn",
            evidence_text="Planilha optin show",
        )
        lineage_leads = LineageRef(
            source_id=src_leads_day.source_id,
            ingestion_id=run_leads.id,
            location_type=LineageLocationType.SHEET,
            location_value="sheet:Leads",
            evidence_text="Planilha leads diurno",
        )
        session.add(lineage_access)
        session.add(lineage_optin)
        session.add(lineage_leads)
        session.commit()
        session.refresh(lineage_access)
        session.refresh(lineage_optin)
        session.refresh(lineage_leads)

        session.add(
            StgAccessControlSession(
                source_id=src_access_show.source_id,
                ingestion_id=run_access.id,
                lineage_ref_id=int(lineage_access.id),
                session_id=int(sess_show.id),
                pdf_page=1,
                session_name="Show 12/12",
                raw_payload_json="{}",
            )
        )
        session.add(
            StgOptinTransaction(
                source_id=src_optin_show.source_id,
                ingestion_id=run_optin.id,
                lineage_ref_id=int(lineage_optin.id),
                session_id=int(sess_show.id),
                sheet_name="OptIn",
                header_row=4,
                row_number=1,
                source_range="A6:I6",
                raw_payload_json="{}",
            )
        )
        session.add(
            StgLead(
                source_id=src_leads_day.source_id,
                ingestion_id=run_leads.id,
                lineage_ref_id=int(lineage_leads.id),
                sheet_name="Leads",
                header_row=2,
                row_number=1,
                source_range="A2:H2",
                raw_payload_json="{}",
                session_id=int(sess_day.id),
            )
        )
        session.commit()


def test_load_coverage_requirements_config_and_required_dataset_resolution(tmp_path: Path) -> None:
    """Loader should parse session-type requirements and resolve fallbacks."""

    path = tmp_path / "datasets.yml"
    path.write_text(
        dedent(
            """
            datasets: []
            coverage_requirements:
              default_required_datasets:
                - access_control
              required_datasets_by_session_type:
                NOTURNO_SHOW:
                  - access_control
                  - ticket_sales
                DIURNO_GRATUITO:
                  - access_control
                  - leads
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    config = load_coverage_requirements_config(path)
    noturno = required_datasets_for_session_type(EventSessionType.NOTURNO_SHOW, config)
    diurno = required_datasets_for_session_type(EventSessionType.DIURNO_GRATUITO, config)
    outro = required_datasets_for_session_type(EventSessionType.OUTRO, config)

    assert noturno == (CoverageDataset.ACCESS_CONTROL, CoverageDataset.TICKET_SALES)
    assert diurno == (CoverageDataset.ACCESS_CONTROL, CoverageDataset.LEADS)
    assert outro == (CoverageDataset.ACCESS_CONTROL,)


def test_build_coverage_matrix_by_session_type_and_payload_contract() -> None:
    """Matrix should honor required datasets per session type and expose GAP/PARTIAL."""

    engine = _make_engine()
    _create_required_tables(engine)
    _seed_matrix_data(engine)

    with Session(engine) as session:
        rows = build_coverage_matrix(session)
        summary_rows = build_coverage_matrix_summary(rows)
        payload = build_coverage_matrix_payload(session)

    assert len(rows) == 5
    by_cell = {(row.session_key, row.dataset.value): row for row in rows}

    assert by_cell[("TMJ2025_20251212_SHOW", "access_control")].matrix_status == "ok"
    assert by_cell[("TMJ2025_20251212_SHOW", "optin")].matrix_status == "ok"
    assert by_cell[("TMJ2025_20251212_SHOW", "ticket_sales")].matrix_status == "partial"

    assert by_cell[("TMJ2025_20251212_DAY", "leads")].matrix_status == "ok"
    assert by_cell[("TMJ2025_20251212_DAY", "access_control")].matrix_status == "gap"

    summary_by_key = {row.session_key: row for row in summary_rows}
    assert summary_by_key["TMJ2025_20251212_SHOW"].status == "partial"
    assert summary_by_key["TMJ2025_20251212_DAY"].status == "gap"

    assert payload["status"] == "ok"
    assert payload["summary"]["total_sessions"] == 2
    assert payload["summary"]["partial_sessions"] == 1
    assert payload["summary"]["gap_sessions"] == 1
    assert isinstance(payload["matrix"], list)
    assert isinstance(payload["sessions"], list)


def test_build_coverage_matrix_payload_skips_when_event_sessions_table_is_missing() -> None:
    """Payload builder should return skipped status when event_sessions is unavailable."""

    engine = _make_engine()
    with Session(engine) as session:
        payload = build_coverage_matrix_payload(session)

    assert payload["status"] == "skipped"
    assert payload["summary"]["total_sessions"] == 0
    assert payload["matrix"] == []
    assert payload["sessions"] == []

