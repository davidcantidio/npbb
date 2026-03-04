#!/usr/bin/env python3
"""Compare row counts between a source and a target database."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from sqlalchemy import MetaData, Table, create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_TABLES = ("lead", "evento", "usuario")
TABLE_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class TableComparison:
    table: str
    source_count: int | None
    target_count: int | None
    status: str
    details: str | None = None


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare row counts between source and target databases.",
    )
    parser.add_argument("--source-url", required=True, help="SQLAlchemy URL for the source database.")
    parser.add_argument("--target-url", required=True, help="SQLAlchemy URL for the target database.")
    parser.add_argument(
        "--tables",
        nargs="+",
        default=list(DEFAULT_TABLES),
        help="Table names to compare. Defaults to lead evento usuario.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Markdown output path for the comparison report.",
    )
    return parser.parse_args(argv)


def validate_tables(tables: Sequence[str]) -> list[str]:
    validated: list[str] = []
    for table_name in tables:
        if not TABLE_NAME_RE.match(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        validated.append(table_name)
    return validated


def redact_url(raw_url: str) -> str:
    return make_url(raw_url).render_as_string(hide_password=True)


def get_table_count(engine: Engine, table_name: str) -> int:
    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)
    with engine.connect() as connection:
        stmt = select(func.count()).select_from(table)
        return int(connection.execute(stmt).scalar_one())


def compare_table(source_engine: Engine, target_engine: Engine, table_name: str) -> TableComparison:
    try:
        source_count = get_table_count(source_engine, table_name)
        target_count = get_table_count(target_engine, table_name)
    except SQLAlchemyError as exc:
        return TableComparison(
            table=table_name,
            source_count=None,
            target_count=None,
            status="error",
            details=str(exc),
        )

    status = "match" if source_count == target_count else "mismatch"
    return TableComparison(
        table=table_name,
        source_count=source_count,
        target_count=target_count,
        status=status,
    )


def build_markdown(
    *,
    source_url: str,
    target_url: str,
    comparisons: Sequence[TableComparison],
) -> str:
    timestamp = datetime.now(timezone.utc).isoformat()
    total_matches = sum(1 for item in comparisons if item.status == "match")
    total_mismatches = sum(1 for item in comparisons if item.status == "mismatch")
    total_errors = sum(1 for item in comparisons if item.status == "error")

    lines = [
        "# Restore Table Counts",
        "",
        f"- Generated at: `{timestamp}`",
        f"- Source: `{redact_url(source_url)}`",
        f"- Target: `{redact_url(target_url)}`",
        f"- Matches: `{total_matches}`",
        f"- Mismatches: `{total_mismatches}`",
        f"- Errors: `{total_errors}`",
        "",
        "| Table | Source Count | Target Count | Status | Details |",
        "|---|---:|---:|---|---|",
    ]

    for item in comparisons:
        source_value = "n/a" if item.source_count is None else str(item.source_count)
        target_value = "n/a" if item.target_count is None else str(item.target_count)
        details = item.details or ""
        lines.append(
            f"| `{item.table}` | `{source_value}` | `{target_value}` | `{item.status}` | {details} |"
        )

    lines.extend(
        [
            "",
            "## Gate Recommendation",
            "",
        ]
    )

    if total_mismatches == 0 and total_errors == 0:
        lines.append("- Decision: `promote-candidate`")
        lines.append("- Reason: all compared table counts matched.")
    else:
        lines.append("- Decision: `hold`")
        lines.append("- Reason: at least one table mismatched or could not be compared.")

    return "\n".join(lines) + "\n"


def run_comparison(
    *,
    source_url: str,
    target_url: str,
    tables: Sequence[str],
) -> list[TableComparison]:
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    return [compare_table(source_engine, target_engine, table_name) for table_name in tables]


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        tables = validate_tables(args.tables)
    except ValueError as exc:
        print(exc)
        return 2

    comparisons = run_comparison(
        source_url=args.source_url,
        target_url=args.target_url,
        tables=tables,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_markdown(
            source_url=args.source_url,
            target_url=args.target_url,
            comparisons=comparisons,
        ),
        encoding="utf-8",
    )

    has_failure = any(item.status != "match" for item in comparisons)
    return 1 if has_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
