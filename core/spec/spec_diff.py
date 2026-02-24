"""Diff utilities for comparing two extracted DOCX specs.

The goal is to summarize structural changes (sections, figures, tables) between
template versions so downstream impacts can be reviewed before deployment.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

from .spec_models import DocxFigure, DocxSection, DocxSpec, DocxTable


def _normalize_text(text: str) -> str:
    """Normalize text for stable, case-insensitive comparisons."""
    return " ".join((text or "").strip().casefold().split())


def _table_signature(table: DocxTable) -> str:
    """Build a readable table signature for diff reporting."""
    section = (table.section_title or "Sem secao").strip()
    headers = [h.strip() for h in table.header_cells if h.strip()]
    if headers:
        return f"{section} | cols={table.n_cols} | headers={', '.join(headers)}"
    return f"{section} | cols={table.n_cols} | sem cabecalho"


def _counter_with_display(items: Iterable[str]) -> Tuple[Counter[str], Dict[str, str]]:
    """Build normalized counters plus display labels."""
    counter: Counter[str] = Counter()
    display_by_key: Dict[str, str] = {}
    for item in items:
        display = (item or "").strip()
        if not display:
            continue
        key = _normalize_text(display)
        counter[key] += 1
        display_by_key.setdefault(key, display)
    return counter, display_by_key


def _fmt_count(label: str, amount: int) -> str:
    """Format label with multiplicity suffix when needed."""
    if amount <= 1:
        return label
    return f"{label} (x{amount})"


def _diff_grouped(old_items: Sequence[str], new_items: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Return grouped added/removed lists between old and new item sequences."""
    old_counter, old_display = _counter_with_display(old_items)
    new_counter, new_display = _counter_with_display(new_items)

    added: List[str] = []
    removed: List[str] = []
    all_keys = sorted(set(old_counter) | set(new_counter))
    for key in all_keys:
        old_count = old_counter.get(key, 0)
        new_count = new_counter.get(key, 0)
        if new_count > old_count:
            label = new_display.get(key) or old_display.get(key) or key
            added.append(_fmt_count(label, new_count - old_count))
        elif old_count > new_count:
            label = old_display.get(key) or new_display.get(key) or key
            removed.append(_fmt_count(label, old_count - new_count))
    return added, removed


@dataclass(frozen=True)
class DiffReport:
    """Summary of structural changes between two DOCX specs."""

    old_source: str
    new_source: str
    sections_added: List[str]
    sections_removed: List[str]
    figures_added: List[str]
    figures_removed: List[str]
    tables_added: List[str]
    tables_removed: List[str]

    def model_dump(self) -> dict:
        """Serialize report as JSON-friendly dict."""
        return {
            "old_source": self.old_source,
            "new_source": self.new_source,
            "sections": {
                "added": list(self.sections_added),
                "removed": list(self.sections_removed),
            },
            "figures": {
                "added": list(self.figures_added),
                "removed": list(self.figures_removed),
            },
            "tables": {
                "added": list(self.tables_added),
                "removed": list(self.tables_removed),
            },
        }


def _section_titles(spec: DocxSpec) -> List[str]:
    """Extract comparable section titles from spec."""
    return [section.title for section in spec.sections if section.title.strip()]


def _figure_captions(spec: DocxSpec) -> List[str]:
    """Extract comparable figure captions from spec."""
    return [figure.caption for figure in spec.figures if figure.caption.strip()]


def _table_signatures(spec: DocxSpec) -> List[str]:
    """Extract comparable table signatures from spec."""
    return [_table_signature(table) for table in spec.tables]


def diff_specs(old: DocxSpec, new: DocxSpec) -> DiffReport:
    """Compute structural diff between two extracted DOCX specs.

    Args:
        old: Old spec baseline.
        new: New spec candidate.

    Returns:
        A `DiffReport` listing added and removed sections, figures and tables.
    """
    sections_added, sections_removed = _diff_grouped(_section_titles(old), _section_titles(new))
    figures_added, figures_removed = _diff_grouped(_figure_captions(old), _figure_captions(new))
    tables_added, tables_removed = _diff_grouped(_table_signatures(old), _table_signatures(new))
    return DiffReport(
        old_source=old.source_path,
        new_source=new.source_path,
        sections_added=sections_added,
        sections_removed=sections_removed,
        figures_added=figures_added,
        figures_removed=figures_removed,
        tables_added=tables_added,
        tables_removed=tables_removed,
    )


def render_diff_json(report: DiffReport) -> str:
    """Render `DiffReport` to JSON text."""
    return json.dumps(report.model_dump(), ensure_ascii=False, indent=2)


def render_diff_markdown(report: DiffReport) -> str:
    """Render `DiffReport` to markdown summary."""
    lines: List[str] = []
    lines.append("# Spec Diff Summary")
    lines.append("")
    lines.append(f"- `old_source`: `{report.old_source}`")
    lines.append(f"- `new_source`: `{report.new_source}`")
    lines.append("")

    def _render_block(title: str, added: Sequence[str], removed: Sequence[str]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Tipo | Item |")
        lines.append("|---|---|")
        if not added and not removed:
            lines.append("| sem_alteracao | - |")
            lines.append("")
            return
        for item in added:
            lines.append(f"| adicionado | {item} |")
        for item in removed:
            lines.append(f"| removido | {item} |")
        lines.append("")

    _render_block("Secoes", report.sections_added, report.sections_removed)
    _render_block("Figuras", report.figures_added, report.figures_removed)
    _render_block("Tabelas", report.tables_added, report.tables_removed)
    return "\n".join(lines)

