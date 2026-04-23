from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.lead_public_models import LeadEventoSourceKind
from app.models.models import Evento, Lead, LeadEvento, StatusEvento
from app.modules.lead_imports.application.etl_import import persistence
from app.modules.lead_imports.application.etl_import.persistence import (
    LeadBatchPersistenceResult,
    LeadLookupContext,
    build_dedupe_key,
    find_existing_lead,
    find_lead_by_ticketing_dedupe_key,
    is_ticketing_dedupe_integrity_error,
    merge_lead_lookup_context,
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


def _seed_evento(db_session: Session, *, nome: str = "Evento Persistencia Canonico") -> Evento:
    status = db_session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    if status is None:
        status = StatusEvento(nome="Previsto")
        db_session.add(status)
        db_session.commit()
        db_session.refresh(status)

    evento = Evento(
        nome=nome,
        cidade="Brasilia",
        estado="DF",
        status_id=status.id,
    )
    db_session.add(evento)
    db_session.commit()
    db_session.refresh(evento)
    return evento


def test_build_dedupe_key_prefers_canonical_evento_id_over_event_name() -> None:
    payload = _lead_payload("canonical@example.com", "52998224725", "Lead Canonico")
    renamed_payload = {**payload, "evento_nome": "Evento Renomeado"}

    assert build_dedupe_key(payload, canonical_evento_id=101) == build_dedupe_key(
        renamed_payload,
        canonical_evento_id=101,
    )
    assert build_dedupe_key(payload, canonical_evento_id=101) != build_dedupe_key(
        renamed_payload,
        canonical_evento_id=202,
    )


def test_persist_lead_batch_bulk_result_is_structured_and_tuple_compatible(
    db_session: Session,
) -> None:
    assert db_session.exec(select(Lead)).all() == []

    result = persist_lead_batch(
        db_session,
        [(_lead_payload("bulk@example.com", "10000000019", "Lead Bulk"), 2)],
    )

    assert isinstance(result, LeadBatchPersistenceResult)
    assert result.created == 1
    assert result.updated == 0
    assert result.imported_count == 1
    assert result.failed_rows == []
    assert tuple(result) == (1, 0, 0, False)

    leads = db_session.exec(select(Lead)).all()
    assert [lead.email for lead in leads] == ["bulk@example.com"]


def test_find_lead_by_ticketing_dedupe_key_treats_blank_cpf_as_missing(
    db_session: Session,
) -> None:
    db_session.add(
        Lead(
            id_salesforce="blank-cpf-existing",
            email="blank-cpf@example.com",
            cpf="",
            nome="Lead Blank CPF",
            evento_nome="Evento Persistencia",
            sessao="Sessao A",
        )
    )
    db_session.commit()

    winner = find_lead_by_ticketing_dedupe_key(
        db_session,
        {
            "email": "blank-cpf@example.com",
            "cpf": "   ",
            "evento_nome": "Evento Persistencia",
            "sessao": "Sessao A",
        },
    )

    assert winner is None


def test_is_ticketing_dedupe_integrity_error_rejects_id_salesforce_unique_violation(
    db_session: Session,
) -> None:
    db_session.add(
        Lead(
            id_salesforce="sf-duplicate",
            email="primeiro@example.com",
            cpf="52998224725",
            nome="Lead 1",
            evento_nome="Evento Persistencia",
            sessao="Sessao A",
        )
    )
    db_session.commit()

    db_session.add(
        Lead(
            id_salesforce="sf-duplicate",
            email="segundo@example.com",
            cpf="39053344705",
            nome="Lead 2",
            evento_nome="Outro Evento",
            sessao="Sessao B",
        )
    )
    with pytest.raises(IntegrityError) as exc_info:
        db_session.commit()
    db_session.rollback()

    assert is_ticketing_dedupe_integrity_error(exc_info.value) is False


def test_persist_lead_batch_fallback_tracks_failed_rows_without_losing_successes(
    db_session: Session,
    monkeypatch,
) -> None:
    def fail_selected_row(session, *, lead, payload, canonical_evento_id=None):
        _ = session, lead
        if payload.get("nome") == "Lead Falha":
            raise ValueError("falha controlada")

    monkeypatch.setattr(persistence, "_ensure_canonical_event_link", fail_selected_row)

    result = persist_lead_batch(
        db_session,
        [
            (_lead_payload("ok-1@example.com", "10000000019", "Lead OK 1"), 2),
            (_lead_payload("fail@example.com", "10000000108", "Lead Falha"), 3),
            (_lead_payload("ok-2@example.com", "10000000280", "Lead OK 2"), 4),
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
    def fail_all_rows(session, *, lead, payload, canonical_evento_id=None):
        _ = session, lead, payload
        raise ValueError("falha total")

    monkeypatch.setattr(persistence, "_ensure_canonical_event_link", fail_all_rows)

    result = persist_lead_batch(
        db_session,
        [(_lead_payload("fail-all@example.com", "10000000019", "Lead Falha"), 2)],
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
            (_lead_payload("commit-1@example.com", "10000000019", "Lead Commit 1"), 2),
            (_lead_payload("commit-2@example.com", "10000000108", "Lead Commit 2"), 3),
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


def test_persist_lead_batch_validation_failures_are_reported_without_losing_successes(
    db_session: Session,
) -> None:
    result = persist_lead_batch(
        db_session,
        [
            (_lead_payload("ok@example.com", "52998224725", "Lead OK"), 2),
            (_lead_payload("bad-email", "11144477735", "Lead Email Invalido"), 3),
            (_lead_payload("bad-cpf@example.com", "12345678901", "Lead CPF Invalido"), 4),
            (_lead_payload("bad email", "11111111111", "Lead Ambos Invalidos"), 5),
        ],
    )

    assert result.created == 1
    assert result.updated == 0
    assert result.imported_count == 1
    assert result.skipped == 3
    assert result.has_errors is True
    assert [(row.row_index, row.reason) for row in result.failed_rows] == [
        (3, "email malformado"),
        (4, "CPF inválido"),
        (5, "email malformado; CPF inválido"),
    ]
    assert tuple(result) == (1, 0, 3, True)

    leads = db_session.exec(select(Lead)).all()
    assert [(lead.email, lead.cpf) for lead in leads] == [
        ("ok@example.com", "52998224725")
    ]


def test_persist_lead_batch_validation_failure_only_does_not_persist(
    db_session: Session,
) -> None:
    result = persist_lead_batch(
        db_session,
        [(_lead_payload("bad-cpf@example.com", "11111111111", "Lead CPF Invalido"), 2)],
    )

    assert result.imported_count == 0
    assert result.skipped == 1
    assert result.has_errors is True
    assert [(row.row_index, row.reason) for row in result.failed_rows] == [
        (2, "CPF inválido")
    ]
    assert tuple(result) == (0, 0, 1, True)
    assert db_session.exec(select(Lead)).all() == []


def test_persist_lead_batch_empty_or_filtered_batch_is_noop(db_session: Session) -> None:
    result = persist_lead_batch(db_session, [None])

    assert result.imported_count == 0
    assert result.failed_rows == []
    assert result.skipped == 0
    assert result.has_errors is False
    assert tuple(result) == (0, 0, 0, False)


def test_persist_lead_batch_links_canonical_event_by_explicit_evento_id_even_with_stale_name(
    db_session: Session,
) -> None:
    evento = _seed_evento(db_session, nome="Evento Atual")
    payload = _lead_payload("evento-id@example.com", "52998224725", "Lead Evento ID")
    payload["evento_nome"] = "Evento Antigo Ou Ambiguo"

    result = persist_lead_batch(
        db_session,
        [(payload, 2)],
        canonical_evento_id=evento.id,
    )

    assert result.created == 1
    lead = db_session.exec(select(Lead).where(Lead.email == "evento-id@example.com")).first()
    assert lead is not None
    assert lead.evento_nome == "Evento Atual"

    lead_eventos = db_session.exec(select(LeadEvento).where(LeadEvento.lead_id == lead.id)).all()
    assert len(lead_eventos) == 1
    assert lead_eventos[0].evento_id == evento.id
    assert lead_eventos[0].source_kind == LeadEventoSourceKind.EVENT_DIRECT


def test_persist_lead_batch_corrige_evento_nome_contaminado_em_lead_existente_com_evento_canonico(
    db_session: Session,
) -> None:
    evento = _seed_evento(db_session, nome="Evento Corrigido")
    existing = Lead(
        email="contaminated@example.com",
        cpf="52998224725",
        nome="Lead Contaminado",
        evento_nome="Ativação",
        sessao="Sessao A",
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    db_session.add(
        LeadEvento(
            lead_id=int(existing.id),
            evento_id=int(evento.id),
            source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        )
    )
    db_session.commit()

    payload = _lead_payload("contaminated@example.com", "52998224725", "Lead Atualizado")
    payload["evento_nome"] = "Proponente"

    result = persist_lead_batch(
        db_session,
        [(payload, 2)],
        canonical_evento_id=int(evento.id),
    )

    assert result.created == 0
    assert result.updated == 1

    lead = db_session.exec(select(Lead).where(Lead.email == "contaminated@example.com")).first()
    assert lead is not None
    assert lead.evento_nome == "Evento Corrigido"


def test_find_existing_lead_ignores_homonymous_lead_from_other_canonical_event(
    db_session: Session,
) -> None:
    evento = _seed_evento(db_session, nome="Evento Homonimo Persistencia")
    outro_evento = _seed_evento(db_session, nome="Evento Homonimo Persistencia")
    lead = Lead(
        email="homonimo@example.com",
        cpf="52998224725",
        nome="Lead Homonimo",
        evento_nome="Evento Homonimo Persistencia",
        sessao="Sessao A",
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    db_session.add(
        LeadEvento(
            lead_id=lead.id,
            evento_id=outro_evento.id,
            source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        )
    )
    db_session.commit()

    payload = _lead_payload("homonimo@example.com", "52998224725", "Lead Homonimo")
    payload["evento_nome"] = "Evento Homonimo Persistencia"

    assert find_existing_lead(db_session, payload, canonical_evento_id=evento.id) is None

    matched = find_existing_lead(
        db_session,
        payload,
        canonical_evento_id=outro_evento.id,
    )
    assert matched is not None
    assert matched.id == lead.id


def test_persist_lead_batch_preserves_filled_fields_on_reimport_after_event_rename(
    db_session: Session,
) -> None:
    evento = _seed_evento(db_session, nome="Evento Persistencia Antigo")
    existing = Lead(
        email="rename-existing@example.com",
        cpf="52998224725",
        nome="Lead Antigo",
        evento_nome="Evento Persistencia Antigo",
        sessao="Sessao A",
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)
    existing_id = existing.id

    db_session.add(
        LeadEvento(
            lead_id=existing_id,
            evento_id=evento.id,
            source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        )
    )
    db_session.commit()

    payload = _lead_payload("rename-existing@example.com", "52998224725", "Lead Atualizado")
    payload["evento_nome"] = "Evento Persistencia Renomeado"

    result = persist_lead_batch(
        db_session,
        [(payload, 2)],
        canonical_evento_id=evento.id,
    )

    assert result.created == 0
    assert result.updated == 1

    leads = db_session.exec(select(Lead).where(Lead.email == "rename-existing@example.com")).all()
    assert len(leads) == 1
    assert leads[0].id == existing_id
    assert leads[0].nome == "Lead Antigo"
    assert leads[0].evento_nome == "Evento Persistencia Antigo"

    lead_eventos = db_session.exec(select(LeadEvento).where(LeadEvento.lead_id == existing_id)).all()
    assert len(lead_eventos) == 1
    assert lead_eventos[0].evento_id == evento.id


def test_merge_lead_lookup_context_deduplicates_lead_ids() -> None:
    class _StubLead:
        def __init__(self, lead_id: int) -> None:
            self.id = lead_id

    a = _StubLead(1)
    b = _StubLead(2)
    acc = LeadLookupContext([a], {1}, set())
    inc = LeadLookupContext([a, b], {2}, {2})
    merge_lead_lookup_context(acc, inc)
    assert [getattr(x, "id") for x in acc.candidates] == [1, 2]
    assert acc.lead_ids_with_any_event_link == {1, 2}
    assert acc.lead_ids_with_target_event_link == {2}
