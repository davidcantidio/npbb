import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models.models import (
    Agencia,
    Ativacao,
    Diretoria,
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


def seed_event_context(
    session: Session,
    *,
    diretoria_nome: str | None = "Diretoria BB",
) -> tuple[Agencia, Evento, Lead]:
    agencia = Agencia(nome="V3A", dominio="v3a.com.br", lote=1)
    status = StatusEvento(nome="Previsto")
    diretoria = Diretoria(nome=diretoria_nome) if diretoria_nome else None
    session.add_all([item for item in [agencia, status, diretoria] if item is not None])
    session.commit()
    session.refresh(agencia)
    session.refresh(status)
    if diretoria is not None:
        session.refresh(diretoria)

    evento = Evento(
        nome="Evento Origem",
        descricao="Evento para teste de origem.",
        concorrencia=False,
        cidade="Brasilia",
        estado="DF",
        agencia_id=agencia.id,
        diretoria_id=diretoria.id if diretoria is not None else None,
        status_id=status.id,
    )
    lead = Lead(nome="Maria", email="maria@example.com", cpf="52998224725")
    session.add_all([evento, lead])
    session.commit()
    session.refresh(evento)
    session.refresh(lead)
    return agencia, evento, lead


def seed_ativacao_lead_context(session: Session) -> tuple[Agencia, Evento, Lead, Ativacao]:
    agencia, evento, lead = seed_event_context(session)
    ativacao = Ativacao(evento_id=evento.id or 0, nome="Roleta Premiada")
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)
    return agencia, evento, lead, ativacao


def test_tipo_lead_and_tipo_responsavel_values_are_lowercase() -> None:
    assert TipoLead.BILHETERIA.value == "bilheteria"
    assert TipoLead.ENTRADA_EVENTO.value == "entrada_evento"
    assert TipoLead.ATIVACAO.value == "ativacao"
    assert TipoResponsavel.PROPONENTE.value == "proponente"
    assert TipoResponsavel.AGENCIA.value == "agencia"


def test_ensure_lead_event_derives_proponente_from_diretoria(db_session: Session) -> None:
    _, evento, lead = seed_event_context(db_session, diretoria_nome="Diretoria Patrocinios")

    result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        source_ref_id=evento.id,
    )
    db_session.commit()
    db_session.refresh(result.lead_evento)

    assert result.lead_evento.tipo_lead == TipoLead.ENTRADA_EVENTO
    assert result.lead_evento.responsavel_tipo == TipoResponsavel.PROPONENTE
    assert result.lead_evento.responsavel_nome == "Diretoria Patrocinios"
    assert result.lead_evento.responsavel_agencia_id is None


def test_ensure_lead_event_falls_back_to_event_name_without_diretoria(db_session: Session) -> None:
    _, evento, lead = seed_event_context(db_session, diretoria_nome=None)

    result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.LEAD_BATCH,
        source_ref_id=99,
    )
    db_session.commit()
    db_session.refresh(result.lead_evento)

    assert result.lead_evento.tipo_lead == TipoLead.ENTRADA_EVENTO
    assert result.lead_evento.responsavel_tipo == TipoResponsavel.PROPONENTE
    assert result.lead_evento.responsavel_nome == evento.nome
    assert result.lead_evento.responsavel_agencia_id is None


def test_ensure_lead_event_preserves_bilheteria_with_proponente_metadata(db_session: Session) -> None:
    _, evento, lead = seed_event_context(db_session, diretoria_nome="Diretoria Bilheteria")

    result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.MANUAL_RECONCILED,
        source_ref_id=123,
        tipo_lead=TipoLead.BILHETERIA,
    )
    db_session.commit()
    db_session.refresh(result.lead_evento)

    assert result.lead_evento.tipo_lead == TipoLead.BILHETERIA
    assert result.lead_evento.responsavel_tipo == TipoResponsavel.PROPONENTE
    assert result.lead_evento.responsavel_nome == "Diretoria Bilheteria"
    assert result.lead_evento.responsavel_agencia_id is None


def test_ensure_lead_event_records_agency_responsavel(db_session: Session) -> None:
    agencia, evento, lead, ativacao = seed_ativacao_lead_context(db_session)
    ativacao_lead = ensure_ativacao_lead_link(db_session, ativacao=ativacao, lead=lead)
    db_session.commit()
    db_session.refresh(ativacao_lead)

    result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
        source_ref_id=ativacao_lead.id,
    )
    db_session.commit()
    db_session.refresh(result.lead_evento)

    assert result.lead_evento.tipo_lead == TipoLead.ATIVACAO
    assert result.lead_evento.responsavel_tipo == TipoResponsavel.AGENCIA
    assert result.lead_evento.responsavel_nome == agencia.nome
    assert result.lead_evento.responsavel_agencia_id == agencia.id

    second_result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
        source_ref_id=ativacao_lead.id,
    )

    assert second_result.lead_evento.tipo_lead == TipoLead.ATIVACAO
    assert second_result.lead_evento.responsavel_tipo == TipoResponsavel.AGENCIA
    assert second_result.lead_evento.responsavel_nome == agencia.nome
    assert second_result.lead_evento.responsavel_agencia_id == agencia.id

    third_result = ensure_lead_event(
        db_session,
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        source_ref_id=evento.id,
    )

    assert third_result.lead_evento.source_kind == LeadEventoSourceKind.ACTIVATION
    assert third_result.lead_evento.source_ref_id == ativacao_lead.id
    assert third_result.lead_evento.tipo_lead == TipoLead.ATIVACAO
    assert third_result.lead_evento.responsavel_tipo == TipoResponsavel.AGENCIA
    assert third_result.lead_evento.responsavel_nome == agencia.nome
    assert third_result.lead_evento.responsavel_agencia_id == agencia.id


def test_ensure_ativacao_lead_link_defaults_nome_ativacao(db_session: Session) -> None:
    _, _, lead, ativacao = seed_ativacao_lead_context(db_session)

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
    _, evento, lead, ativacao = seed_ativacao_lead_context(db_session)
    ativacao_lead = ensure_ativacao_lead_link(db_session, ativacao=ativacao, lead=lead)
    db_session.commit()
    db_session.refresh(ativacao_lead)

    lead_evento = LeadEvento(
        lead_id=lead.id or 0,
        evento_id=evento.id or 0,
        source_kind=LeadEventoSourceKind.ACTIVATION,
        source_ref_id=ativacao_lead.id,
        tipo_lead=TipoLead.ATIVACAO,
        responsavel_tipo=responsavel_tipo,
        responsavel_nome=responsavel_nome,
        responsavel_agencia_id=None,
    )
    db_session.add(lead_evento)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
