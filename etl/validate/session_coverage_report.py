"""Generate session coverage report (expected sessions vs observed staging data).

This module builds an operational report that helps answer:
- which expected sessions already have dataset coverage,
- which datasets are still missing per session,
- and how many staging records remain unresolved (`session_id` missing).
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Iterable

from sqlmodel import Session

try:  # pragma: no cover - import style depends on caller cwd
    from app.db.database import engine
    from app.models.etl_registry import CoverageDataset
    from app.services.etl_coverage_queries import (
        build_session_coverage_matrix,
        build_session_coverage_summary,
        coverage_rows_to_dicts,
        coverage_summary_rows_to_dicts,
        unresolved_staging_records_by_dataset,
    )
    from .coverage_matrix import build_coverage_matrix_payload
except ModuleNotFoundError:  # pragma: no cover
    BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.db.database import engine
    from app.models.etl_registry import CoverageDataset
    from app.services.etl_coverage_queries import (
        build_session_coverage_matrix,
        build_session_coverage_summary,
        coverage_rows_to_dicts,
        coverage_summary_rows_to_dicts,
        unresolved_staging_records_by_dataset,
    )
    from .coverage_matrix import build_coverage_matrix_payload


def build_session_coverage_report_payload(
    session: Session,
    *,
    event_id: int | None = None,
    expected_datasets: Iterable[CoverageDataset] | None = None,
) -> dict[str, Any]:
    """Build session coverage report payload from database state.

    Args:
        session: Open database session.
        event_id: Optional event filter.
        expected_datasets: Optional dataset domain for coverage matrix.

    Returns:
        JSON-friendly payload with summary, session rows and matrix details.
    """

    if expected_datasets is None:
        # Preferred mode: session-type requirements loaded from datasets.yml.
        return build_coverage_matrix_payload(session, event_id=event_id)

    matrix_rows = build_session_coverage_matrix(
        session,
        event_id=event_id,
        expected_datasets=expected_datasets,
    )
    summary_rows = build_session_coverage_summary(matrix_rows)

    unresolved = unresolved_staging_records_by_dataset(
        session,
        event_id=event_id,
        expected_datasets=expected_datasets,
    )

    summary_payload = coverage_summary_rows_to_dicts(summary_rows)
    matrix_payload = coverage_rows_to_dicts(matrix_rows)

    total_sessions = len(summary_payload)
    ok_sessions = sum(1 for row in summary_payload if row["status"] == "ok")
    gap_sessions = total_sessions - ok_sessions

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "event_id": event_id,
        "status": "ok",
        "summary": {
            "total_sessions": total_sessions,
            "ok_sessions": ok_sessions,
            "partial_sessions": 0,
            "gap_sessions": gap_sessions,
        },
        "sessions": summary_payload,
        "matrix": matrix_payload,
        "unresolved_without_session": {
            dataset.value: int(count) for dataset, count in unresolved.items()
        },
    }


def render_session_coverage_report_markdown(payload: dict[str, Any]) -> str:
    """Render a Markdown report from a coverage payload.

    Args:
        payload: Payload produced by `build_session_coverage_report_payload`.

    Returns:
        Markdown text ready for operational review.
    """

    summary = payload.get("summary", {})
    sessions = payload.get("sessions", [])
    unresolved = payload.get("unresolved_without_session", {})

    lines: list[str] = []
    lines.append("# Session Coverage Report")
    lines.append("")
    lines.append(f"- generated_at: {payload.get('generated_at')}")
    lines.append(f"- event_id: {payload.get('event_id')}")
    lines.append(f"- total_sessions: {summary.get('total_sessions', 0)}")
    lines.append(f"- ok_sessions: {summary.get('ok_sessions', 0)}")
    if "partial_sessions" in summary:
        lines.append(f"- partial_sessions: {summary.get('partial_sessions', 0)}")
    lines.append(f"- gap_sessions: {summary.get('gap_sessions', 0)}")
    lines.append("")
    lines.append("## Sessions")
    lines.append("")
    lines.append(
        "| session_key | session_date | session_type | status | missing_datasets | observed_datasets |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in sessions:
        missing = ", ".join(row.get("missing_datasets", [])) or "-"
        observed = ", ".join(row.get("observed_datasets", [])) or "-"
        lines.append(
            f"| {row.get('session_key')} | {row.get('session_date')} | "
            f"{row.get('session_type')} | {row.get('status')} | {missing} | {observed} |"
        )

    lines.append("")
    lines.append("## Unresolved Staging Records")
    lines.append("")
    lines.append("| dataset | unresolved_without_session |")
    lines.append("| --- | --- |")
    for dataset, count in sorted(unresolved.items()):
        lines.append(f"| {dataset} | {count} |")

    return "\n".join(lines) + "\n"


def write_session_coverage_report(
    *,
    out_md: Path | str | None = None,
    out_json: Path | str | None = None,
    event_id: int | None = None,
    expected_datasets: Iterable[CoverageDataset] | None = None,
) -> dict[str, Any]:
    """Generate and optionally write session coverage report outputs.

    Args:
        out_md: Optional destination path for Markdown report.
        out_json: Optional destination path for JSON report.
        event_id: Optional event filter.
        expected_datasets: Optional dataset domain for the report.

    Returns:
        Report payload that was written/rendered.

    Raises:
        ValueError: When both output paths are missing.
    """

    if out_md is None and out_json is None:
        raise ValueError("Informe ao menos um destino: out_md ou out_json.")

    with Session(engine) as session:
        payload = build_session_coverage_report_payload(
            session,
            event_id=event_id,
            expected_datasets=expected_datasets,
        )

    if out_json is not None:
        path_json = Path(out_json)
        path_json.parent.mkdir(parents=True, exist_ok=True)
        path_json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    if out_md is not None:
        path_md = Path(out_md)
        path_md.parent.mkdir(parents=True, exist_ok=True)
        path_md.write_text(render_session_coverage_report_markdown(payload), encoding="utf-8")

    return payload
