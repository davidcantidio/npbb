"""Aplica `schema_postgres.sql` via sqlparse (vários statements; evita falhas com `;` em comentários)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def apply_postgres_schema_file(conn: Any, schema_path: Path) -> None:
    try:
        import sqlparse
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Postgres DDL requer sqlparse (pip install -r scripts/openclaw_projects_index/requirements.txt)."
        ) from exc

    raw = schema_path.read_text(encoding="utf-8")
    statements = [s.strip() for s in sqlparse.split(raw) if s.strip()]
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
