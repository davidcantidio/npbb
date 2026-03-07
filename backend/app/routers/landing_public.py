"""Rotas publicas das landing pages dinamicas."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.models import Ativacao, Evento
from app.schemas.gamificacao_landing import (
    GamificacaoCompleteRequest,
    GamificacaoCompleteResponse,
)
from app.schemas.landing_public import (
    LandingAnalyticsTrackRequest,
    LandingAnalyticsTrackResponse,
    LandingPageRead,
    LandingSubmitRequest,
    LandingSubmitResponse,
    LandingTemplateConfigRead,
)
from app.services.landing_pages import (
    build_landing_payload,
    get_template_config,
    hydrate_ativacao_public_urls,
    track_landing_analytics,
    submit_landing_lead,
)
from app.services.landing_gamificacao_completion import complete_landing_gamificacao
from app.services.landing_pages import get_event_form_config as get_event_form_config_service
from app.services.qr_code import build_qr_code_svg
from app.utils.http_errors import raise_http_error

router = APIRouter(tags=["landing-public"])


def _get_evento_or_404(session: Session, evento_id: int) -> Evento:
    evento = session.get(Evento, evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
        )
    return evento


def _get_ativacao_or_404(session: Session, ativacao_id: int) -> Ativacao:
    ativacao = session.get(Ativacao, ativacao_id)
    if not ativacao:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )
    return ativacao


@router.get("/eventos/{evento_id}/landing", response_model=LandingPageRead)
def get_evento_landing(
    evento_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    evento = _get_evento_or_404(session, evento_id)
    return build_landing_payload(
        session,
        evento=evento,
        ativacao=None,
        backend_base_url=str(request.base_url),
    )


@router.get("/ativacoes/{ativacao_id}/landing", response_model=LandingPageRead)
def get_ativacao_landing(
    ativacao_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    evento = _get_evento_or_404(session, ativacao.evento_id)
    return build_landing_payload(
        session,
        evento=evento,
        ativacao=ativacao,
        backend_base_url=str(request.base_url),
    )


@router.get("/eventos/{evento_id}/template-config", response_model=LandingTemplateConfigRead)
def get_evento_template_config(
    evento_id: int,
    session: Session = Depends(get_session),
):
    evento = _get_evento_or_404(session, evento_id)
    _, _, template_name = get_event_form_config_service(session, evento_id=evento_id)
    return get_template_config(session, evento=evento, template_name=template_name)


@router.get("/ativacoes/{ativacao_id}/template-config", response_model=LandingTemplateConfigRead)
def get_ativacao_template_config(
    ativacao_id: int,
    session: Session = Depends(get_session),
):
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    evento = _get_evento_or_404(session, ativacao.evento_id)
    _, _, template_name = get_event_form_config_service(session, evento_id=evento.id or 0)
    return get_template_config(session, evento=evento, template_name=template_name)


@router.post(
    "/landing/eventos/{evento_id}/submit",
    response_model=LandingSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_evento_landing(
    evento_id: int,
    payload: LandingSubmitRequest,
    session: Session = Depends(get_session),
):
    evento = _get_evento_or_404(session, evento_id)
    landing = build_landing_payload(session, evento=evento, ativacao=None)
    return submit_landing_lead(
        session,
        evento=evento,
        ativacao=None,
        payload=payload,
        success_message=landing.formulario.mensagem_sucesso,
    )


@router.post(
    "/landing/ativacoes/{ativacao_id}/submit",
    response_model=LandingSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_ativacao_landing(
    ativacao_id: int,
    payload: LandingSubmitRequest,
    session: Session = Depends(get_session),
):
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    evento = _get_evento_or_404(session, ativacao.evento_id)
    landing = build_landing_payload(session, evento=evento, ativacao=ativacao)
    return submit_landing_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
        success_message=landing.formulario.mensagem_sucesso,
    )


@router.get("/ativacoes/{ativacao_id}/qr-code")
def get_ativacao_qr_code(
    ativacao_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    changed = hydrate_ativacao_public_urls(ativacao, backend_base_url=str(request.base_url))
    if changed:
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
    svg = build_qr_code_svg(ativacao.landing_url or "")
    return Response(content=svg, media_type="image/svg+xml")


@router.post("/landing/analytics", response_model=LandingAnalyticsTrackResponse)
def post_landing_analytics(
    payload: LandingAnalyticsTrackRequest,
    session: Session = Depends(get_session),
):
    track_landing_analytics(session, payload=payload)
    return LandingAnalyticsTrackResponse()


@router.post(
    "/ativacao-leads/{ativacao_lead_id}/gamificacao",
    response_model=GamificacaoCompleteResponse,
)
def complete_gamificacao(
    ativacao_lead_id: int,
    payload: GamificacaoCompleteRequest,
    session: Session = Depends(get_session),
):
    return complete_landing_gamificacao(
        session=session,
        ativacao_lead_id=ativacao_lead_id,
        payload=payload,
    )
