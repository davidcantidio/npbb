"""Contratos internos do core de importacao assistida."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ImportFieldSpec:
    name: str
    required: bool = False
    aliases: tuple[str, ...] = ()
    kind: str = "text"
    uppercase: bool = False


@dataclass(frozen=True)
class ImportDomainSpec:
    domain: str
    fields: tuple[ImportFieldSpec, ...]
    required_key_fields: tuple[str, ...] = ()
    alias_fields: tuple[str, ...] = ()

    def field_names(self) -> set[str]:
        return {f.name for f in self.fields}

    def field_map(self) -> dict[str, ImportFieldSpec]:
        return {f.name: f for f in self.fields}


@dataclass(frozen=True)
class ColumnSuggestion:
    coluna: str
    campo: Optional[str] = None
    confianca: Optional[float] = None


@dataclass(frozen=True)
class ImportValidationResult:
    ok: bool
    missing_required_fields: tuple[str, ...] = ()
    missing_required_key_fields: tuple[str, ...] = ()
    unknown_fields: tuple[str, ...] = ()
    duplicated_fields: tuple[str, ...] = ()


@dataclass
class ImportPreviewResult:
    filename: str
    headers: list[str]
    rows: list[list[str]]
    delimiter: str | None
    start_index: int
    sheet_name: Optional[str] = None
    suggestions: list[ColumnSuggestion] = field(default_factory=list)
    samples_by_column: list[list[str]] = field(default_factory=list)
    #: Linha física 1-based no ficheiro/aba, alinhada a `rows` (após filtrar linhas vazias).
    physical_line_numbers: list[int] = field(default_factory=list)
