"""Build and render request lists for missing show artifacts.

This module converts show-coverage gaps into an actionable "what to request"
list with stable output contracts for Markdown/CSV.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import csv
import io
from typing import Iterable

from .show_coverage_evaluator import CoverageReport

try:  # pragma: no cover - import style depends on caller cwd
    from app.models.models import EventSessionType
except ModuleNotFoundError:  # pragma: no cover
    from pathlib import Path as _Path
    import sys as _sys

    BACKEND_ROOT = _Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in _sys.path:
        _sys.path.insert(0, str(BACKEND_ROOT))
    from app.models.models import EventSessionType


@dataclass(frozen=True)
class RequestItem:
    """One missing-artifact request row for show-day closure operations.

    Args:
        dia: Show day (`YYYY-MM-DD`).
        sessao: Canonical session key/name for operator action.
        dataset: Missing dataset (`access_control`, `optin`, `ticket_sales`).
        artefato_esperado: Expected source artifact description.
        justificativa: Objective reason for request generation.
    """

    dia: date
    sessao: str
    dataset: str
    artefato_esperado: str
    justificativa: str

    def to_dict(self) -> dict[str, str]:
        """Serialize request item into JSON/CSV-friendly mapping."""

        return {
            "dia": self.dia.isoformat(),
            "sessao": self.sessao,
            "dataset": self.dataset,
            "artefato_esperado": self.artefato_esperado,
            "justificativa": self.justificativa,
        }


def _normalize_focus_dates(focus_show_dates: Iterable[date] | None) -> set[date]:
    """Normalize optional focus date filter."""

    if focus_show_dates is None:
        return set()
    return {item for item in focus_show_dates}


def build_missing_artifacts_list(
    coverage_report: CoverageReport,
    *,
    include_partial: bool = False,
    focus_show_dates: Iterable[date] | None = None,
) -> list[RequestItem]:
    """Build request list from show-coverage missing inputs.

    Args:
        coverage_report: Coverage report returned by `evaluate_coverage`.
        include_partial: Include partial findings in addition to gaps.
        focus_show_dates: Optional date filter (for example: 12/12 and 14/12).

    Returns:
        Ordered list of request items with deterministic deduplication.
    """

    allowed_status = {"gap", "partial"} if include_partial else {"gap"}
    focus_dates = _normalize_focus_dates(focus_show_dates)

    rows: list[RequestItem] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for item in coverage_report.missing_inputs:
        if item.session_type != EventSessionType.NOTURNO_SHOW:
            continue
        if item.status not in allowed_status:
            continue
        if focus_dates and item.session_date not in focus_dates:
            continue

        justificativa = item.reason.strip()
        request_action = item.request_action.strip()
        if request_action:
            justificativa = f"{justificativa} Acao sugerida: {request_action}"

        request_item = RequestItem(
            dia=item.session_date,
            sessao=item.session_key,
            dataset=item.dataset.value,
            artefato_esperado=item.expected_artifact,
            justificativa=justificativa,
        )
        key = (
            request_item.dia.isoformat(),
            request_item.sessao,
            request_item.dataset,
            request_item.artefato_esperado,
            request_item.justificativa,
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(request_item)

    return sorted(
        rows,
        key=lambda row: (
            row.dia,
            row.sessao,
            row.dataset,
            row.artefato_esperado,
        ),
    )


def render_missing_artifacts_markdown(items: Iterable[RequestItem]) -> str:
    """Render request list as Markdown table.

    Args:
        items: Request items from `build_missing_artifacts_list`.

    Returns:
        Markdown string with deterministic ordering and fixed columns.
    """

    ordered = list(items)
    lines: list[str] = []
    lines.append("# Lista Do Que Pedir (Gaps De Show)")
    lines.append("")
    lines.append(f"- total_itens: {len(ordered)}")
    lines.append("")
    lines.append("| dia | sessao | dataset | artefato_esperado | justificativa |")
    lines.append("| --- | --- | --- | --- | --- |")
    if not ordered:
        lines.append("| - | - | - | - | Nenhum gap de show encontrado no recorte. |")
    else:
        for item in ordered:
            row = item.to_dict()
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["dia"],
                        row["sessao"].replace("|", "\\|"),
                        row["dataset"],
                        row["artefato_esperado"].replace("|", "\\|"),
                        row["justificativa"].replace("|", "\\|"),
                    ]
                )
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def render_missing_artifacts_csv(items: Iterable[RequestItem]) -> str:
    """Render request list as CSV text.

    Args:
        items: Request items from `build_missing_artifacts_list`.

    Returns:
        CSV string with fixed headers:
        `dia,sessao,dataset,artefato_esperado,justificativa`.
    """

    ordered = list(items)
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "dia",
            "sessao",
            "dataset",
            "artefato_esperado",
            "justificativa",
        ],
    )
    writer.writeheader()
    for item in ordered:
        writer.writerow(item.to_dict())
    return buffer.getvalue()

