"""Column-name normalization helpers for extractors.

This module keeps normalization deterministic across source types by:
- trimming and collapsing spaces,
- converting accents and punctuation to stable tokens,
- applying configurable alias mappings,
- and deduplicating collisions.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence
import unicodedata


_SPACE_RE = re.compile(r"\s+")
_NON_WORD_RE = re.compile(r"[^0-9A-Za-z_]+")
_UNDERSCORE_RE = re.compile(r"_+")


@dataclass(frozen=True)
class ColumnNormalizationConfig:
    """Configuration for canonical column-name normalization.

    Attributes:
        case: Output case strategy (`lower`, `upper`, `preserve`).
        replace_spaces_with: Token used to replace whitespace.
        strip_accents: If True, removes accents before punctuation cleanup.
        fallback_prefix: Prefix used for empty column names.
    """

    case: str = "lower"
    replace_spaces_with: str = "_"
    strip_accents: bool = True
    fallback_prefix: str = "col"


def _strip_accents(value: str) -> str:
    """Remove accents/diacritics from one string."""
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _apply_case(value: str, case: str) -> str:
    """Apply case strategy to a normalized string."""
    normalized_case = (case or "lower").strip().lower()
    if normalized_case == "upper":
        return value.upper()
    if normalized_case == "preserve":
        return value
    return value.lower()


def normalize_column_name(
    value: Any,
    *,
    config: ColumnNormalizationConfig | None = None,
) -> str:
    """Normalize one column name into a stable token.

    Args:
        value: Raw column name value.
        config: Optional normalization configuration.

    Returns:
        Normalized column name token.
    """

    cfg = config or ColumnNormalizationConfig()
    text = "" if value is None else str(value).strip()
    if cfg.strip_accents:
        text = _strip_accents(text)
    text = _SPACE_RE.sub(cfg.replace_spaces_with, text)
    text = _NON_WORD_RE.sub(cfg.replace_spaces_with, text)
    text = _UNDERSCORE_RE.sub("_", text)
    text = text.strip("_")
    return _apply_case(text, cfg.case)


def normalize_column_names(
    values: Sequence[Any],
    *,
    config: ColumnNormalizationConfig | None = None,
    aliases: Mapping[str, str] | None = None,
) -> list[str]:
    """Normalize a list of column names with aliasing and deduplication.

    Args:
        values: Raw column names.
        config: Optional normalization configuration.
        aliases: Optional map from normalized name to canonical name.

    Returns:
        Canonical and deduplicated column-name list.
    """

    cfg = config or ColumnNormalizationConfig()
    alias_map = aliases or {}
    counts: dict[str, int] = {}
    out: list[str] = []

    for index, raw in enumerate(values, start=1):
        normalized = normalize_column_name(raw, config=cfg)
        if not normalized:
            normalized = f"{cfg.fallback_prefix}_{index}"
        canonical = alias_map.get(normalized, normalized)
        seen = counts.get(canonical, 0)
        counts[canonical] = seen + 1
        if seen > 0:
            out.append(f"{canonical}_{seen + 1}")
        else:
            out.append(canonical)
    return out

