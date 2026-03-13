"""Rotas de questionário por evento."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import QuestionarioResposta, Usuario
from app.schemas.questionario import (
    QuestionarioEstruturaRead,
    QuestionarioEstruturaWrite,
    QuestionarioPaginaRead,
)
from app.services.questionario import load_questionario_estrutura, replace_questionario_estrutura

from . import _shared

router = APIRouter()


@router.get("/{evento_id}/questionario", response_model=QuestionarioEstruturaRead)
@router.get("/{evento_id}/questionario/", response_model=QuestionarioEstruturaRead)
def obter_questionario(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    paginas = load_questionario_estrutura(session, evento_id=evento_id)
    paginas_read = [QuestionarioPaginaRead.model_validate(p, from_attributes=True) for p in paginas]
    return QuestionarioEstruturaRead(evento_id=evento_id, paginas=paginas_read)


@router.put("/{evento_id}/questionario", response_model=QuestionarioEstruturaRead)
@router.put("/{evento_id}/questionario/", response_model=QuestionarioEstruturaRead)
def salvar_questionario(
    evento_id: int,
    payload: QuestionarioEstruturaWrite,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    respostas = session.exec(
        select(func.count())
        .select_from(QuestionarioResposta)
        .where(QuestionarioResposta.evento_id == evento_id)
    ).one()
    if int(respostas) > 0:
        _shared._raise_http(
            status.HTTP_409_CONFLICT,
            code="QUESTIONARIO_UPDATE_BLOCKED",
            message="Nao e possivel atualizar questionario com respostas",
            extra={"extra": {"dependencies": {"respostas_questionario": int(respostas)}}},
        )

    paginas = replace_questionario_estrutura(session, evento_id=evento_id, payload=payload)
    paginas_read = [QuestionarioPaginaRead.model_validate(p, from_attributes=True) for p in paginas]
    return QuestionarioEstruturaRead(evento_id=evento_id, paginas=paginas_read)
