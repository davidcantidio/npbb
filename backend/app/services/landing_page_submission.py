"""Lead submission flow for public landing pages."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.models import (
    Ativacao,
    AtivacaoLead,
    ConversaoAtivacao,
    Evento,
    LandingAnalyticsEvent,
    Lead,
)
from app.schemas.landing_public import LandingSubmitRequest, LandingSubmitResponse
from app.services.landing_page_templates import TEMPLATE_REGISTRY, get_template_config
from app.services.reconhecimento import gerar_token

ANALYTICS_EVENT_SUBMIT_SUCCESS = "submit_success"


def get_public_lead_success_message(
    session: Session,
    *,
    evento: Evento,
) -> str:
    template_config = get_template_config(session, evento=evento)
    return TEMPLATE_REGISTRY[template_config.categoria]["success_message"]


def _find_existing_public_lead(
    session: Session,
    *,
    evento: Evento,
    email: str | None,
    cpf: str | None,
) -> Lead | None:
    if email and cpf:
        exact_match = session.exec(
            select(Lead)
            .where(func.lower(Lead.email) == email)
            .where(Lead.cpf == cpf)
            .where(Lead.evento_nome == evento.nome)
        ).first()
        if exact_match is not None:
            return exact_match

    if cpf:
        by_cpf = session.exec(
            select(Lead)
            .where(Lead.cpf == cpf)
            .where(Lead.evento_nome == evento.nome)
        ).first()
        if by_cpf is not None:
            return by_cpf

    if email:
        return session.exec(
            select(Lead)
            .where(func.lower(Lead.email) == email)
            .where(Lead.evento_nome == evento.nome)
            .where(Lead.cpf.is_(None))
        ).first()

    return None


def _build_public_lead_defaults(
    *,
    evento: Evento,
    payload: LandingSubmitRequest,
    email: str | None,
) -> dict[str, object]:
    return {
        "nome": payload.nome,
        "sobrenome": payload.sobrenome,
        "email": email,
        "telefone": payload.telefone,
        "cpf": payload.cpf,
        "data_nascimento": payload.data_nascimento,
        "evento_nome": evento.nome,
        "cidade": evento.cidade,
        "estado": (payload.estado or evento.estado or "").strip() or None,
        "endereco_rua": payload.endereco,
        "genero": payload.genero,
        "metodo_entrega": payload.area_de_atuacao,
        "fonte_origem": "landing_publica",
        "opt_in": "aceito",
        "opt_in_flag": True,
    }


def _merge_public_lead(
    *,
    lead: Lead,
    values: dict[str, object],
) -> None:
    for field, value in values.items():
        if value is None:
            continue
        current = getattr(lead, field)
        if field in {"email", "cpf", "fonte_origem"} and current:
            continue
        if isinstance(current, str) and current.strip():
            continue
        if current is not None and field == "opt_in_flag":
            continue
        setattr(lead, field, value)


def resolve_or_create_public_lead(
    session: Session,
    *,
    evento: Evento,
    payload: LandingSubmitRequest,
    email: str | None,
) -> Lead:
    values = _build_public_lead_defaults(evento=evento, payload=payload, email=email)
    lead = _find_existing_public_lead(
        session,
        evento=evento,
        email=email,
        cpf=payload.cpf,
    )
    if lead is None:
        lead = Lead(**values)
        session.add(lead)
        session.flush()
        return lead

    _merge_public_lead(lead=lead, values=values)
    return lead


def ensure_ativacao_lead_link(
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


def register_conversao_ativacao(
    session: Session,
    *,
    ativacao: Ativacao | None,
    lead: Lead,
    cpf: str | None,
) -> bool:
    if ativacao is None or ativacao.id is None or lead.id is None or not cpf:
        return False

    session.add(
        ConversaoAtivacao(
            ativacao_id=ativacao.id,
            lead_id=lead.id,
            cpf=cpf,
        )
    )
    session.flush()
    return True


def _find_duplicate_conversao_ativacao(
    session: Session,
    *,
    ativacao: Ativacao | None,
    cpf: str | None,
) -> ConversaoAtivacao | None:
    if ativacao is None or ativacao.id is None or not cpf or not ativacao.checkin_unico:
        return None

    return session.exec(
        select(ConversaoAtivacao)
        .where(ConversaoAtivacao.ativacao_id == ativacao.id)
        .where(ConversaoAtivacao.cpf == cpf)
    ).first()


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


def submit_public_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
    success_message: str,
    cpf_for_conversion: str | None = None,
) -> LandingSubmitResponse:
    duplicate_conversao = _find_duplicate_conversao_ativacao(
        session,
        ativacao=ativacao,
        cpf=cpf_for_conversion,
    )
    if duplicate_conversao is not None:
        ativacao_lead = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == duplicate_conversao.ativacao_id)
            .where(AtivacaoLead.lead_id == duplicate_conversao.lead_id)
        ).first()
        return LandingSubmitResponse(
            lead_id=duplicate_conversao.lead_id,
            event_id=evento.id or 0,
            ativacao_id=ativacao.id if ativacao else None,
            ativacao_lead_id=ativacao_lead.id if ativacao_lead else None,
            mensagem_sucesso=success_message,
            conversao_registrada=False,
            bloqueado_cpf_duplicado=True,
        )

    email = str(payload.email).strip().lower() if payload.email else None
    lead = resolve_or_create_public_lead(
        session,
        evento=evento,
        payload=payload,
        email=email,
    )
    ativacao_lead = ensure_ativacao_lead_link(
        session,
        ativacao=ativacao,
        lead=lead,
    )
    conversao_registrada = register_conversao_ativacao(
        session,
        ativacao=ativacao,
        lead=lead,
        cpf=cpf_for_conversion,
    )
    token_reconhecimento: str | None = None
    if ativacao is not None and lead.id is not None and evento.id is not None and conversao_registrada:
        token_reconhecimento = gerar_token(session, lead_id=lead.id, evento_id=evento.id)
    _track_submit_success_analytics_if_needed(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
    )

    session.commit()
    session.refresh(lead)
    if ativacao_lead:
        session.refresh(ativacao_lead)
    return LandingSubmitResponse(
        lead_id=lead.id or 0,
        event_id=evento.id or 0,
        ativacao_id=ativacao.id if ativacao else None,
        ativacao_lead_id=ativacao_lead.id if ativacao_lead else None,
        mensagem_sucesso=success_message,
        conversao_registrada=conversao_registrada,
        bloqueado_cpf_duplicado=False,
        token_reconhecimento=token_reconhecimento,
    )


def submit_landing_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
    success_message: str,
    cpf_for_conversion: str | None = None,
) -> LandingSubmitResponse:
    return submit_public_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
        success_message=success_message,
        cpf_for_conversion=cpf_for_conversion,
    )
