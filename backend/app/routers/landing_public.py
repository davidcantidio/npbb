"""Rotas publicas das landing pages dinamicas."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.models import Ativacao, Evento
from app.schemas.landing import LandingPayload
from app.schemas.gamificacao_landing import (
    GamificacaoCompleteRequest,
    GamificacaoCompleteResponse,
)
from app.schemas.landing_public import (
    LandingAnalyticsTrackRequest,
    LandingAnalyticsTrackResponse,
    LandingSubmitRequest,
    LandingSubmitResponse,
    LandingTemplateConfigRead,
)
from app.services.landing_pages import (
    build_landing_payload,
    get_template_config,
    hydrate_ativacao_public_urls,
    normalize_template_override_input,
    track_landing_analytics,
)
from app.services.landing_gamificacao_completion import complete_landing_gamificacao
from app.services.landing_page_submission import (
    get_public_lead_success_message,
    submit_landing_lead,
)
from app.services.landing_pages import get_event_form_config as get_event_form_config_service
from app.services.qr_code import build_qr_code_svg
from app.utils.cpf import is_valid_cpf
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


def _get_ativacao_for_evento_or_404(
    session: Session,
    *,
    evento_id: int,
    ativacao_id: int,
) -> Ativacao:
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    if ativacao.evento_id != evento_id:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )
    return ativacao


def _normalize_preview_template_override(template_override: str | None) -> str | None:
    normalized = normalize_template_override_input(template_override)
    if template_override is not None and str(template_override).strip() and normalized is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="LANDING_TEMPLATE_OVERRIDE_INVALID",
            message="template_override fora do catalogo homologado",
        )
    return normalized


@router.get("/eventos/{evento_id}/landing", response_model=LandingPayload)
def get_evento_landing(
    evento_id: int,
    request: Request,
    template_override: str | None = Query(default=None, max_length=50),
    session: Session = Depends(get_session),
):
    evento = _get_evento_or_404(session, evento_id)
    return build_landing_payload(
        session,
        evento=evento,
        ativacao=None,
        backend_base_url=str(request.base_url),
        template_override=_normalize_preview_template_override(template_override),
    )


def _build_ativacao_landing_payload(
    *,
    session: Session,
    ativacao: Ativacao,
    request: Request,
    token: str | None,
) -> LandingPayload:
    evento = _get_evento_or_404(session, ativacao.evento_id)
    return build_landing_payload(
        session,
        evento=evento,
        ativacao=ativacao,
        backend_base_url=str(request.base_url),
        token=token,
    )


@router.get("/ativacoes/{ativacao_id}/landing", response_model=LandingPayload)
def get_ativacao_landing(
    ativacao_id: int,
    request: Request,
    token: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    ativacao = _get_ativacao_or_404(session, ativacao_id)
    return _build_ativacao_landing_payload(
        session=session,
        ativacao=ativacao,
        request=request,
        token=token,
    )


@router.get(
    "/eventos/{evento_id}/ativacoes/{ativacao_id}/landing",
    response_model=LandingPayload,
)
def get_evento_ativacao_landing(
    evento_id: int,
    ativacao_id: int,
    request: Request,
    token: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    _get_evento_or_404(session, evento_id)
    ativacao = _get_ativacao_for_evento_or_404(
        session,
        evento_id=evento_id,
        ativacao_id=ativacao_id,
    )
    return _build_ativacao_landing_payload(
        session=session,
        ativacao=ativacao,
        request=request,
        token=token,
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
    return submit_landing_lead(
        session,
        evento=evento,
        ativacao=None,
        payload=payload,
        success_message=get_public_lead_success_message(session, evento=evento),
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
    return submit_landing_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
        success_message=get_public_lead_success_message(session, evento=evento),
        cpf_for_conversion=payload.cpf if payload.cpf and is_valid_cpf(payload.cpf) else None,
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
