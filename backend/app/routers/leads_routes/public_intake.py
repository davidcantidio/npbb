
"""Rotas publicas de captura e reconhecimento de lead."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi import Response as FastAPIResponse
from sqlmodel import Session

from app.db.database import get_session, set_internal_service_db_context
from app.models.models import Ativacao, Evento
from app.schemas.landing_public import LandingSubmitRequest, LandingSubmitResponse
from app.schemas.reconhecimento import LeadRecognitionRead
from app.services.landing_page_submission import get_public_lead_success_message, submit_public_lead
from app.services.reconhecimento import set_lead_recognition_cookie, validar_token
from app.utils.cpf import validate_and_normalize_cpf
from app.utils.http_errors import raise_http_error

router = APIRouter()


def _get_public_submit_context(
    session: Session,
    *,
    payload: LandingSubmitRequest,
) -> tuple[Evento, Ativacao | None, str | None]:
    set_internal_service_db_context(session)
    ativacao: Ativacao | None = None

    if payload.ativacao_id is not None:
        ativacao = session.get(Ativacao, payload.ativacao_id)
        if ativacao is None:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="ATIVACAO_NOT_FOUND",
                message="Ativacao nao encontrada",
                field="ativacao_id",
            )

        if payload.event_id is not None and payload.event_id != ativacao.evento_id:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="EVENTO_ATIVACAO_MISMATCH",
                message="event_id diverge da ativacao informada",
                field="event_id",
            )
        if not payload.cpf:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="CPF_REQUIRED",
                message="cpf obrigatorio quando ativacao_id for informado",
                field="cpf",
            )
        try:
            cpf_for_conversion = validate_and_normalize_cpf(payload.cpf)
        except ValueError:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="CPF_INVALID",
                message="CPF invalido",
                field="cpf",
            )

        evento = session.get(Evento, ativacao.evento_id)
        if evento is None:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="EVENTO_NOT_FOUND",
                message="Evento nao encontrado",
                field="event_id",
            )
        return evento, ativacao, cpf_for_conversion

    if payload.event_id is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EVENT_ID_REQUIRED",
            message="event_id obrigatorio quando ativacao_id nao for informado",
            field="event_id",
        )

    evento = session.get(Evento, payload.event_id)
    if evento is None:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
            field="event_id",
        )
    return evento, None, None

def criar_lead_publico(
    payload: LandingSubmitRequest,
    response: FastAPIResponse,
    session: Session = Depends(get_session),
):
    evento, ativacao, cpf_for_conversion = _get_public_submit_context(
        session,
        payload=payload,
    )
    result = submit_public_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
        success_message=get_public_lead_success_message(session, evento=evento),
        cpf_for_conversion=cpf_for_conversion,
    )
    if result.token_reconhecimento:
        set_lead_recognition_cookie(response, result.token_reconhecimento)
    return result


@router.get("/reconhecer", response_model=LeadRecognitionRead)
def reconhecer_lead_publico(
    token: str,
    evento_id: int,
    session: Session = Depends(get_session),
):
    set_internal_service_db_context(session)
    result = validar_token(session, token=token, evento_id=evento_id)
    return LeadRecognitionRead(
        lead_reconhecido=result is not None,
        lead_id=result.lead_id if result else None,
    )
