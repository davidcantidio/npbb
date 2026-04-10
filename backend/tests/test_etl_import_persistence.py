from __future__ import annotations

from sqlmodel import Session, select

from app.models.models import Lead
from app.modules.leads_publicidade.application.etl_import import persistence
from app.modules.leads_publicidade.application.etl_import.persistence import (
    LeadBatchPersistenceResult,
    persist_lead_batch,
)


def _lead_payload(email: str, cpf: str, nome: str) -> dict[str, object]:
    return {
        "email": email,
        "cpf": cpf,
        "nome": nome,
        "evento_nome": "Evento Persistencia",
        "sessao": "Sessao A",
    }


def test_persist_lead_batch_bulk_result_is_structured_and_tuple_compatible(
    db_session: Session,
) -> None:
    result = persist_lead_batch(
        db_session,
        [(_lead_payload("bulk@example.com", "10000000001", "Lead Bulk"), 2)],
    )

    assert isinstance(result, LeadBatchPersistenceResult)
    assert result.created == 1
    assert result.updated == 0
    assert result.imported_count == 1
    assert result.failed_rows == []
    assert tuple(result) == (1, 0, 0, False)

    leads = db_session.exec(select(Lead)).all()
    assert [lead.email for lead in leads] == ["bulk@example.com"]


def test_persist_lead_batch_fallback_tracks_failed_rows_without_losing_successes(
    db_session: Session,
    monkeypatch,
) -> None:
    def fail_selected_row(session, *, lead, payload):
        _ = session, lead
        if payload.get("nome") == "Lead Falha":
            raise ValueError("falha controlada")

    monkeypatch.setattr(persistence, "_ensure_canonical_event_link", fail_selected_row)

    result = persist_lead_batch(
        db_session,
        [
            (_lead_payload("ok-1@example.com", "10000000001", "Lead OK 1"), 2),
            (_lead_payload("fail@example.com", "10000000002", "Lead Falha"), 3),
            (_lead_payload("ok-2@example.com", "10000000003", "Lead OK 2"), 4),
        ],
    )

    assert result.created == 2
    assert result.updated == 0
    assert result.imported_count == 2
    assert result.skipped == 1
    assert result.has_errors is True
    assert [(row.row_index, row.reason) for row in result.failed_rows] == [
        (3, "ValueError: falha controlada")
    ]
    assert tuple(result) == (2, 0, 1, True)

    emails = db_session.exec(select(Lead.email).order_by(Lead.email)).all()
    assert emails == ["ok-1@example.com", "ok-2@example.com"]


def test_persist_lead_batch_total_failure_reports_failed_rows(
    db_session: Session,
    monkeypatch,
) -> None:
    def fail_all_rows(session, *, lead, payload):
        _ = session, lead, payload
        raise ValueError("falha total")

    monkeypatch.setattr(persistence, "_ensure_canonical_event_link", fail_all_rows)

    result = persist_lead_batch(
        db_session,
        [(_lead_payload("fail-all@example.com", "10000000001", "Lead Falha"), 2)],
    )

    assert result.imported_count == 0
    assert result.skipped == 1
    assert result.has_errors is True
    assert [(row.row_index, row.reason) for row in result.failed_rows] == [
        (2, "ValueError: falha total")
    ]
    assert tuple(result) == (0, 0, 1, True)
    assert db_session.exec(select(Lead)).all() == []


def test_persist_lead_batch_commit_failure_reports_all_attempted_rows(
    db_session: Session,
    monkeypatch,
) -> None:
    def fail_commit() -> None:
        raise RuntimeError("commit falhou")

    monkeypatch.setattr(db_session, "commit", fail_commit)

    result = persist_lead_batch(
        db_session,
        [
            (_lead_payload("commit-1@example.com", "10000000001", "Lead Commit 1"), 2),
            (_lead_payload("commit-2@example.com", "10000000002", "Lead Commit 2"), 3),
        ],
    )

    assert result.imported_count == 0
    assert result.skipped == 2
    assert result.has_errors is True
    assert [(row.row_index, row.reason) for row in result.failed_rows] == [
        (2, "RuntimeError: commit falhou"),
        (3, "RuntimeError: commit falhou"),
    ]
    assert db_session.exec(select(Lead)).all() == []


def test_persist_lead_batch_empty_or_filtered_batch_is_noop(db_session: Session) -> None:
    result = persist_lead_batch(db_session, [None])

    assert result.imported_count == 0
    assert result.failed_rows == []
    assert result.skipped == 0
    assert result.has_errors is False
    assert tuple(result) == (0, 0, 0, False)
