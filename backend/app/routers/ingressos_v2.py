"""Ingressos v2 configuration and planned quantities endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.ingressos_v2_models import (
    AuditoriaIngressoEvento,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    PrevisaoIngresso,
)
from app.models.models import Diretoria, TipoIngresso, Usuario, now_utc
from app.platform.security.rbac import require_npbb_user
from app.routers.eventos import _shared as eventos_shared
from app.schemas.ingressos_v2 import (
    ConfiguracaoIngressoEventoCreate,
    ConfiguracaoIngressoEventoRead,
    ConfiguracaoIngressoEventoUpdate,
    PrevisaoIngressoCreate,
    PrevisaoIngressoRead,
)
from app.utils.http_errors import raise_http_error


router = APIRouter(prefix="/ingressos/v2", tags=["ingressos"])


def _list_config_tipos(
    session: Session, configuracao_id: int
) -> list[ConfiguracaoIngressoEventoTipo]:
    return session.exec(
        select(ConfiguracaoIngressoEventoTipo)
        .where(ConfiguracaoIngressoEventoTipo.configuracao_id == configuracao_id)
        .order_by(ConfiguracaoIngressoEventoTipo.tipo_ingresso)
    ).all()


def _serialize_config(
    session: Session, configuracao: ConfiguracaoIngressoEvento
) -> ConfiguracaoIngressoEventoRead:
    tipos = _list_config_tipos(session, int(configuracao.id))
    return ConfiguracaoIngressoEventoRead(
        id=int(configuracao.id),
        evento_id=int(configuracao.evento_id),
        modo_fornecimento=configuracao.modo_fornecimento,
        tipos_ingresso=sorted((item.tipo_ingresso for item in tipos), key=lambda item: item.value),
        created_at=configuracao.created_at,
        updated_at=configuracao.updated_at,
    )


def _get_config_or_404(session: Session, evento_id: int) -> ConfiguracaoIngressoEvento:
    configuracao = session.exec(
        select(ConfiguracaoIngressoEvento).where(ConfiguracaoIngressoEvento.evento_id == evento_id)
    ).first()
    if configuracao is None:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="CONFIGURACAO_INGRESSO_NOT_FOUND",
            message="Configuracao de ingressos nao encontrada para o evento",
        )
    return configuracao


def _replace_config_tipos(
    session: Session, configuracao_id: int, tipos_ingresso: list[TipoIngresso]
) -> None:
    session.exec(
        sa_delete(ConfiguracaoIngressoEventoTipo).where(
            ConfiguracaoIngressoEventoTipo.configuracao_id == configuracao_id
        )
    )
    for tipo_ingresso in tipos_ingresso:
        session.add(
            ConfiguracaoIngressoEventoTipo(
                configuracao_id=configuracao_id,
                tipo_ingresso=tipo_ingresso,
            )
        )


def _ensure_diretoria_exists(session: Session, diretoria_id: int) -> None:
    if session.get(Diretoria, diretoria_id) is None:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="DIRETORIA_NOT_FOUND",
            message="Diretoria nao encontrada",
        )


def _ensure_tipo_ingresso_ativo(
    session: Session, configuracao_id: int, tipo_ingresso: TipoIngresso
) -> None:
    ativo = session.exec(
        select(ConfiguracaoIngressoEventoTipo.id).where(
            ConfiguracaoIngressoEventoTipo.configuracao_id == configuracao_id,
            ConfiguracaoIngressoEventoTipo.tipo_ingresso == tipo_ingresso,
        )
    ).first()
    if ativo is None:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="TIPO_INGRESSO_INVALID_FOR_EVENT",
            message="Tipo de ingresso nao esta ativo para o evento",
        )


@router.post(
    "/eventos/{evento_id}/configuracao",
    response_model=ConfiguracaoIngressoEventoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_configuracao_ingresso_evento(
    evento_id: int,
    payload: ConfiguracaoIngressoEventoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)

    existing = session.exec(
        select(ConfiguracaoIngressoEvento.id).where(ConfiguracaoIngressoEvento.evento_id == evento_id)
    ).first()
    if existing is not None:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="CONFIGURACAO_INGRESSO_DUPLICATE",
            message="Evento ja possui configuracao de ingressos",
        )

    configuracao = ConfiguracaoIngressoEvento(
        evento_id=evento_id,
        modo_fornecimento=payload.modo_fornecimento,
    )
    session.add(configuracao)

    try:
        session.flush()
        _replace_config_tipos(session, int(configuracao.id), payload.tipos_ingresso)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="CONFIGURACAO_INGRESSO_DUPLICATE",
            message="Evento ja possui configuracao de ingressos",
        )

    session.refresh(configuracao)
    return _serialize_config(session, configuracao)


@router.get(
    "/eventos/{evento_id}/configuracao",
    response_model=ConfiguracaoIngressoEventoRead,
)
def obter_configuracao_ingresso_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)
    return _serialize_config(session, configuracao)


@router.patch(
    "/eventos/{evento_id}/configuracao",
    response_model=ConfiguracaoIngressoEventoRead,
)
def atualizar_configuracao_ingresso_evento(
    evento_id: int,
    payload: ConfiguracaoIngressoEventoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)

    effective_fields = {
        field_name
        for field_name in payload.model_fields_set
        if getattr(payload, field_name) is not None
    }
    if not effective_fields:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR_NO_FIELDS",
            message="Nenhum campo para atualizar",
        )

    changed = False
    if "modo_fornecimento" in effective_fields:
        novo_modo = payload.modo_fornecimento
        assert novo_modo is not None
        if novo_modo != configuracao.modo_fornecimento:
            session.add(
                AuditoriaIngressoEvento(
                    evento_id=evento_id,
                    modo_fornecimento_anterior=configuracao.modo_fornecimento,
                    modo_fornecimento_novo=novo_modo,
                    usuario_id=getattr(current_user, "id", None),
                )
            )
            configuracao.modo_fornecimento = novo_modo
            changed = True

    if "tipos_ingresso" in effective_fields:
        assert payload.tipos_ingresso is not None
        _replace_config_tipos(session, int(configuracao.id), payload.tipos_ingresso)
        changed = True

    if changed:
        configuracao.updated_at = now_utc()
        session.add(configuracao)

    session.commit()
    session.refresh(configuracao)
    return _serialize_config(session, configuracao)


@router.post(
    "/eventos/{evento_id}/previsoes",
    response_model=PrevisaoIngressoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_ou_atualizar_previsao_ingresso(
    evento_id: int,
    payload: PrevisaoIngressoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)
    _ensure_diretoria_exists(session, payload.diretoria_id)
    _ensure_tipo_ingresso_ativo(session, int(configuracao.id), payload.tipo_ingresso)

    previsao = session.exec(
        select(PrevisaoIngresso).where(
            PrevisaoIngresso.evento_id == evento_id,
            PrevisaoIngresso.diretoria_id == payload.diretoria_id,
            PrevisaoIngresso.tipo_ingresso == payload.tipo_ingresso,
        )
    ).first()

    if previsao is None:
        previsao = PrevisaoIngresso(
            evento_id=evento_id,
            diretoria_id=payload.diretoria_id,
            tipo_ingresso=payload.tipo_ingresso,
            quantidade=payload.quantidade,
        )
        session.add(previsao)
    else:
        previsao.quantidade = payload.quantidade
        previsao.updated_at = now_utc()
        session.add(previsao)

    session.commit()
    session.refresh(previsao)
    return PrevisaoIngressoRead.model_validate(previsao)


@router.get(
    "/eventos/{evento_id}/previsoes",
    response_model=list[PrevisaoIngressoRead],
)
def listar_previsoes_ingresso(
    evento_id: int,
    diretoria_id: int | None = Query(None, ge=1),
    tipo_ingresso: TipoIngresso | None = Query(None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    _get_config_or_404(session, evento_id)

    query = select(PrevisaoIngresso).where(PrevisaoIngresso.evento_id == evento_id)
    if diretoria_id is not None:
        query = query.where(PrevisaoIngresso.diretoria_id == diretoria_id)
    if tipo_ingresso is not None:
        query = query.where(PrevisaoIngresso.tipo_ingresso == tipo_ingresso)

    rows = session.exec(
        query.order_by(
            PrevisaoIngresso.diretoria_id,
            PrevisaoIngresso.tipo_ingresso,
            PrevisaoIngresso.id,
        )
    ).all()
    return [PrevisaoIngressoRead.model_validate(row) for row in rows]
