"""Deterministic mapper for ticket category -> canonical BB segment.

This module provides a config-driven mapping contract to keep the relationship
proxy auditable and versioned in-repo.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
import unicodedata
from typing import Mapping

import yaml


class Segment(str, Enum):
    """Canonical relationship-segment domain used by TMJ ETL."""

    CLIENTE_BB = "CLIENTE_BB"
    CARTAO_BB = "CARTAO_BB"
    FUNCIONARIO_BB = "FUNCIONARIO_BB"
    PUBLICO_GERAL = "PUBLICO_GERAL"
    OUTRO = "OUTRO"
    DESCONHECIDO = "DESCONHECIDO"


@dataclass(frozen=True)
class SegmentMappingFinding:
    """Actionable finding when category mapping is unknown or invalid."""

    code: str
    message: str
    category_raw: str | None
    category_norm: str


@dataclass(frozen=True)
class SegmentMappingResult:
    """Output contract for one mapped ticket category."""

    category_raw: str | None
    category_norm: str
    segment: Segment
    finding: SegmentMappingFinding | None = None


class SegmentMappingError(ValueError):
    """Raised when mapping config is invalid."""


DEFAULT_MAPPING_PATH = Path(__file__).resolve().parent / "config" / "segment_mapping.yml"


def normalize_ticket_category(value: str | None) -> str:
    """Normalize raw ticket category to stable matching key.

    Args:
        value: Raw category label.

    Returns:
        Normalized ASCII uppercase label with collapsed spaces.
    """

    raw = str(value or "").strip()
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_only = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_only = ascii_only.upper()
    ascii_only = re.sub(r"[^A-Z0-9]+", " ", ascii_only)
    return re.sub(r"\s+", " ", ascii_only).strip()


def _coerce_segment(value: str) -> Segment:
    """Coerce one segment name into controlled enum."""

    name = str(value or "").strip().upper()
    try:
        return Segment[name]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise SegmentMappingError(
            f"Segmento invalido no mapping: {value!r}. "
            "Segmentos validos: CLIENTE_BB, CARTAO_BB, FUNCIONARIO_BB, "
            "PUBLICO_GERAL, OUTRO, DESCONHECIDO."
        ) from exc


def load_segment_mapping(
    path: Path | str | None = None,
) -> tuple[dict[str, Segment], Segment]:
    """Load segment mapping config from YAML file.

    Args:
        path: Optional path to mapping YAML file. Defaults to bundled config.

    Returns:
        Tuple containing:
        - normalized category -> segment mapping
        - default segment used for unknown categories

    Raises:
        SegmentMappingError: If config structure is invalid.
    """

    mapping_path = Path(path) if path is not None else DEFAULT_MAPPING_PATH
    data = yaml.safe_load(mapping_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
        raise SegmentMappingError("Arquivo de mapeamento deve ser um objeto YAML.")

    default_segment = _coerce_segment(str(data.get("default_segment", "DESCONHECIDO")))
    raw_mappings = data.get("mappings")
    if not isinstance(raw_mappings, Mapping):
        raise SegmentMappingError("Campo 'mappings' obrigatorio e deve ser objeto.")

    output: dict[str, Segment] = {}
    for segment_name, categories in raw_mappings.items():
        segment = _coerce_segment(str(segment_name))
        if not isinstance(categories, list):
            raise SegmentMappingError(
                f"Segmento {segment_name!r} deve conter lista de categorias."
            )
        for category in categories:
            norm = normalize_ticket_category(str(category))
            if not norm:
                continue
            output[norm] = segment
    return output, default_segment


def map_ticket_category_to_segment(
    value: str | None,
    *,
    mapping: dict[str, Segment] | None = None,
    default_segment: Segment | None = None,
) -> Segment:
    """Map one ticket category to canonical segment.

    Args:
        value: Raw ticket category.
        mapping: Optional preloaded mapping dictionary.
        default_segment: Optional fallback segment for unknown categories.

    Returns:
        Canonical segment value.
    """

    local_mapping, local_default = load_segment_mapping() if mapping is None else (mapping, default_segment)
    fallback = local_default if local_default is not None else Segment.DESCONHECIDO
    norm = normalize_ticket_category(value)
    if not norm:
        return fallback
    return local_mapping.get(norm, fallback)


def map_ticket_category_with_finding(
    value: str | None,
    *,
    mapping: dict[str, Segment] | None = None,
    default_segment: Segment | None = None,
) -> SegmentMappingResult:
    """Map one ticket category and emit finding for unknown mappings.

    Args:
        value: Raw ticket category.
        mapping: Optional preloaded mapping dictionary.
        default_segment: Optional fallback segment for unknown categories.

    Returns:
        Mapping result with optional finding when category is unknown.
    """

    local_mapping, local_default = load_segment_mapping() if mapping is None else (mapping, default_segment)
    fallback = local_default if local_default is not None else Segment.DESCONHECIDO
    norm = normalize_ticket_category(value)

    if norm and norm in local_mapping:
        return SegmentMappingResult(
            category_raw=value,
            category_norm=norm,
            segment=local_mapping[norm],
            finding=None,
        )

    finding = SegmentMappingFinding(
        code="SEGMENT_CATEGORY_UNKNOWN",
        message=(
            "Categoria de ingresso nao mapeada. Como corrigir: adicionar categoria "
            "no arquivo etl/transform/config/segment_mapping.yml."
        ),
        category_raw=value,
        category_norm=norm,
    )
    return SegmentMappingResult(
        category_raw=value,
        category_norm=norm,
        segment=fallback,
        finding=finding,
    )

