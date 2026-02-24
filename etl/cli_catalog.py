"""CLI for ETL ingestion operational catalog reports.

Examples (PowerShell):
  python -m etl.cli_catalog catalog:report --out-md out/catalog.md --out-json out/catalog.json
  python -m etl.cli_catalog catalog:report --status failed --kind pdf --out-md out/failures.md
  python -m etl.cli_catalog catalog:report --status partial --kind xlsx --out-json out/partial.xlsx.json
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from sqlmodel import Session

try:
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus, SourceKind
    from app.services.etl_catalog_queries import (
        CatalogSummary,
        LatestIngestionBySourceRow,
        latest_ingestion_by_source,
        summarize_latest_ingestion_rows,
    )
except ModuleNotFoundError:
    BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.db.database import engine
    from app.models.etl_registry import IngestionStatus, SourceKind
    from app.services.etl_catalog_queries import (
        CatalogSummary,
        LatestIngestionBySourceRow,
        latest_ingestion_by_source,
        summarize_latest_ingestion_rows,
    )


def _iso_or_none(value: datetime | None) -> str | None:
    """Render datetime to ISO-8601 when present."""
    if value is None:
        return None
    return value.isoformat()


def _md_cell(value: Any) -> str:
    """Render one value as a safe Markdown table cell."""
    if value is None:
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ").strip() or "-"


def _row_to_json(row: LatestIngestionBySourceRow) -> dict[str, Any]:
    """Convert one query row to JSON-serializable mapping."""
    return {
        "source_id": row.source_id,
        "source_kind": row.source_kind.value,
        "source_uri": row.source_uri,
        "source_display_name": row.source_display_name,
        "source_is_active": row.source_is_active,
        "latest_ingestion_id": row.latest_ingestion_id,
        "latest_status": row.latest_status.value if row.latest_status else None,
        "latest_started_at": _iso_or_none(row.latest_started_at),
        "latest_finished_at": _iso_or_none(row.latest_finished_at),
        "latest_extractor_name": row.latest_extractor_name,
        "latest_notes": row.latest_notes,
        "latest_created_at": _iso_or_none(row.latest_created_at),
    }


def render_catalog_markdown(
    rows: list[LatestIngestionBySourceRow],
    summary: CatalogSummary,
    *,
    status_filters: list[IngestionStatus],
    kind_filters: list[SourceKind],
) -> str:
    """Render operational catalog report in Markdown format.

    Args:
        rows: Query rows already filtered.
        summary: Aggregate counters for report header.
        status_filters: Status filters applied in the query.
        kind_filters: Source-kind filters applied in the query.

    Returns:
        Markdown report string ready to persist.
    """

    generated_at = datetime.now(timezone.utc).isoformat()
    status_filter_text = ", ".join(st.value for st in status_filters) if status_filters else "all"
    kind_filter_text = ", ".join(k.value for k in kind_filters) if kind_filters else "all"
    status_counts = (
        ", ".join(f"{k}={v}" for k, v in sorted(summary.latest_status_counts.items()))
        if summary.latest_status_counts
        else "none"
    )

    lines = [
        "# TMJ 2025 - Operational Ingestion Catalog",
        "",
        f"- generated_at_utc: {generated_at}",
        f"- filters.status: {status_filter_text}",
        f"- filters.source_kind: {kind_filter_text}",
        f"- total_sources: {summary.total_sources}",
        f"- sources_with_ingestion: {summary.sources_with_ingestion}",
        f"- sources_without_ingestion: {summary.sources_without_ingestion}",
        f"- latest_status_counts: {status_counts}",
        "",
        "| source_id | kind | active | latest_status | started_at | finished_at | extractor | notes | uri |",
        "|---|---|---:|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(row.source_id),
                    _md_cell(row.source_kind.value),
                    _md_cell("yes" if row.source_is_active else "no"),
                    _md_cell(row.latest_status.value if row.latest_status else None),
                    _md_cell(_iso_or_none(row.latest_started_at)),
                    _md_cell(_iso_or_none(row.latest_finished_at)),
                    _md_cell(row.latest_extractor_name),
                    _md_cell(row.latest_notes),
                    _md_cell(row.source_uri),
                ]
            )
            + " |"
        )
    return "\n".join(lines).strip() + "\n"


def render_catalog_json(
    rows: list[LatestIngestionBySourceRow],
    summary: CatalogSummary,
    *,
    status_filters: list[IngestionStatus],
    kind_filters: list[SourceKind],
) -> str:
    """Render operational catalog report in JSON format.

    Args:
        rows: Query rows already filtered.
        summary: Aggregate counters for report header.
        status_filters: Status filters applied in the query.
        kind_filters: Source-kind filters applied in the query.

    Returns:
        JSON report string with filters, summary and source rows.
    """

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "filters": {
            "status": [st.value for st in status_filters],
            "source_kind": [kind.value for kind in kind_filters],
        },
        "summary": {
            "total_sources": summary.total_sources,
            "sources_with_ingestion": summary.sources_with_ingestion,
            "sources_without_ingestion": summary.sources_without_ingestion,
            "latest_status_counts": dict(sorted(summary.latest_status_counts.items())),
        },
        "sources": [_row_to_json(row) for row in rows],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def run_catalog_report(
    *,
    out_md: Path | None,
    out_json: Path | None,
    statuses: list[IngestionStatus] | None = None,
    source_kinds: list[SourceKind] | None = None,
) -> int:
    """Execute catalog report generation and persist output artifacts.

    Args:
        out_md: Optional markdown destination path.
        out_json: Optional JSON destination path.
        statuses: Optional latest-run status filters.
        source_kinds: Optional source kind filters.

    Returns:
        Exit code where 0 means success.

    Raises:
        ValueError: If neither output path is provided.
        OSError: If writing one output file fails.
    """

    if out_md is None and out_json is None:
        raise ValueError("Informe ao menos um destino: --out-md e/ou --out-json.")

    statuses = statuses or []
    source_kinds = source_kinds or []
    with Session(engine) as session:
        rows = latest_ingestion_by_source(
            session,
            statuses=statuses or None,
            source_kinds=source_kinds or None,
        )
    summary = summarize_latest_ingestion_rows(rows)

    if out_md is not None:
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(
            render_catalog_markdown(
                rows,
                summary,
                status_filters=statuses,
                kind_filters=source_kinds,
            ),
            encoding="utf-8",
        )
    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(
            render_catalog_json(
                rows,
                summary,
                status_filters=statuses,
                kind_filters=source_kinds,
            ),
            encoding="utf-8",
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for ETL operational catalog."""

    parser = argparse.ArgumentParser(prog="npbb-catalog")
    sub = parser.add_subparsers(dest="command", required=True)
    report = sub.add_parser(
        "catalog:report",
        help="Generate ingestion operational catalog report (markdown/json).",
    )
    report.add_argument("--out-md", default=None, help="Optional output markdown path.")
    report.add_argument("--out-json", default=None, help="Optional output JSON path.")
    report.add_argument(
        "--status",
        action="append",
        choices=[status.value for status in IngestionStatus],
        default=None,
        help="Filter by latest ingestion status. Repeatable.",
    )
    report.add_argument(
        "--kind",
        action="append",
        choices=[kind.value for kind in SourceKind],
        default=None,
        help="Filter by source kind. Repeatable.",
    )

    args = parser.parse_args(argv)
    if args.command == "catalog:report":
        status_filters = [IngestionStatus(value) for value in (args.status or [])]
        kind_filters = [SourceKind(value) for value in (args.kind or [])]
        return run_catalog_report(
            out_md=Path(args.out_md) if args.out_md else None,
            out_json=Path(args.out_json) if args.out_json else None,
            statuses=status_filters,
            source_kinds=kind_filters,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
