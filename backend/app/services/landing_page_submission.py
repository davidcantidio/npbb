"""Lead submission flow for public landing pages."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.models import Ativacao, AtivacaoLead, Evento, LandingAnalyticsEvent, Lead
from app.schemas.landing_public import LandingSubmitRequest, LandingSubmitResponse
from app.services.landing_page_templates import get_template_config

ANALYTICS_EVENT_SUBMIT_SUCCESS = "submit_success"


def _find_existing_landing_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    email: str | None,
) -> Lead | None:
    if not email:
        return None

    if ativacao and ativacao.id is not None:
        return session.exec(
            select(Lead)
            .join(AtivacaoLead, AtivacaoLead.lead_id == Lead.id)
            .where(AtivacaoLead.ativacao_id == ativacao.id)
            .where(func.lower(Lead.email) == email)
        ).first()

    return session.exec(
        select(Lead)
        .where(func.lower(Lead.email) == email)
        .where(Lead.evento_nome == evento.nome)
    ).first()


def _create_landing_lead(
    session: Session,
    *,
    evento: Evento,
    payload: LandingSubmitRequest,
    email: str | None,
) -> Lead:
    lead = Lead(
        nome=payload.nome,
        sobrenome=payload.sobrenome,
        email=email,
        telefone=payload.telefone,
        cpf=payload.cpf,
        data_nascimento=payload.data_nascimento,
        evento_nome=evento.nome,
        cidade=evento.cidade,
        estado=(payload.estado or evento.estado or "").strip() or None,
        endereco_rua=payload.endereco,
        genero=payload.genero,
        metodo_entrega=payload.area_de_atuacao,
        fonte_origem="landing_publica",
        opt_in="aceito",
        opt_in_flag=True,
    )
    session.add(lead)
    session.flush()
    return lead


def _ensure_ativacao_lead_link(
    session: Session,
    *,
    ativacao: Ativacao | None,
    lead: Lead,
) -> AtivacaoLead | None:
    if ativacao is None or ativacao.id is None or lead.id is None:
        return None

    ativacao_lead = session.exec(
        select(AtivacaoLead)
        .where(AtivacaoLead.ativacao_id == ativacao.id)
        .where(AtivacaoLead.lead_id == lead.id)
    ).first()
    if ativacao_lead is None:
        ativacao_lead = AtivacaoLead(ativacao_id=ativacao.id, lead_id=lead.id)
        try:
            with session.begin_nested():
                session.add(ativacao_lead)
                session.flush()
        except IntegrityError:
            ativacao_lead = session.exec(
                select(AtivacaoLead)
                .where(AtivacaoLead.ativacao_id == ativacao.id)
                .where(AtivacaoLead.lead_id == lead.id)
            ).first()
            if ativacao_lead is None:
                raise
    return ativacao_lead


def _track_submit_success_analytics_if_needed(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
) -> None:
    if not (payload.cta_variant_id or payload.landing_session_id):
        return

    template_config = get_template_config(session, evento=evento)
    session.add(
        LandingAnalyticsEvent(
            event_id=evento.id or 0,
            ativacao_id=ativacao.id if ativacao else None,
            categoria=template_config.categoria,
            tema=template_config.tema,
            event_name=ANALYTICS_EVENT_SUBMIT_SUCCESS,
            cta_variant_id=payload.cta_variant_id,
            landing_session_id=payload.landing_session_id,
        )
    )


def submit_landing_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
    success_message: str,
) -> LandingSubmitResponse:
    email = str(payload.email).strip().lower() if payload.email else None
    existing_lead = _find_existing_landing_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        email=email,
    )

    if not existing_lead:
        existing_lead = _create_landing_lead(
            session,
            evento=evento,
            payload=payload,
            email=email,
        )

    ativacao_lead = _ensure_ativacao_lead_link(
        session,
        ativacao=ativacao,
        lead=existing_lead,
    )
    _track_submit_success_analytics_if_needed(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
    )

    session.commit()
    session.refresh(existing_lead)
    if ativacao_lead:
        session.refresh(ativacao_lead)
    return LandingSubmitResponse(
        lead_id=existing_lead.id or 0,
        event_id=evento.id or 0,
        ativacao_id=ativacao.id if ativacao else None,
        ativacao_lead_id=ativacao_lead.id if ativacao_lead else None,
        mensagem_sucesso=success_message,
    )
