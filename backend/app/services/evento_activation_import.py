"""Helpers para elegibilidade de importacao por ativacao."""

from __future__ import annotations

from app.models.models import Evento


ACTIVATION_IMPORT_REQUIRES_AGENCY_CODE = "EVENTO_AGENCIA_REQUIRED_FOR_ATIVACAO_IMPORT"
ACTIVATION_IMPORT_REQUIRES_AGENCY_MESSAGE = (
    "Vincule uma agencia ao evento antes de importar leads de ativacao."
)


def get_activation_import_block_reason_from_agencia_id(agencia_id: int | None) -> str | None:
    if agencia_id is None:
        return ACTIVATION_IMPORT_REQUIRES_AGENCY_MESSAGE
    return None


def get_activation_import_block_reason(evento: Evento) -> str | None:
    return get_activation_import_block_reason_from_agencia_id(evento.agencia_id)


def supports_activation_import(evento: Evento) -> bool:
    return get_activation_import_block_reason(evento) is None
