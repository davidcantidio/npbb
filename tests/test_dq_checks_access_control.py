"""Unit tests for access-control reconciliation data-quality check."""

from __future__ import annotations

from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from etl.validate.checks_access_control import AccessControlReconciliationCheck
from etl.validate.framework import CheckContext, CheckStatus, Severity


def _make_engine():
    """Create isolated in-memory SQLite engine for check tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_attendance_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic attendance table compatible with reconciliation check.

    Args:
        engine: SQLAlchemy engine used by tests.

    Returns:
        SQLAlchemy table object.
    """

    metadata = sa.MetaData()
    table = sa.Table(
        "attendance_access_control",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.String(160), nullable=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("ingressos_validos", sa.Numeric(20, 6), nullable=True),
        sa.Column("presentes", sa.Numeric(20, 6), nullable=True),
        sa.Column("ausentes", sa.Numeric(20, 6), nullable=True),
        sa.Column("comparecimento_pct", sa.Numeric(20, 6), nullable=True),
    )
    metadata.create_all(engine)
    return table


def test_access_control_reconciliation_passes_for_consistent_rows() -> None:
    """Check should pass when validos/presentes/ausentes and comparecimento reconcile."""

    engine = _make_engine()
    table = _create_attendance_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "session_id": 1201,
                    "source_id": "SRC_ACCESS_12",
                    "ingestion_id": 501,
                    "lineage_ref_id": 9001,
                    "ingressos_validos": Decimal("100"),
                    "presentes": Decimal("80"),
                    "ausentes": Decimal("20"),
                    "comparecimento_pct": Decimal("0.80"),
                },
                {
                    "id": 2,
                    "session_id": 1202,
                    "source_id": "SRC_ACCESS_13",
                    "ingestion_id": 501,
                    "lineage_ref_id": 9002,
                    "ingressos_validos": Decimal("200"),
                    "presentes": Decimal("150"),
                    "ausentes": Decimal("50"),
                    "comparecimento_pct": Decimal("75"),
                },
            ],
        )

    with Session(engine) as session:
        result = AccessControlReconciliationCheck().run(
            CheckContext(ingestion_id=501, resources={"session": session})
        )

    assert result.status == CheckStatus.PASS
    assert result.severity == Severity.INFO
    assert result.evidence["finding_count"] == 0
    assert result.evidence["evaluated_rows"] == 2


def test_access_control_reconciliation_detects_inconsistency_with_session_evidence() -> None:
    """Check should fail and emit sample findings including session and lineage ids."""

    engine = _make_engine()
    table = _create_attendance_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "session_id": 1301,
                    "source_id": "SRC_ACCESS_14",
                    "ingestion_id": 777,
                    "lineage_ref_id": 9101,
                    "ingressos_validos": Decimal("100"),
                    "presentes": Decimal("120"),
                    "ausentes": Decimal("0"),
                    "comparecimento_pct": Decimal("1.20"),
                }
            ],
        )

    with Session(engine) as session:
        result = AccessControlReconciliationCheck(sample_limit=5).run(
            CheckContext(ingestion_id=777, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["finding_count"] >= 1
    sample = result.evidence["findings_sample"][0]
    assert sample["session_id"] == 1301
    assert sample["lineage_ref_id"] == 9101
    assert result.lineage["source_id"] == "SRC_ACCESS_14"
    assert result.lineage["lineage_ref_id"] == 9101


def test_access_control_reconciliation_flags_comparecimento_out_of_bounds() -> None:
    """Check should fail when comparecimento_pct is outside [0, 100]."""

    engine = _make_engine()
    table = _create_attendance_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "session_id": 1401,
                    "source_id": "SRC_ACCESS_15",
                    "ingestion_id": 888,
                    "lineage_ref_id": 9201,
                    "ingressos_validos": Decimal("100"),
                    "presentes": Decimal("80"),
                    "ausentes": Decimal("20"),
                    "comparecimento_pct": Decimal("120.5"),
                }
            ],
        )

    with Session(engine) as session:
        result = AccessControlReconciliationCheck().run(
            CheckContext(ingestion_id=888, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert any(item["code"] == "COMPARECIMENTO_FORA_BOUNDS" for item in result.evidence["findings_sample"])


def test_access_control_reconciliation_skips_for_partial_source_without_required_fields() -> None:
    """Check should skip when rows do not provide enough fields for reconciliation."""

    engine = _make_engine()
    table = _create_attendance_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "session_id": 1501,
                    "source_id": "SRC_ACCESS_PARTIAL",
                    "ingestion_id": 999,
                    "lineage_ref_id": 9301,
                    "ingressos_validos": None,
                    "presentes": None,
                    "ausentes": None,
                    "comparecimento_pct": None,
                }
            ],
        )

    with Session(engine) as session:
        result = AccessControlReconciliationCheck().run(
            CheckContext(ingestion_id=999, resources={"session": session})
        )

    assert result.status == CheckStatus.SKIP
    assert result.severity == Severity.INFO
    assert result.evidence["evaluated_rows"] == 0
    assert result.evidence["partial_rows"] == 1
