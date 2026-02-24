"""Placeholder mapping loader for Word report generation.

This module defines and validates the configuration contract that maps DOCX
placeholders to `mart_report_*` views, avoiding hardcoded query/render links.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re
from typing import Any, Mapping

import yaml


DEFAULT_PLACEHOLDERS_MAPPING_PATH = (
    Path(__file__).resolve().parent / "config" / "word_placeholders.yml"
)
_PLACEHOLDER_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:__[A-Z0-9]+){1,}$")
_MART_NAME_RE = re.compile(r"^mart_report_[a-z0-9_]+$")
_PARAM_KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class PlaceholderRenderType(str, Enum):
    """Supported render output types for one placeholder mapping."""

    TEXT = "text"
    TABLE = "table"
    FIGURE = "figure"


class PlaceholderMappingError(ValueError):
    """Raised when placeholder mapping YAML is invalid."""


def is_valid_mart_name(value: str) -> bool:
    """Return whether a mart name follows mapping convention.

    Args:
        value: Mart/view name candidate.

    Returns:
        `True` when value matches `mart_report_*` naming pattern.
    """

    return bool(_MART_NAME_RE.match(str(value or "").strip()))


def ensure_mart_name(value: str) -> str:
    """Validate and return one mart/view name.

    Args:
        value: Mart/view name candidate.

    Returns:
        Normalized mart/view name.

    Raises:
        PlaceholderMappingError: If mart name is invalid.
    """

    clean = str(value or "").strip()
    if not is_valid_mart_name(clean):
        raise PlaceholderMappingError(
            f"mart_name invalido '{clean}'. Como corrigir: usar nome com prefixo mart_report_."
        )
    return clean


@dataclass(frozen=True)
class WordPlaceholderBinding:
    """One placeholder-to-mart contract item.

    Args:
        placeholder_id: Placeholder identifier in template.
        mart_name: Source mart/view (`mart_report_*`).
        params: Optional static parameters passed to query/render layer.
        render_type: Target render mode (`text`/`table`/`figure`).
        spec_item: Optional reference to DOCX spec item.
        description: Optional note explaining intent.
    """

    placeholder_id: str
    mart_name: str
    params: dict[str, Any]
    render_type: PlaceholderRenderType
    spec_item: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize binding to a JSON-friendly dictionary.

        Returns:
            Dictionary preserving the mapping contract fields.
        """

        return {
            "placeholder_id": self.placeholder_id,
            "mart_name": self.mart_name,
            "params": dict(self.params),
            "render_type": self.render_type.value,
            "spec_item": self.spec_item,
            "description": self.description,
        }


@dataclass(frozen=True)
class WordPlaceholdersMapping:
    """Root placeholder mapping contract loaded from YAML.

    Args:
        version: Mapping version.
        placeholders: Placeholder bindings list.
    """

    version: int
    placeholders: tuple[WordPlaceholderBinding, ...]

    def by_id(self, placeholder_id: str) -> WordPlaceholderBinding:
        """Return one binding by placeholder id.

        Args:
            placeholder_id: Target placeholder identifier.

        Returns:
            Matching placeholder binding.

        Raises:
            KeyError: If placeholder does not exist in mapping.
        """

        for item in self.placeholders:
            if item.placeholder_id == placeholder_id:
                return item
        raise KeyError(placeholder_id)

    def to_dict(self) -> dict[str, Any]:
        """Serialize full mapping contract to dictionary.

        Returns:
            Dictionary with version and placeholder items.
        """

        return {
            "version": int(self.version),
            "placeholders": [item.to_dict() for item in self.placeholders],
        }


def _ensure_mapping(value: Any, *, path: str) -> Mapping[str, Any]:
    """Validate that a YAML node is a mapping.

    Args:
        value: Node value parsed from YAML.
        path: JSON-like source path for error context.

    Returns:
        Mapping node.

    Raises:
        PlaceholderMappingError: If node is not a mapping.
    """

    if isinstance(value, Mapping):
        return value
    raise PlaceholderMappingError(
        f"{path}: esperado objeto YAML. Como corrigir: usar estrutura chave: valor."
    )


def _require_str(mapping: Mapping[str, Any], field: str, *, path: str) -> str:
    """Read one required non-empty string field from mapping.

    Args:
        mapping: Source node mapping.
        field: Field name.
        path: Node path for error reporting.

    Returns:
        Stripped field value.

    Raises:
        PlaceholderMappingError: If field is missing or invalid.
    """

    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise PlaceholderMappingError(
            f"{path}.{field}: campo obrigatorio ausente/vazio. "
            "Como corrigir: informar texto nao vazio."
        )
    return value.strip()


def _validate_placeholder_id(value: str, *, path: str) -> str:
    """Validate placeholder naming convention.

    Args:
        value: Placeholder id candidate.
        path: Source path for error context.

    Returns:
        Valid placeholder id.

    Raises:
        PlaceholderMappingError: If naming convention is not respected.
    """

    if not _PLACEHOLDER_ID_RE.match(value):
        raise PlaceholderMappingError(
            f"{path}: placeholder_id invalido '{value}'. "
            "Como corrigir: usar <SECAO>__<BLOCO>__<TIPO> em UPPER_SNAKE_CASE."
        )
    return value


def _validate_mart_name(value: str, *, path: str) -> str:
    """Validate mart/view name convention.

    Args:
        value: Mart name candidate.
        path: Source path for error context.

    Returns:
        Valid mart name.

    Raises:
        PlaceholderMappingError: If mart name is outside expected pattern.
    """

    try:
        return ensure_mart_name(value)
    except PlaceholderMappingError as exc:
        raise PlaceholderMappingError(f"{path}: {exc}") from exc


def _validate_render_type(value: str, *, path: str) -> PlaceholderRenderType:
    """Parse and validate render type enum.

    Args:
        value: Render type string.
        path: Source path for error context.

    Returns:
        Parsed `PlaceholderRenderType`.

    Raises:
        PlaceholderMappingError: If render type is unsupported.
    """

    try:
        return PlaceholderRenderType(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in PlaceholderRenderType)
        raise PlaceholderMappingError(
            f"{path}: render_type invalido '{value}'. Como corrigir: usar {allowed}."
        ) from exc


def _validate_params(raw: Any, *, path: str) -> dict[str, Any]:
    """Validate optional params dictionary for one placeholder.

    Args:
        raw: Raw params node from YAML.
        path: Source path for error context.

    Returns:
        Validated params dictionary.

    Raises:
        PlaceholderMappingError: If params format or value types are invalid.
    """

    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise PlaceholderMappingError(
            f"{path}: params deve ser objeto YAML. Como corrigir: usar chave: valor."
        )

    params: dict[str, Any] = {}
    for key, value in raw.items():
        key_text = str(key).strip()
        if not _PARAM_KEY_RE.match(key_text):
            raise PlaceholderMappingError(
                f"{path}.{key}: chave de parametro invalida. "
                "Como corrigir: usar snake_case iniciando com letra."
            )
        if isinstance(value, (str, int, float, bool)) or value is None:
            params[key_text] = value
            continue
        if isinstance(value, list):
            if not all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
                raise PlaceholderMappingError(
                    f"{path}.{key_text}: lista de parametro invalida. "
                    "Como corrigir: usar lista com apenas string/int/float/bool/null."
                )
            params[key_text] = list(value)
            continue
        raise PlaceholderMappingError(
            f"{path}.{key_text}: tipo de parametro invalido ({type(value).__name__}). "
            "Como corrigir: usar apenas string/int/float/bool/null ou lista desses tipos."
        )
    return params


def load_placeholders_mapping(
    path: Path | str = DEFAULT_PLACEHOLDERS_MAPPING_PATH,
) -> WordPlaceholdersMapping:
    """Load and validate placeholder mapping YAML.

    Args:
        path: YAML mapping path. Defaults to bundled config file.

    Returns:
        Parsed and validated `WordPlaceholdersMapping`.

    Raises:
        FileNotFoundError: If mapping path does not exist.
        PlaceholderMappingError: If mapping schema is invalid.
    """

    mapping_path = Path(path)
    if not mapping_path.exists():
        raise FileNotFoundError(f"Arquivo de mapping nao encontrado: {mapping_path}")

    raw = yaml.safe_load(mapping_path.read_text(encoding="utf-8")) or {}
    root = _ensure_mapping(raw, path="$")

    version_raw = root.get("version", 1)
    try:
        version = int(version_raw)
    except (TypeError, ValueError) as exc:
        raise PlaceholderMappingError(
            "$.version: valor invalido. Como corrigir: usar inteiro positivo."
        ) from exc
    if version <= 0:
        raise PlaceholderMappingError(
            "$.version: valor invalido. Como corrigir: usar inteiro positivo."
        )

    placeholders_raw = root.get("placeholders")
    if not isinstance(placeholders_raw, list) or not placeholders_raw:
        raise PlaceholderMappingError(
            "$.placeholders: lista obrigatoria e nao vazia. "
            "Como corrigir: adicionar ao menos um placeholder."
        )

    placeholders: list[WordPlaceholderBinding] = []
    seen_ids: set[str] = set()
    for idx, item_raw in enumerate(placeholders_raw):
        node_path = f"$.placeholders[{idx}]"
        item = _ensure_mapping(item_raw, path=node_path)
        placeholder_id = _validate_placeholder_id(
            _require_str(item, "placeholder_id", path=node_path),
            path=f"{node_path}.placeholder_id",
        )
        if placeholder_id in seen_ids:
            raise PlaceholderMappingError(
                f"{node_path}.placeholder_id: duplicado '{placeholder_id}'. "
                "Como corrigir: usar identificador unico por placeholder."
            )
        seen_ids.add(placeholder_id)

        mart_name = _validate_mart_name(
            _require_str(item, "mart_name", path=node_path),
            path=f"{node_path}.mart_name",
        )
        render_type = _validate_render_type(
            _require_str(item, "render_type", path=node_path),
            path=f"{node_path}.render_type",
        )
        params = _validate_params(item.get("params"), path=f"{node_path}.params")

        spec_item = item.get("spec_item")
        if spec_item is not None:
            spec_item = str(spec_item).strip() or None
        description = item.get("description")
        if description is not None:
            description = str(description).strip() or None

        placeholders.append(
            WordPlaceholderBinding(
                placeholder_id=placeholder_id,
                mart_name=mart_name,
                params=params,
                render_type=render_type,
                spec_item=spec_item,
                description=description,
            )
        )

    return WordPlaceholdersMapping(version=version, placeholders=tuple(placeholders))
