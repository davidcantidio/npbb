"""Rotas de gamificacao (CRUD por ativacao) - MVP."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Ativacao, Evento, Gamificacao, Usuario, UsuarioTipo
from app.schemas.gamificacao import GamificacaoRead, GamificacaoUpdate
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/gamificacao", tags=["gamificacao"])


def _check_visibility_or_404(*, evento: Evento, current_user: Usuario) -> None:
    if current_user.tipo_usuario != UsuarioTipo.AGENCIA:
        return
    if not current_user.agencia_id:
        raise_http_error(
            status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message="Usuario agencia sem agencia_id",
            field="agencia_id",
        )
    if evento.agencia_id != current_user.agencia_id:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="GAMIFICACAO_NOT_FOUND",
            message="Gamificacao nao encontrada",
        )


def _get_visible_gamificacao_or_404(
    *,
    session: Session,
    gamificacao_id: int,
    current_user: Usuario,
) -> Gamificacao:
    gamificacao = session.get(Gamificacao, gamificacao_id)
    if not gamificacao:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="GAMIFICACAO_NOT_FOUND",
            message="Gamificacao nao encontrada",
        )

    ativacao = session.get(Ativacao, gamificacao.ativacao_id)
    if not ativacao:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="GAMIFICACAO_NOT_FOUND",
            message="Gamificacao nao encontrada",
        )

    evento = session.get(Evento, ativacao.evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="GAMIFICACAO_NOT_FOUND",
            message="Gamificacao nao encontrada",
        )

    _check_visibility_or_404(evento=evento, current_user=current_user)
    return gamificacao


@router.put("/{gamificacao_id}", response_model=GamificacaoRead)
@router.put("/{gamificacao_id}/", response_model=GamificacaoRead)
def atualizar_gamificacao(
    gamificacao_id: int,
    payload: GamificacaoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    gamificacao = _get_visible_gamificacao_or_404(
        session=session,
        gamificacao_id=gamificacao_id,
        current_user=current_user,
    )

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR_NO_FIELDS",
            message="Nenhum campo para atualizar",
        )

    for key, value in data.items():
        setattr(gamificacao, key, value)

    session.add(gamificacao)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = session.exec(select(Gamificacao).where(Gamificacao.ativacao_id == gamificacao.ativacao_id)).first()
        if existing and existing.id != gamificacao.id:
            raise_http_error(
                status.HTTP_409_CONFLICT,
                code="GAMIFICACAO_ALREADY_EXISTS",
                message="Gamificacao ja existe para esta ativacao",
                field="ativacao_id",
            )
        raise

    session.refresh(gamificacao)
    return GamificacaoRead.model_validate(gamificacao, from_attributes=True)


@router.delete("/{gamificacao_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{gamificacao_id}/", status_code=status.HTTP_204_NO_CONTENT)
def deletar_gamificacao(
    gamificacao_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    gamificacao = _get_visible_gamificacao_or_404(
        session=session,
        gamificacao_id=gamificacao_id,
        current_user=current_user,
    )

    session.delete(gamificacao)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
