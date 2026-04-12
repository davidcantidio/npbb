"""Ingressos v2 configuration, receipts, and inventory endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.ingressos_v2_models import (
    AuditoriaDesbloqueioInventario,
    AuditoriaIngressoEvento,
    ConfiguracaoIngressoEvento,
    ConfiguracaoIngressoEventoTipo,
    InventarioIngresso,
    PrevisaoIngresso,
    RecebimentoIngresso,
)
from app.models.models import Diretoria, TipoIngresso, Usuario, now_utc
from app.platform.security.rbac import require_npbb_user
from app.routers.eventos import _shared as eventos_shared
from app.schemas.ingressos_v2 import (
    ConfiguracaoIngressoEventoCreate,
    ConfiguracaoIngressoEventoRead,
    ConfiguracaoIngressoEventoUpdate,
    DesbloqueioManualInventarioCreate,
    DesbloqueioManualInventarioResponse,
    InventarioIngressoRead,
    PrevisaoIngressoCreate,
    PrevisaoIngressoRead,
    RecebimentoIngressoCreate,
    RecebimentoIngressoRead,
    RecebimentoIngressoResponse,
)
from app.services.inventario_ingressos import (
    MSG_CONFIG_NOT_FOUND,
    MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO,
    MSG_DESBLOQUEIO_MODO_INVALIDO,
    MSG_DESBLOQUEIO_MOTIVO_OBRIGATORIO,
    MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA,
    MSG_DESBLOQUEIO_SEM_BLOQUEIO,
    MSG_DESBLOQUEIO_USUARIO_OBRIGATORIO,
    MSG_RECEBIMENTO_MODO_INVALIDO,
    MSG_RECEBIMENTO_QUANTIDADE_INVALIDA,
    MSG_TIPO_INATIVO,
    calcular_inventario,
    desbloqueio_manual,
    registrar_recebimento,
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


def _translate_inventario_service_error(exc: ValueError) -> None:
    message = str(exc)
    if message == MSG_CONFIG_NOT_FOUND:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="CONFIGURACAO_INGRESSO_NOT_FOUND",
            message=message,
        )
    if message == MSG_TIPO_INATIVO:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="TIPO_INGRESSO_INVALID_FOR_EVENT",
            message=message,
        )
    if message == MSG_RECEBIMENTO_QUANTIDADE_INVALIDA:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="RECEBIMENTO_QUANTIDADE_INVALIDA",
            message=message,
        )
    if message == MSG_RECEBIMENTO_MODO_INVALIDO:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="RECEBIMENTO_INVALID_MODE",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_QUANTIDADE_INVALIDA:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="DESBLOQUEIO_MANUAL_QUANTIDADE_INVALIDA",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_MODO_INVALIDO:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="DESBLOQUEIO_MANUAL_INVALID_MODE",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_MOTIVO_OBRIGATORIO:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="DESBLOQUEIO_MANUAL_MOTIVO_OBRIGATORIO",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_USUARIO_OBRIGATORIO:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="DESBLOQUEIO_MANUAL_USUARIO_OBRIGATORIO",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_SEM_BLOQUEIO:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="DESBLOQUEIO_MANUAL_SEM_BLOQUEIO",
            message=message,
        )
    if message == MSG_DESBLOQUEIO_EXCEDE_BLOQUEIO:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="DESBLOQUEIO_MANUAL_EXCEDE_BLOQUEIO",
            message=message,
        )
    raise_http_error(
        status.HTTP_400_BAD_REQUEST,
        code="INGRESSOS_V2_INVALID_OPERATION",
        message=message,
    )


def _serialize_recebimento_response(
    recebimento: RecebimentoIngresso, inventario: InventarioIngresso
) -> RecebimentoIngressoResponse:
    return RecebimentoIngressoResponse(
        recebimento=RecebimentoIngressoRead.model_validate(recebimento),
        inventario=InventarioIngressoRead.model_validate(inventario),
    )


def _serialize_desbloqueio_response(
    auditoria: AuditoriaDesbloqueioInventario, inventario: InventarioIngresso
) -> DesbloqueioManualInventarioResponse:
    return DesbloqueioManualInventarioResponse(
        auditoria_id=int(auditoria.id),
        evento_id=int(auditoria.evento_id),
        diretoria_id=int(auditoria.diretoria_id),
        tipo_ingresso=auditoria.tipo_ingresso,
        usuario_id=auditoria.usuario_id,
        quantidade=int(auditoria.quantidade),
        bloqueado_antes=int(auditoria.bloqueado_antes),
        bloqueado_depois=int(auditoria.bloqueado_depois),
        motivo=auditoria.motivo,
        correlation_id=auditoria.correlation_id,
        created_at=auditoria.created_at,
        inventario=InventarioIngressoRead.model_validate(inventario),
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
        if novo_modo is None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="VALIDATION_ERROR_INVALID_FIELD",
                message="modo_fornecimento nao pode ser nulo quando enviado",
            )
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
        if payload.tipos_ingresso is None:
            raise_http_error(
                status.HTTP_400_BAD_REQUEST,
                code="VALIDATION_ERROR_INVALID_FIELD",
                message="tipos_ingresso nao pode ser nulo quando enviado",
            )
        # Existing PrevisaoIngresso rows for removed tipos are intentionally kept:
        # they become inert (no new previsoes allowed) but remain for audit history.
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

    session.flush()
    calcular_inventario(
        session,
        evento_id=evento_id,
        diretoria_id=payload.diretoria_id,
        tipo_ingresso=payload.tipo_ingresso,
    )
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


@router.post(
    "/eventos/{evento_id}/recebimentos",
    response_model=RecebimentoIngressoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_recebimento_ingresso(
    evento_id: int,
    payload: RecebimentoIngressoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)
    _ensure_diretoria_exists(session, payload.diretoria_id)
    _ensure_tipo_ingresso_ativo(session, int(configuracao.id), payload.tipo_ingresso)

    try:
        recebimento, inventario = registrar_recebimento(
            session,
            evento_id=evento_id,
            diretoria_id=payload.diretoria_id,
            tipo_ingresso=payload.tipo_ingresso,
            quantidade=payload.quantidade,
            artifact_file_path=payload.artifact_file_path,
            artifact_link=payload.artifact_link,
            artifact_instructions=payload.artifact_instructions,
            correlation_id=payload.correlation_id,
        )
    except ValueError as exc:
        _translate_inventario_service_error(exc)

    session.commit()
    session.refresh(recebimento)
    session.refresh(inventario)
    return _serialize_recebimento_response(recebimento, inventario)


@router.get(
    "/eventos/{evento_id}/inventario",
    response_model=list[InventarioIngressoRead],
)
def listar_inventario_ingresso(
    evento_id: int,
    diretoria_id: int | None = Query(None, ge=1),
    tipo_ingresso: TipoIngresso | None = Query(None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)
    if diretoria_id is not None:
        _ensure_diretoria_exists(session, diretoria_id)
    if tipo_ingresso is not None:
        _ensure_tipo_ingresso_ativo(session, int(configuracao.id), tipo_ingresso)

    query = select(InventarioIngresso).where(InventarioIngresso.evento_id == evento_id)
    if diretoria_id is not None:
        query = query.where(InventarioIngresso.diretoria_id == diretoria_id)
    if tipo_ingresso is not None:
        query = query.where(InventarioIngresso.tipo_ingresso == tipo_ingresso)

    rows = session.exec(
        query.order_by(
            InventarioIngresso.diretoria_id,
            InventarioIngresso.tipo_ingresso,
            InventarioIngresso.id,
        )
    ).all()
    return [InventarioIngressoRead.model_validate(row) for row in rows]


@router.post(
    "/eventos/{evento_id}/inventario/desbloqueio-manual",
    response_model=DesbloqueioManualInventarioResponse,
)
def criar_desbloqueio_manual_inventario(
    evento_id: int,
    payload: DesbloqueioManualInventarioCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(require_npbb_user),
):
    eventos_shared._check_evento_visible_or_404(session, evento_id, current_user)
    configuracao = _get_config_or_404(session, evento_id)
    _ensure_diretoria_exists(session, payload.diretoria_id)
    _ensure_tipo_ingresso_ativo(session, int(configuracao.id), payload.tipo_ingresso)

    try:
        auditoria, inventario = desbloqueio_manual(
            session,
            evento_id=evento_id,
            diretoria_id=payload.diretoria_id,
            tipo_ingresso=payload.tipo_ingresso,
            quantidade=payload.quantidade,
            usuario_id=getattr(current_user, "id", None),
            motivo=payload.motivo,
            correlation_id=payload.correlation_id,
        )
    except ValueError as exc:
        _translate_inventario_service_error(exc)

    session.commit()
    session.refresh(auditoria)
    session.refresh(inventario)
    return _serialize_desbloqueio_response(auditoria, inventario)
