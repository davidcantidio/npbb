"""Helpers compartilhados entre os subrouters de eventos."""

from __future__ import annotations

from datetime import date

from fastapi import status
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import Evento, StatusEvento, Usuario, UsuarioTipo
from app.services.landing_pages import normalize_template_override_input
from app.utils.http_errors import raise_http_error


def _raise_http(status_code: int, code: str, message: str, extra: dict | None = None) -> None:
    raise_http_error(status_code, code=code, message=message, extra=extra)


def _apply_visibility(query, current_user: Usuario):
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            _raise_http(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                extra={"field": "agencia_id"},
            )
        return query.where(Evento.agencia_id == current_user.agencia_id)
    return query


def _check_evento_visible_or_404(
    session: Session, evento_id: int, current_user: Usuario
) -> Evento:
    evento = session.get(Evento, evento_id)
    if not evento:
        _raise_http(
            status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado"
        )
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            _raise_http(
                status.HTTP_404_NOT_FOUND, code="EVENTO_NOT_FOUND", message="Evento nao encontrado"
            )
    return evento


def _validate_fk(session: Session, model_cls, obj_id: int | None, code: str, message: str) -> None:
    if obj_id is None:
        return
    if not session.get(model_cls, obj_id):
        _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)


def _normalize_str(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _normalize_estado(value: str | None) -> str | None:
    text = _normalize_str(value)
    return text.upper() if text else None


def _normalize_template_override_or_error(value: str | None) -> str | None:
    normalized = normalize_template_override_input(value)
    if value is not None and str(value).strip() and normalized is None:
        _raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="LANDING_TEMPLATE_OVERRIDE_INVALID",
            message="template_override fora do catalogo homologado",
        )
    return normalized


STATUS_PREVISTO = "Previsto"
STATUS_A_CONFIRMAR = "A Confirmar"
STATUS_CONFIRMADO = "Confirmado"
STATUS_REALIZADO = "Realizado"
STATUS_CANCELADO = "Cancelado"


def _infer_status_nome(data_inicio_prevista: date | None, data_fim_prevista: date | None) -> str:
    """Infere o nome do status quando o cliente nao envia `status_id`."""
    today = date.today()
    if data_inicio_prevista and data_inicio_prevista > today:
        return STATUS_PREVISTO
    if data_fim_prevista and data_fim_prevista < today:
        return STATUS_REALIZADO
    if data_inicio_prevista and data_inicio_prevista <= today:
        return STATUS_CONFIRMADO
    return STATUS_A_CONFIRMAR


def _get_status_id_by_nome(session: Session, nome: str) -> int:
    row = session.exec(
        select(StatusEvento).where(func.lower(StatusEvento.nome) == nome.lower())
    ).first()
    if not row or row.id is None:
        _raise_http(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="STATUS_NOT_CONFIGURED",
            message=f"Status '{nome}' nao configurado no banco",
        )
    return row.id


def _normalize_unique_ids(values: list[int] | None, *, code: str, message: str) -> list[int]:
    if not values:
        return []
    unique: list[int] = []
    seen: set[int] = set()
    for raw in values:
        try:
            value = int(raw)
        except (TypeError, ValueError):
            _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)
        if value < 1:
            _raise_http(status.HTTP_400_BAD_REQUEST, code=code, message=message)
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return unique
