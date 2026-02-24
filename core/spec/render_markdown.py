"""Markdown renderer for the DOCX-as-spec checklist.

This module renders a deterministic checklist markdown so the DOCX structure can
be treated as a versioned data contract.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List

from .spec_models import (
    CHECKLIST_COLUMNS,
    MANDATORY_SHOWS_BY_DAY_ITEM,
    DocxChecklistRow,
    DocxSpec,
)


_LEADING_NUMBERING_RE = re.compile(r"^\s*\d+(?:\.\d+)*\s*[\).:-]?\s*")
_MULTISPACE_RE = re.compile(r"\s+")


def _to_ascii(text: str) -> str:
    """Best-effort ASCII conversion (remove diacritics, normalize punctuation)."""
    if not text:
        return ""
    # Normalize dashes BEFORE stripping non-ASCII, otherwise they're lost.
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    # Normalize unicode (remove diacritics)
    norm = unicodedata.normalize("NFKD", text)
    norm = "".join(ch for ch in norm if ord(ch) < 128)
    return norm


def sanitize_contract_text(text: str) -> str:
    """Sanitize text for planning/contract markdown.

    We normalize text and remove only structural numbering prefixes such as
    "4.1 " so section titles remain stable in the checklist.
    """
    s = _to_ascii(text)
    s = _LEADING_NUMBERING_RE.sub("", s)
    s = _MULTISPACE_RE.sub(" ", s).strip()
    # Remove trailing separators
    s = s.strip(" -:;,.")
    return s


def sanitize_figure_caption(caption: str) -> str:
    """Sanitize a figure caption for inventory display."""
    s = _to_ascii(caption)
    # Remove "Figura <n> -" prefix
    s = re.sub(r"^\s*Figura\s*\d+\s*[-:]\s*", "", s, flags=re.IGNORECASE)
    s = sanitize_contract_text(s)
    return s


def build_initial_checklist_rows(spec: DocxSpec) -> List[DocxChecklistRow]:
    """Build deterministic checklist rows from a DOCX spec.

    Args:
        spec: Extracted DOCX specification.

    Returns:
        Normalized checklist rows with initial status set to GAP.
    """
    rows: List[DocxChecklistRow] = []
    seen_sections = set()

    for section in spec.sections:
        if section.level not in (1, 2):
            continue
        title = sanitize_contract_text(section.title)
        if not title or title in seen_sections:
            continue
        seen_sections.add(title)
        rows.append(
            DocxChecklistRow(
                section=title,
                expected_content="TODO",
                granularity="TODO",
                required_fields="TODO",
                source_in_docx=f'Secao "{title}" (template DOCX)',
                status="GAP",
            )
        )

    if MANDATORY_SHOWS_BY_DAY_ITEM not in seen_sections:
        rows.append(
            DocxChecklistRow(
                section=MANDATORY_SHOWS_BY_DAY_ITEM,
                expected_content=(
                    "Para cada dia com show: entradas validadas, ingressos vendidos, "
                    "opt-in aceitos e reconciliacao entre metricas"
                ),
                granularity="Dia e sessao (show)",
                required_fields=(
                    "`event_sessions` (tipo=show), `attendance_access_control`, "
                    "`ticket_sales`, `optin_transactions`"
                ),
                source_in_docx="Requisito obrigatorio de governanca (feedback de cobertura)",
                status="GAP",
            )
        )

    return rows


def render_docx_as_spec_md(spec: DocxSpec) -> str:
    """Render a planning-friendly markdown checklist from an extracted DocxSpec.

    Args:
        spec: The extracted DocxSpec.

    Returns:
        Markdown checklist string ready to become `00_docx_as_spec.md`.
    """
    lines: List[str] = []
    lines.append("# DOCX Como Spec de Dados")
    lines.append("")
    lines.append(
        "Este arquivo transforma o documento modelo de fechamento em um checklist de requisitos de dados. "
        "A intencao e que cada item abaixo vire um ou mais campos/tabelas no banco, com regras de calculo "
        "e linhagem para as fontes."
    )
    lines.append("")

    # Checklist
    lines.append("## Checklist (Contrato de Dados)")
    lines.append("")
    lines.append("| " + " | ".join(CHECKLIST_COLUMNS) + " |")
    lines.append("|---|---|---|---|---|---|")
    for row in build_initial_checklist_rows(spec):
        lines.append(
            "| "
            + " | ".join(
                [
                    row.section,
                    row.expected_content,
                    row.granularity,
                    row.required_fields,
                    row.source_in_docx,
                    row.status,
                ]
            )
            + " |"
        )

    lines.append("")

    # Inventory
    lines.append("## Figuras e Tabelas (Inventario do DOCX)")
    lines.append("")
    lines.append("### Figuras (titulos)")
    lines.append("")
    if spec.figures:
        for fig in spec.figures:
            cap = sanitize_figure_caption(fig.caption)
            if cap:
                lines.append(f"- {cap}.")
    else:
        lines.append("- Sem figuras detectadas.")

    lines.append("")
    lines.append("### Tabelas")
    lines.append("")
    if spec.tables:
        for tbl in spec.tables:
            headers = [sanitize_contract_text(h) for h in tbl.header_cells if h.strip()]
            headers = [h for h in headers if h]
            section = sanitize_contract_text(tbl.section_title or "") or "Sem secao"
            if headers:
                fields = ", ".join(f"`{h}`" for h in headers)
                lines.append(f"- {section}: Campos esperados: {fields}.")
            else:
                lines.append(f"- {section}: Tabela sem cabecalho detectavel.")
    else:
        lines.append("- Sem tabelas detectadas.")

    lines.append("")
    return "\n".join(lines)
