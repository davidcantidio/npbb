"""Rotas de gamificações por evento."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Gamificacao, Usuario
from app.schemas.gamificacao import GamificacaoCreate, GamificacaoRead

from . import _shared

router = APIRouter()


@router.get("/{evento_id}/gamificacoes", response_model=list[GamificacaoRead])
@router.get("/{evento_id}/gamificacoes/", response_model=list[GamificacaoRead])
def listar_gamificacoes(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    gamificacoes = session.exec(
        select(Gamificacao).where(Gamificacao.evento_id == evento_id).order_by(Gamificacao.id)
    ).all()
    return [GamificacaoRead.model_validate(g, from_attributes=True) for g in gamificacoes]


@router.post(
    "/{evento_id}/gamificacoes",
    response_model=GamificacaoRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{evento_id}/gamificacoes/",
    response_model=GamificacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_gamificacao(
    evento_id: int,
    payload: GamificacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    gamificacao = Gamificacao(
        evento_id=evento_id,
        nome=payload.nome,
        descricao=payload.descricao,
        premio=payload.premio,
        titulo_feedback=payload.titulo_feedback,
        texto_feedback=payload.texto_feedback,
    )
    session.add(gamificacao)
    session.commit()

    session.refresh(gamificacao)
    return GamificacaoRead.model_validate(gamificacao, from_attributes=True)
