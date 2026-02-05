"""Rotas de ativacao (update/delete) - MVP."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    Ativacao,
    AtivacaoLead,
    Cupom,
    Evento,
    Gamificacao,
    Investimento,
    QuestionarioResposta,
    TermoUsoAtivacao,
    Usuario,
    UsuarioTipo,
    now_utc,
)
from app.schemas.ativacao import AtivacaoRead, AtivacaoUpdate
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/ativacao", tags=["ativacao"])


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
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )


def _get_visible_ativacao_or_404(
    *,
    session: Session,
    ativacao_id: int,
    current_user: Usuario,
) -> Ativacao:
    ativacao = session.get(Ativacao, ativacao_id)
    if not ativacao:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )

    evento = session.get(Evento, ativacao.evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )

    _check_visibility_or_404(evento=evento, current_user=current_user)
    return ativacao


@router.put("/{ativacao_id}", response_model=AtivacaoRead)
@router.put("/{ativacao_id}/", response_model=AtivacaoRead)
def atualizar_ativacao(
    ativacao_id: int,
    payload: AtivacaoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    ativacao = _get_visible_ativacao_or_404(
        session=session,
        ativacao_id=ativacao_id,
        current_user=current_user,
    )

    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR_NO_FIELDS",
            message="Nenhum campo para atualizar",
        )

    if "gamificacao_id" in data and data["gamificacao_id"] is not None:
        gamificacao = session.get(Gamificacao, data["gamificacao_id"])
        if not gamificacao or gamificacao.evento_id != ativacao.evento_id:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="GAMIFICACAO_OUT_OF_SCOPE",
                message="Gamificacao invalida para este evento",
                field="gamificacao_id",
            )

    for key, value in data.items():
        setattr(ativacao, key, value)

    ativacao.updated_at = now_utc()
    session.add(ativacao)
    session.commit()

    session.refresh(ativacao)
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)


@router.delete("/{ativacao_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{ativacao_id}/", status_code=status.HTTP_204_NO_CONTENT)
def deletar_ativacao(
    ativacao_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    ativacao = _get_visible_ativacao_or_404(
        session=session,
        ativacao_id=ativacao_id,
        current_user=current_user,
    )

    dependencies = {
        "ativacao_leads": int(
            session.exec(
                select(func.count())
                .select_from(AtivacaoLead)
                .where(AtivacaoLead.ativacao_id == ativacao_id)
            ).one()
        ),
        "cupons": int(
            session.exec(
                select(func.count()).select_from(Cupom).where(Cupom.ativacao_id == ativacao_id)
            ).one()
        ),
        "respostas_questionario": int(
            session.exec(
                select(func.count())
                .select_from(QuestionarioResposta)
                .where(QuestionarioResposta.ativacao_id == ativacao_id)
            ).one()
        ),
        "investimentos": int(
            session.exec(
                select(func.count())
                .select_from(Investimento)
                .where(Investimento.ativacao_id == ativacao_id)
            ).one()
        ),
    }

    if any(v > 0 for v in dependencies.values()):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ATIVACAO_DELETE_BLOCKED",
            message="Nao e possivel excluir ativacao com vinculos",
            extra={"dependencies": {k: v for k, v in dependencies.items() if v > 0}},
        )

    # Objetos 1:1 de configuracao (nao entram na lista de bloqueio do MVP).
    termo = session.exec(
        select(TermoUsoAtivacao).where(TermoUsoAtivacao.ativacao_id == ativacao_id)
    ).first()
    if termo:
        session.delete(termo)

    try:
        session.delete(ativacao)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ATIVACAO_DELETE_BLOCKED",
            message="Nao e possivel excluir ativacao com vinculos",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
