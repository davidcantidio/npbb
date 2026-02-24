"""Models for the DOCX-as-spec extraction pipeline.

These dataclasses are designed to be:
- serializable (via `.model_dump()` helpers),
- stable (so we can diff changes between template versions),
- and simple enough to be used by both the extractor and the report generator.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


@dataclass(frozen=True)
class DocxSection:
    """A logical section extracted from headings (Heading 1/2/3...)."""

    level: int
    title: str
    body_lines: List[str]
    start_paragraph_index: int

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "level": self.level,
            "title": self.title,
            "body_lines": list(self.body_lines),
            "start_paragraph_index": self.start_paragraph_index,
        }


@dataclass(frozen=True)
class DocxFigure:
    """A figure caption extracted from the template (typically style: Caption)."""

    caption: str
    paragraph_index: int
    section_title: Optional[str]

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "caption": self.caption,
            "paragraph_index": self.paragraph_index,
            "section_title": self.section_title,
        }


@dataclass(frozen=True)
class DocxTable:
    """A table definition extracted from the template."""

    table_index: int
    n_rows: int
    n_cols: int
    header_cells: List[str]
    section_title: Optional[str]

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "table_index": self.table_index,
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "header_cells": list(self.header_cells),
            "section_title": self.section_title,
        }


@dataclass(frozen=True)
class DocxSpec:
    """Full extracted spec from a DOCX template."""

    source_path: str
    extracted_at: datetime
    sections: List[DocxSection]
    figures: List[DocxFigure]
    tables: List[DocxTable]

    @property
    def source_name(self) -> str:
        """Basename of the source document path."""
        return Path(self.source_path).name

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict (JSON-friendly)."""
        return {
            "source_path": self.source_path,
            "extracted_at": self.extracted_at.isoformat(),
            "sections": [s.model_dump() for s in self.sections],
            "figures": [f.model_dump() for f in self.figures],
            "tables": [t.model_dump() for t in self.tables],
        }


ChecklistStatus = Literal["OK", "GAP", "INCONSISTENTE"]
FindingSeverity = Literal["error", "warning", "info"]

CHECKLIST_COLUMNS: List[str] = [
    "Secao (DOCX)",
    "Metrica/Conteudo esperado",
    "Granularidade (evento/dia/sessao)",
    "Tabelas/campos necessarios",
    "Fonte atual no DOCX",
    "Status",
]

MANDATORY_SHOWS_BY_DAY_ITEM = "Shows por dia (12/12, 13/12, 14/12)"
SPEC_REQUIRED_SECTION_MISSING = "SPEC_REQUIRED_SECTION_MISSING"
SPEC_SECTION_DUPLICATE_TITLE = "SPEC_SECTION_DUPLICATE_TITLE"
SPEC_SECTION_AMBIGUOUS_TITLE = "SPEC_SECTION_AMBIGUOUS_TITLE"


@dataclass(frozen=True)
class DocxChecklistRow:
    """One normalized checklist row derived from the DOCX contract."""

    section: str
    expected_content: str
    granularity: str
    required_fields: str
    source_in_docx: str
    status: ChecklistStatus

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "section": self.section,
            "expected_content": self.expected_content,
            "granularity": self.granularity,
            "required_fields": self.required_fields,
            "source_in_docx": self.source_in_docx,
            "status": self.status,
        }


@dataclass(frozen=True)
class Finding:
    """Validation finding produced by spec/mapping quality gates."""

    severity: FindingSeverity
    code: str
    item_docx: str
    message: str
    reference: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "severity": self.severity,
            "code": self.code,
            "item_docx": self.item_docx,
            "message": self.message,
            "reference": self.reference,
        }
