import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models.models import (
    Agencia,
    Ativacao,
    Evento,
    Lead,
    LeadEvento,
    LeadEventoSourceKind,
    StatusEvento,
    TipoLead,
    TipoResponsavel,
)
from app.services.landing_page_submission import ensure_ativacao_lead_link
from app.services.lead_event_service import ensure_lead_event


def seed_event_context(session: Session) -> tuple[Agencia, Evento, Lead]:
    agencia = Agencia(nome="V3A", dominio="v3a.com.br", lote=1)
    status = StatusEvento(nome="Previsto")
    session.add_all([agencia, status])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)

    evento = Evento(
        nome="Evento Origem",
        descricao="Evento para teste de origem.",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=agencia.id,
        status_id=status.id,
    )
    lead = Lead(nome="Maria", email="maria@example.com", cpf="52998224725")
    session.add_all([evento, lead])
    session.commit()
    session.refresh(evento)
    session.refresh(lead)
    return agencia, evento, lead


def test_tipo_lead_and_tipo_responsavel_values_are_lowercase() -> None:
    assert TipoLead.BILHETERIA.value == "bilheteria"
    assert TipoLead.ENTRADA_EVENTO.value == "entrada_evento"
    assert TipoLead.ATIVACAO.value == "ativacao"
    assert TipoResponsavel.PROPONENTE.value == "proponente"
    assert TipoResponsavel.AGENCIA.value == "agencia"


def test_ensure_lead_event_records_agency_responsavel(db_session: Session) -> None:
    agencia, evento, lead = seed_event_context(db_session)

    result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
        tipo_lead=TipoLead.ATIVACAO,
        responsavel_tipo=TipoResponsavel.AGENCIA,
        responsavel_nome=agencia.nome,
        responsavel_agencia_id=agencia.id,
    )
    db_session.commit()
    db_session.refresh(result.lead_evento)

    assert result.lead_evento.tipo_lead == TipoLead.ATIVACAO
    assert result.lead_evento.responsavel_tipo == TipoResponsavel.AGENCIA
    assert result.lead_evento.responsavel_nome == "V3A"
    assert result.lead_evento.responsavel_agencia_id == agencia.id

    second_result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
    )

    assert second_result.lead_evento.tipo_lead == TipoLead.ATIVACAO
    assert second_result.lead_evento.responsavel_tipo == TipoResponsavel.AGENCIA
    assert second_result.lead_evento.responsavel_nome == "V3A"
    assert second_result.lead_evento.responsavel_agencia_id == agencia.id


def test_ensure_ativacao_lead_link_defaults_nome_ativacao(db_session: Session) -> None:
    _, evento, lead = seed_event_context(db_session)
    ativacao = Ativacao(evento_id=evento.id or 0, nome="Roleta Premiada")
    db_session.add(ativacao)
    db_session.commit()
    db_session.refresh(ativacao)

    ativacao_lead = ensure_ativacao_lead_link(db_session, ativacao=ativacao, lead=lead)
    db_session.commit()
    db_session.refresh(ativacao_lead)

    assert ativacao_lead.nome_ativacao == "Roleta Premiada"


@pytest.mark.parametrize(
    ("responsavel_tipo", "responsavel_nome"),
    [
        (None, None),
        (TipoResponsavel.PROPONENTE, "Proponente X"),
    ],
)
def test_tipo_lead_ativacao_requires_agency_responsavel(
    db_session: Session,
    responsavel_tipo: TipoResponsavel | None,
    responsavel_nome: str | None,
) -> None:
    _, evento, lead = seed_event_context(db_session)
    lead_evento = LeadEvento(
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
        tipo_lead=TipoLead.ATIVACAO,
        responsavel_tipo=responsavel_tipo,
        responsavel_nome=responsavel_nome,
    )
    db_session.add(lead_evento)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
