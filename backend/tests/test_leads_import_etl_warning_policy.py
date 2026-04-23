from __future__ import annotations

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.modules.lead_imports.application.etl_import.contracts import (
    EtlPreviewDQItem,
    EtlPreviewSnapshot,
)
from app.modules.lead_imports.application.etl_import.dq_report_policy import (
    compute_has_warnings,
)
from app.modules.lead_imports.application.etl_import.preview_session_repository import (
    create_snapshot,
    get_snapshot,
)


def _make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _dq_item(severity: str, affected_rows: int) -> EtlPreviewDQItem:
    return EtlPreviewDQItem(
        check_name=f"dq.test.{severity}.{affected_rows}",
        severity=severity,
        affected_rows=affected_rows,
    )


def test_compute_has_warnings_counts_warning_even_without_affected_rows() -> None:
    assert compute_has_warnings((_dq_item("warning", 0),)) is True


def test_compute_has_warnings_counts_warning_with_affected_rows() -> None:
    assert compute_has_warnings((_dq_item("warning", 2),)) is True


def test_compute_has_warnings_ignores_non_warning_severities() -> None:
    assert compute_has_warnings((_dq_item("info", 0), _dq_item("error", 1))) is False


def test_compute_has_warnings_returns_false_for_empty_report() -> None:
    assert compute_has_warnings(()) is False


def test_get_snapshot_preserves_warning_gate_for_zero_affected_rows() -> None:
    engine = _make_engine()
    SQLModel.metadata.create_all(engine)

    snapshot = EtlPreviewSnapshot(
        session_token="warning-zero-rows",
        filename="warning-zero-rows.xlsx",
        evento_id=1,
        evento_nome="Evento Warning",
        strict=False,
        total_rows=0,
        valid_rows=0,
        invalid_rows=0,
        approved_rows=(),
        rejected_rows=(),
        dq_report=(_dq_item("warning", 0),),
        status="previewed",
        idempotency_key="lead-etl-preview:warning-zero-rows",
        has_validation_errors=False,
        has_warnings=True,
    )

    with Session(engine) as session:
        create_snapshot(session, snapshot)
        persisted = get_snapshot(session, snapshot.session_token)

    assert persisted.dq_report == snapshot.dq_report
    assert persisted.has_warnings is True
