"""Rotas de ativacao (update/delete) - MVP."""

from __future__ import annotations

from decimal import Decimal

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
from app.schemas.ativacao import AtivacaoCreate, AtivacaoRead, AtivacaoUpdate
from app.services.landing_pages import hydrate_ativacao_public_urls
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/ativacao", tags=["ativacao"])
eventos_router = APIRouter(prefix="/eventos", tags=["ativacao"])


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
    evento_id: int | None = None,
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
    if evento_id is not None and ativacao.evento_id != evento_id:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ATIVACAO_NOT_FOUND",
            message="Ativacao nao encontrada",
        )
    return ativacao


def _get_visible_evento_or_404(
    *,
    session: Session,
    evento_id: int,
    current_user: Usuario,
) -> Evento:
    evento = session.get(Evento, evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
        )

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
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
                code="EVENTO_NOT_FOUND",
                message="Evento nao encontrado",
            )
    return evento


def _validate_gamificacao_scope(
    *,
    session: Session,
    evento_id: int,
    gamificacao_id: int | None,
) -> None:
    if gamificacao_id is None:
        return

    gamificacao = session.get(Gamificacao, gamificacao_id)
    if not gamificacao or gamificacao.evento_id != evento_id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="GAMIFICACAO_OUT_OF_SCOPE",
            message="Gamificacao invalida para este evento",
            field="gamificacao_id",
        )


def _refresh_ativacao_urls(session: Session, ativacao: Ativacao) -> Ativacao:
    session.refresh(ativacao)
    if hydrate_ativacao_public_urls(ativacao):
        ativacao.updated_at = now_utc()
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
    return ativacao


def _build_ativacao_update_data(payload: AtivacaoUpdate) -> dict[str, object]:
    data = payload.model_dump(exclude_unset=True)
    data.pop("conversao_unica", None)
    if data:
        return data
    raise_http_error(
        status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR_NO_FIELDS",
        message="Nenhum campo para atualizar",
    )


def _apply_ativacao_update(
    *,
    session: Session,
    ativacao: Ativacao,
    data: dict[str, object],
) -> Ativacao:
    _validate_gamificacao_scope(
        session=session,
        evento_id=ativacao.evento_id,
        gamificacao_id=data.get("gamificacao_id"),
    )
    for key, value in data.items():
        setattr(ativacao, key, value)
    ativacao.updated_at = now_utc()
    session.add(ativacao)
    session.commit()
    return _refresh_ativacao_urls(session, ativacao)


def _count_ativacao_dependencies(session: Session, ativacao_id: int) -> dict[str, int]:
    return {
        name: int(
            session.exec(
                select(func.count()).select_from(model).where(model.ativacao_id == ativacao_id)
            ).one()
        )
        for name, model in (
            ("ativacao_leads", AtivacaoLead),
            ("cupons", Cupom),
            ("respostas_questionario", QuestionarioResposta),
            ("investimentos", Investimento),
        )
    }


@eventos_router.get("/{evento_id}/ativacoes", response_model=list[AtivacaoRead])
@eventos_router.get("/{evento_id}/ativacoes/", response_model=list[AtivacaoRead])
def listar_ativacoes_por_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _get_visible_evento_or_404(
        session=session,
        evento_id=evento_id,
        current_user=current_user,
    )

    ativacoes = session.exec(
        select(Ativacao).where(Ativacao.evento_id == evento_id).order_by(Ativacao.id)
    ).all()
    changed = False
    for ativacao in ativacoes:
        changed = hydrate_ativacao_public_urls(ativacao) or changed

    if changed:
        for ativacao in ativacoes:
            ativacao.updated_at = now_utc()
            session.add(ativacao)
        session.commit()
        for ativacao in ativacoes:
            session.refresh(ativacao)

    return [AtivacaoRead.model_validate(ativacao, from_attributes=True) for ativacao in ativacoes]


@eventos_router.post(
    "/{evento_id}/ativacoes",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
@eventos_router.post(
    "/{evento_id}/ativacoes/",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_ativacao_por_evento(
    evento_id: int,
    payload: AtivacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _get_visible_evento_or_404(
        session=session,
        evento_id=evento_id,
        current_user=current_user,
    )
    _validate_gamificacao_scope(
        session=session,
        evento_id=evento_id,
        gamificacao_id=payload.gamificacao_id,
    )

    ativacao = Ativacao(
        evento_id=evento_id,
        nome=payload.nome,
        descricao=payload.descricao,
        mensagem_qrcode=payload.mensagem_qrcode,
        gamificacao_id=payload.gamificacao_id,
        redireciona_pesquisa=payload.redireciona_pesquisa,
        checkin_unico=payload.checkin_unico,
        termo_uso=payload.termo_uso,
        gera_cupom=payload.gera_cupom,
        valor=Decimal("0.00"),
    )
    session.add(ativacao)
    session.commit()

    ativacao = _refresh_ativacao_urls(session, ativacao)
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)


@eventos_router.get(
    "/{evento_id}/ativacoes/{ativacao_id}",
    response_model=AtivacaoRead,
)
@eventos_router.get(
    "/{evento_id}/ativacoes/{ativacao_id}/",
    response_model=AtivacaoRead,
)
def obter_ativacao_por_evento(
    evento_id: int,
    ativacao_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _get_visible_evento_or_404(
        session=session,
        evento_id=evento_id,
        current_user=current_user,
    )
    ativacao = _get_visible_ativacao_or_404(
        session=session,
        evento_id=evento_id,
        ativacao_id=ativacao_id,
        current_user=current_user,
    )
    ativacao = _refresh_ativacao_urls(session, ativacao)
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)


@eventos_router.patch(
    "/{evento_id}/ativacoes/{ativacao_id}",
    response_model=AtivacaoRead,
)
@eventos_router.patch(
    "/{evento_id}/ativacoes/{ativacao_id}/",
    response_model=AtivacaoRead,
)
def atualizar_ativacao_por_evento(
    evento_id: int,
    ativacao_id: int,
    payload: AtivacaoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _get_visible_evento_or_404(
        session=session,
        evento_id=evento_id,
        current_user=current_user,
    )
    ativacao = _get_visible_ativacao_or_404(
        session=session,
        evento_id=evento_id,
        ativacao_id=ativacao_id,
        current_user=current_user,
    )
    ativacao = _apply_ativacao_update(
        session=session,
        ativacao=ativacao,
        data=_build_ativacao_update_data(payload),
    )
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)


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
    ativacao = _apply_ativacao_update(
        session=session,
        ativacao=ativacao,
        data=_build_ativacao_update_data(payload),
    )
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
    dependencies = _count_ativacao_dependencies(session, ativacao_id)

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
