"""Tests for canonical audience fact models (attendance/sales/opt-in)."""

from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.models.etl_lineage import LineageRef
from app.models.etl_registry import IngestionRun, Source
from app.models.events_sessions import Event, EventSession
from app.models.fct_attendance_access_control import FctAttendanceAccessControl
from app.models.fct_optin_transactions import FctOptinTransaction
from app.models.fct_ticket_sales import FctTicketSales


def _make_engine():
    """Create isolated in-memory SQLite engine for audience fact tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_fct_tables_define_expected_names_and_core_columns() -> None:
    """Fact models should expose controlled table names and required ruler columns."""

    assert FctAttendanceAccessControl.__tablename__ == "attendance_access_control"
    assert FctTicketSales.__tablename__ == "ticket_sales"
    assert FctOptinTransaction.__tablename__ == "optin_transactions"

    att_cols = set(FctAttendanceAccessControl.__table__.columns.keys())
    sales_cols = set(FctTicketSales.__table__.columns.keys())
    optin_cols = set(FctOptinTransaction.__table__.columns.keys())

    assert {"session_id", "ingestion_id", "lineage_ref_id"} <= att_cols
    assert {"ingressos_validos", "presentes", "ausentes"} <= att_cols

    assert {"session_id", "ingestion_id", "lineage_ref_id"} <= sales_cols
    assert {"sold_total"} <= sales_cols

    assert {"session_id", "ingestion_id", "lineage_ref_id"} <= optin_cols
    assert {"optin_flag", "qty"} <= optin_cols


def test_fct_tables_have_expected_foreign_keys_and_indexes() -> None:
    """Fact models should keep links to session/ingestion/lineage with indexes."""

    engine = _make_engine()
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Event.__table__,
            EventSession.__table__,
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            FctAttendanceAccessControl.__table__,
            FctTicketSales.__table__,
            FctOptinTransaction.__table__,
        ],
    )

    inspector = inspect(engine)

    for table_name in (
        "attendance_access_control",
        "ticket_sales",
        "optin_transactions",
    ):
        fk_targets = {
            f"{fk.column.table.name}.{fk.column.name}"
            for constraint in SQLModel.metadata.tables[table_name].foreign_key_constraints
            for fk in constraint.elements
        }
        assert "event_sessions.id" in fk_targets
        assert "ingestions.id" in fk_targets
        assert "lineage_refs.id" in fk_targets

        indexed_cols = {
            col
            for idx in inspector.get_indexes(table_name)
            for col in idx["column_names"]
        }
        assert "session_id" in indexed_cols
        assert "lineage_ref_id" in indexed_cols

