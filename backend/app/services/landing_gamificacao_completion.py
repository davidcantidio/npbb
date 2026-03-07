"""Use case de conclusao de gamificacao na landing publica."""

from __future__ import annotations

from fastapi import status
from sqlmodel import Session

from app.models.models import Ativacao, AtivacaoLead, Gamificacao, now_utc
from app.schemas.gamificacao_landing import (
    GamificacaoCompleteRequest,
    GamificacaoCompleteResponse,
)
from app.utils.http_errors import raise_http_error


def _get_ativacao_or_404(session: Session, ativacao_id: int) -> Ativacao:
    ativacao = session.get(Ativacao, ativacao_id)
    if not ativacao:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )
    return ativacao


def _get_ativacao_lead_or_404(session: Session, ativacao_lead_id: int) -> AtivacaoLead:
    ativacao_lead = session.get(AtivacaoLead, ativacao_lead_id)
    if not ativacao_lead:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_LEAD_NOT_FOUND",
            message="Ativacao-lead nao encontrada",
        )
    return ativacao_lead


def _get_gamificacao_or_400(session: Session, gamificacao_id: int) -> Gamificacao:
    gamificacao = session.get(Gamificacao, gamificacao_id)
    if not gamificacao:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="GAMIFICACAO_INVALID",
            message=f"Gamificacao {gamificacao_id} nao encontrada",
        )
    return gamificacao


def _validate_gamificacao_scope(*, ativacao: Ativacao, gamificacao: Gamificacao) -> None:
    if ativacao.gamificacao_id is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="GAMIFICACAO_OUT_OF_SCOPE",
            message="Ativacao sem gamificacao configurada",
            field="gamificacao_id",
        )

    if gamificacao.evento_id != ativacao.evento_id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="GAMIFICACAO_OUT_OF_SCOPE",
            message="Gamificacao invalida para esta ativacao",
            field="gamificacao_id",
        )

    if ativacao.gamificacao_id != gamificacao.id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="GAMIFICACAO_OUT_OF_SCOPE",
            message="Gamificacao invalida para esta ativacao",
            field="gamificacao_id",
        )


def _apply_gamificacao_completion(
    *,
    ativacao_lead: AtivacaoLead,
    gamificacao_id: int,
    completed: bool,
) -> None:
    ativacao_lead.gamificacao_id = gamificacao_id
    ativacao_lead.gamificacao_completed = completed
    if completed:
        if ativacao_lead.gamificacao_completed_at is None:
            ativacao_lead.gamificacao_completed_at = now_utc()
    else:
        ativacao_lead.gamificacao_completed_at = None


def complete_landing_gamificacao(
    *,
    session: Session,
    ativacao_lead_id: int,
    payload: GamificacaoCompleteRequest,
) -> GamificacaoCompleteResponse:
    ativacao_lead = _get_ativacao_lead_or_404(session, ativacao_lead_id)
    ativacao = _get_ativacao_or_404(session, ativacao_lead.ativacao_id)
    gamificacao = _get_gamificacao_or_400(session, payload.gamificacao_id)
    _validate_gamificacao_scope(ativacao=ativacao, gamificacao=gamificacao)
    _apply_gamificacao_completion(
        ativacao_lead=ativacao_lead,
        gamificacao_id=payload.gamificacao_id,
        completed=payload.gamificacao_completed,
    )

    session.add(ativacao_lead)
    session.commit()
    session.refresh(ativacao_lead)

    if ativacao_lead.id is None or ativacao_lead.gamificacao_id is None:
        raise_http_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="GAMIFICACAO_UPDATE_FAILED",
            message="Falha ao persistir conclusao de gamificacao",
        )

    return GamificacaoCompleteResponse(
        ativacao_lead_id=ativacao_lead.id,
        gamificacao_id=ativacao_lead.gamificacao_id,
        gamificacao_completed=bool(ativacao_lead.gamificacao_completed),
        gamificacao_completed_at=ativacao_lead.gamificacao_completed_at,
    )
