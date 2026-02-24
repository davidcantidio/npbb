"""Integration-oriented tests for health, coverage and alert observability."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.dq_results import DQCheckResult  # noqa: E402
from app.models.etl_lineage import LineageLocationType, LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from app.models.models import EventSession, EventSessionType, Source as LegacySource  # noqa: E402
from app.services.etl_health_queries import (  # noqa: E402
    list_source_health_status,
    source_health_rows_to_dicts,
    source_health_summary_to_dict,
    summarize_source_health,
)
from etl.validate.alerts import alerts_to_dicts, generate_alerts  # noqa: E402
from etl.validate.coverage_matrix import build_coverage_matrix_payload  # noqa: E402


def _make_engine():
    """Create in-memory engine for observability integration tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create the minimal table set used by health/coverage/alerts tests."""

    SQLModel.metadata.create_all(
        engine,
        tables=[
            LegacySource.__table__,
            EventSession.__table__,
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            DQCheckResult.__table__,
        ],
    )

    metadata = sa.MetaData()
    sa.Table(
        "stg_access_control_sessions",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
    )
    sa.Table(
        "stg_optin_transactions",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
    )
    metadata.create_all(engine)


def _seed_observability_data(engine) -> None:  # noqa: ANN001
    """Seed sources, runs and session coverage with one deliberate show-day gap."""

    show_12_id: int
    run_access_id: int
    run_optin_id: int
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

        src_access = Source(
            source_id="SRC_ACESSO_NOTURNO_DOZE",
            kind=SourceKind.PDF,
            uri="file:///tmp/access_12.pdf",
        )
        src_optin = Source(
            source_id="SRC_OPTIN_NOTURNO_DOZE",
            kind=SourceKind.XLSX,
            uri="file:///tmp/optin_12.xlsx",
        )
        src_sales_partial = Source(
            source_id="SRC_VENDAS_NOTURNO_DOZE",
            kind=SourceKind.CSV,
            uri="file:///tmp/sales_12.csv",
        )
        session.add(src_access)
        session.add(src_optin)
        session.add(src_sales_partial)
        session.commit()
        session.refresh(src_access)
        session.refresh(src_optin)
        session.refresh(src_sales_partial)

        run_access = IngestionRun(source_pk=src_access.id, status=IngestionStatus.SUCCESS)
        run_optin = IngestionRun(source_pk=src_optin.id, status=IngestionStatus.SUCCESS)
        run_sales_partial = IngestionRun(
            source_pk=src_sales_partial.id,
            status=IngestionStatus.PARTIAL,
            notes="Arquivo de vendas incompleto",
        )
        session.add(run_access)
        session.add(run_optin)
        session.add(run_sales_partial)
        session.commit()
        session.refresh(run_access)
        session.refresh(run_optin)
        run_access_id = int(run_access.id)
        run_optin_id = int(run_optin.id)
        show_12_id = int(show_12.id)

        lineage_access = LineageRef(
            source_id=src_access.source_id,
            ingestion_id=run_access.id,
            location_type=LineageLocationType.PAGE,
            location_value="page:1",
            evidence_text="Tabela de acesso show 12/12",
        )
        lineage_optin = LineageRef(
            source_id=src_optin.source_id,
            ingestion_id=run_optin.id,
            location_type=LineageLocationType.SHEET,
            location_value="sheet:OptIn",
            evidence_text="Planilha opt-in show 12/12",
        )
        session.add(lineage_access)
        session.add(lineage_optin)
        session.commit()
        session.refresh(lineage_access)
        session.refresh(lineage_optin)

    with engine.begin() as conn:
        stg_access = sa.Table("stg_access_control_sessions", sa.MetaData(), autoload_with=engine)
        stg_optin = sa.Table("stg_optin_transactions", sa.MetaData(), autoload_with=engine)
        conn.execute(
            stg_access.insert(),
            [
                {
                    "id": 1,
                    "source_id": "SRC_ACESSO_NOTURNO_DOZE",
                    "ingestion_id": run_access_id,
                    "event_id": 1,
                    "session_id": show_12_id,
                }
            ],
        )
        conn.execute(
            stg_optin.insert(),
            [
                {
                    "id": 1,
                    "source_id": "SRC_OPTIN_NOTURNO_DOZE",
                    "ingestion_id": run_optin_id,
                    "event_id": 1,
                    "session_id": show_12_id,
                }
            ],
        )


def test_observability_alerts_highlight_partial_and_show_day_gap() -> None:
    """Pipeline should emit warning for partial run and critical show-day gap."""

    engine = _make_engine()
    _create_required_tables(engine)
    _seed_observability_data(engine)

    with Session(engine) as session:
        health_rows = list_source_health_status(session)
        health_payload = {
            "summary": source_health_summary_to_dict(summarize_source_health(health_rows)),
            "items": source_health_rows_to_dicts(health_rows),
        }
        coverage_payload = build_coverage_matrix_payload(session, event_id=1)

    alerts = alerts_to_dicts(generate_alerts(health_payload, coverage_payload))
    by_code = {item["code"]: item for item in alerts}

    assert health_payload["summary"]["partial_sources"] >= 1
    assert coverage_payload["summary"]["gap_sessions"] >= 1

    assert "ALERT_PARTIAL_INGESTION" in by_code
    assert by_code["ALERT_PARTIAL_INGESTION"]["severity"] == "warning"
    assert "status parcial" in by_code["ALERT_PARTIAL_INGESTION"]["message"].lower()

    assert "ALERT_MISSING_REQUIRED_DATASET" in by_code
    assert by_code["ALERT_MISSING_REQUIRED_DATASET"]["severity"] == "critical"
    assert "show por dia" in by_code["ALERT_MISSING_REQUIRED_DATASET"]["message"].lower()
    assert by_code["ALERT_MISSING_REQUIRED_DATASET"]["session_key"] == "TMJ2025_20251214_SHOW"


def test_observability_alert_messages_include_minimum_actionable_fields() -> None:
    """Every generated alert should carry severity, message and action guidance."""

    health_payload = {
        "items": [
            {
                "source_id": "SRC_X",
                "latest_ingestion_id": 7,
                "latest_status": "partial",
                "health_status": "partial",
            }
        ]
    }
    coverage_payload = {
        "sessions": [
            {
                "session_id": 77,
                "session_key": "TMJ2025_20251212_SHOW",
                "session_date": "2025-12-12",
                "session_type": "NOTURNO_SHOW",
                "status": "gap",
                "missing_datasets": ["ticket_sales"],
            }
        ],
        "matrix": [],
        "unresolved_without_session": {"optin": 2},
    }

    alerts = alerts_to_dicts(generate_alerts(health_payload, coverage_payload))
    assert alerts
    for item in alerts:
        assert item["severity"] in {"critical", "warning", "info"}
        assert item["title"]
        assert item["message"]
        assert item["recommended_action"]
