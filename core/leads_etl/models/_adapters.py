"""Payload adapters for canonical lead-row materialization."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ._errors import LeadRowAdapterError
from ._field_catalog import (
    ETL_ALIAS_TO_LEAD_ROW_FIELD,
    ETL_FORBIDDEN_FIELDS,
    LEAD_ROW_EXCLUDED_FIELDS,
    LEAD_ROW_FIELDS,
)


_ALLOWED_FIELDS = set(LEAD_ROW_FIELDS)
_EXCLUDED_FIELDS = set(LEAD_ROW_EXCLUDED_FIELDS)
_FORBIDDEN_ETL_FIELDS = set(ETL_FORBIDDEN_FIELDS)


def _ensure_mapping_payload(payload: Mapping[str, Any] | Any, *, source: str) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    raise LeadRowAdapterError(
        source=source,
        message="Payload deve ser um mapping para materializar LeadRow.",
    )


def _adapt_payload(
    payload: Mapping[str, Any],
    *,
    source: str,
    alias_map: Mapping[str, str],
    forbidden_keys: set[str] | None = None,
) -> dict[str, Any]:
    adapted: dict[str, Any] = {}
    unknown_keys: list[str] = []
    excluded_keys: list[str] = []
    seen_from: dict[str, str] = {}

    if forbidden_keys:
        invalid_forbidden = sorted(set(payload).intersection(forbidden_keys))
        if invalid_forbidden:
            raise LeadRowAdapterError(
                source=source,
                message=(
                    "Payload contem metadados de staging/canonical que nao pertencem "
                    "ao contrato de entrada de lead."
                ),
                invalid_keys=invalid_forbidden,
            )

    for raw_key, value in payload.items():
        canonical_key = alias_map.get(raw_key, raw_key)
        if canonical_key in _EXCLUDED_FIELDS:
            excluded_keys.append(raw_key)
            continue
        if canonical_key not in _ALLOWED_FIELDS:
            unknown_keys.append(raw_key)
            continue
        previous_source = seen_from.get(canonical_key)
        if previous_source and previous_source != raw_key:
            raise LeadRowAdapterError(
                source=source,
                message="Payload gera colisao de aliases para o mesmo campo canonico.",
                invalid_keys=(previous_source, raw_key),
            )
        seen_from[canonical_key] = raw_key
        adapted[canonical_key] = value

    if excluded_keys:
        raise LeadRowAdapterError(
            source=source,
            message="Payload tenta enviar campos de persistencia ou derivados fora do contrato.",
            invalid_keys=excluded_keys,
        )

    if unknown_keys:
        raise LeadRowAdapterError(
            source=source,
            message="Payload contem campos fora do inventario canonico de LeadRow.",
            invalid_keys=unknown_keys,
        )
    return adapted


def adapt_backend_payload(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Normalize a backend-oriented payload into canonical LeadRow kwargs."""

    mapping = _ensure_mapping_payload(payload, source="backend")
    return _adapt_payload(mapping, source="backend", alias_map={})


def adapt_etl_payload(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Normalize an ETL-oriented payload into canonical LeadRow kwargs."""

    mapping = _ensure_mapping_payload(payload, source="etl")
    adapted = _adapt_payload(
        mapping,
        source="etl",
        alias_map=ETL_ALIAS_TO_LEAD_ROW_FIELD,
        forbidden_keys=_FORBIDDEN_ETL_FIELDS,
    )
    if not adapted:
        raise LeadRowAdapterError(
            source="etl",
            message="Payload ETL nao contem campos semanticamente compativeis com LeadRow.",
        )
    return adapted
