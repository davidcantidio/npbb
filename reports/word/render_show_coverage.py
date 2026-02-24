"""Show-coverage section rendering helpers for Word reports.

This module renders the dedicated TMJ section "cobertura de shows por dia"
using the `mart_report_show_day_summary` payload contract, and appends an
explicit legend for status values OK/GAP/INCONSISTENTE.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from docx.document import Document as DocxDocument

from .render_table import render_table_placeholder


SHOW_COVERAGE_PLACEHOLDER_ID = "SHOW__COVERAGE__TABLE"
SHOW_COVERAGE_REQUIRED_COLUMNS = (
    "dia",
    "sessao",
    "status_access_control",
    "status_optin",
    "status_ticket_sales",
    "observacoes",
)
SHOW_COVERAGE_LEGEND_LINES = (
    "Legenda de status da cobertura de shows por dia:",
    "OK: dataset presente e carregado para a sessao.",
    "GAP: dataset ausente para a sessao esperada.",
    "INCONSISTENTE: dataset presente com conflito entre fontes ou regras.",
)


class ShowCoverageRenderError(ValueError):
    """Raised when show-coverage payload contract is invalid."""


def validate_show_coverage_columns(
    columns: Sequence[str],
    *,
    placeholder_id: str = SHOW_COVERAGE_PLACEHOLDER_ID,
) -> list[str]:
    """Validate and normalize columns for show-coverage table rendering.

    Args:
        columns: Output columns provided by mapping payload.
        placeholder_id: Placeholder identifier for error context.

    Returns:
        Normalized list of column names preserving input order.

    Raises:
        ShowCoverageRenderError: If required show-coverage columns are missing.
    """

    if not isinstance(columns, Sequence) or isinstance(columns, (str, bytes, bytearray)):
        raise ShowCoverageRenderError(
            f"Payload de cobertura de shows invalido para {placeholder_id}: "
            "columns deve ser list[str]."
        )

    normalized = [str(column).strip() for column in columns if str(column).strip()]
    missing = [column for column in SHOW_COVERAGE_REQUIRED_COLUMNS if column not in normalized]
    if missing:
        missing_text = ", ".join(missing)
        raise ShowCoverageRenderError(
            f"Payload de cobertura de shows invalido para {placeholder_id}: "
            f"faltam colunas obrigatorias ({missing_text})."
        )
    return normalized


def render_show_coverage_section(
    doc: DocxDocument,
    *,
    placeholder_id: str = SHOW_COVERAGE_PLACEHOLDER_ID,
    columns: Sequence[str],
    rows: Sequence[dict[str, Any] | Sequence[Any]],
    legend_lines: Sequence[str] = SHOW_COVERAGE_LEGEND_LINES,
) -> int:
    """Render show-coverage table section and append status legend.

    Args:
        doc: Open DOCX document.
        placeholder_id: Placeholder token id where table is rendered.
        columns: Output columns (must include show-coverage required fields).
        rows: Row payload to render.
        legend_lines: Legend lines appended to document after table rendering.

    Returns:
        Number of placeholder occurrences replaced by show-coverage tables.

    Raises:
        ShowCoverageRenderError: If coverage column contract is invalid.
        ValueError: Propagated from generic table renderer when payload is invalid.
    """

    normalized_columns = validate_show_coverage_columns(
        columns,
        placeholder_id=placeholder_id,
    )
    replacements = render_table_placeholder(
        doc,
        placeholder_id,
        columns=normalized_columns,
        rows=rows,
    )
    for line in legend_lines:
        line_text = str(line).strip()
        if line_text:
            doc.add_paragraph(line_text)
    return replacements
