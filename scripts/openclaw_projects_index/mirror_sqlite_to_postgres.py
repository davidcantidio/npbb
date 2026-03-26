#!/usr/bin/env python3
"""
Espelha o índice SQLite (v4) para o Postgres read model após aplicar schema_postgres.sql.

Requisitos:
  pip install -r scripts/openclaw_projects_index/requirements-postgres.txt

Variáveis de ambiente:
  OPENCLAW_PROJECTS_DB           — caminho do .sqlite (default: mesmo que sync.py)
  OPENCLAW_PROJECTS_DATABASE_URL — URL Postgres

Uso:
  python3 scripts/openclaw_projects_index/mirror_sqlite_to_postgres.py [--dry-run]

Notas:
  - Limpa e repovoa tabelas estruturadas + documents; não copia BLOB de embeddings
    (regerar embeddings no Postgres com o pipeline de vetores).
  - Preserva IDs numéricos do SQLite para manter FKs estáveis numa janela de cutover.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import psycopg
except ModuleNotFoundError:  # pragma: no cover
    print(
        "psycopg não instalado. Execute: pip install -r scripts/openclaw_projects_index/requirements-postgres.txt",
        file=sys.stderr,
    )
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _default_sqlite_path() -> Path:
    env = os.environ.get("OPENCLAW_PROJECTS_DB")
    if env:
        return Path(env)
    return REPO_ROOT / "openclaw-workspace" / ".openclaw" / "openclaw-projects.sqlite"


def _pg_url() -> str:
    url = os.environ.get("OPENCLAW_PROJECTS_DATABASE_URL")
    if not url:
        raise SystemExit("OPENCLAW_PROJECTS_DATABASE_URL não definido.")
    return url


def _rows(conn: sqlite3.Connection, sql: str) -> list[sqlite3.Row]:
    cur = conn.execute(sql)
    return cur.fetchall()


def _bool_from_sqlite(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    return int(v) != 0


def _truncate_pg(cur: Any) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
          sync_runs,
          execution_commits,
          embeddings,
          document_chunks,
          documents,
          feature_audits,
          tasks,
          user_stories,
          features,
          project_documents,
          projects
        RESTART IDENTITY CASCADE
        """
    )


def _copy_projects(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(slc, "SELECT id, slug, name_display, created_at, updated_at FROM projects"):
        cur.execute(
            """
            INSERT INTO projects (id, slug, name_display, created_at, updated_at)
            VALUES (%s, %s, %s, %s::timestamptz, %s::timestamptz)
            """,
            (r["id"], r["slug"], r["name_display"], r["created_at"], r["updated_at"]),
        )


def _copy_features(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, project_id, feature_key, feature_number, name_display, status, audit_gate,
               path_relative, created_at, updated_at
        FROM features
        """,
    ):
        cur.execute(
            """
            INSERT INTO features (id, project_id, feature_key, feature_number, name_display, status,
              audit_gate, path_relative, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["project_id"],
                r["feature_key"],
                r["feature_number"],
                r["name_display"],
                r["status"],
                r["audit_gate"],
                r["path_relative"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _copy_user_stories(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, project_id, feature_id, user_story_key, layout, status, task_instruction_mode,
               decision_refs_json, path_relative, created_at, updated_at
        FROM user_stories
        """,
    ):
        dj = r["decision_refs_json"]
        if dj is not None and not isinstance(dj, (dict, list)):
            try:
                dj = json.loads(dj)
            except json.JSONDecodeError:
                dj = None
        cur.execute(
            """
            INSERT INTO user_stories (id, project_id, feature_id, user_story_key, layout, status,
              task_instruction_mode, decision_refs_json, path_relative, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["project_id"],
                r["feature_id"],
                r["user_story_key"],
                r["layout"],
                r["status"],
                r["task_instruction_mode"],
                json.dumps(dj) if dj is not None else None,
                r["path_relative"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _copy_tasks(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, user_story_id, task_number, task_id, status, tdd_aplicavel, path_relative,
               created_at, updated_at
        FROM tasks
        """,
    ):
        cur.execute(
            """
            INSERT INTO tasks (id, user_story_id, task_number, task_id, status, tdd_aplicavel,
              path_relative, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["user_story_id"],
                r["task_number"],
                r["task_id"],
                r["status"],
                _bool_from_sqlite(r["tdd_aplicavel"]),
                r["path_relative"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _copy_feature_audits(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, feature_id, report_key, status, verdict, scope_type, scope_ref, feature_code,
               base_commit, compares_to, round_number, supersedes, followup_destination,
               decision_refs_json, path_relative, created_at, updated_at
        FROM feature_audits
        """,
    ):
        dj = r["decision_refs_json"]
        if dj is not None and not isinstance(dj, (dict, list)):
            try:
                dj = json.loads(dj)
            except json.JSONDecodeError:
                dj = None
        cur.execute(
            """
            INSERT INTO feature_audits (id, feature_id, report_key, status, verdict, scope_type,
              scope_ref, feature_code, base_commit, compares_to, round_number, supersedes,
              followup_destination, decision_refs_json, path_relative, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["feature_id"],
                r["report_key"],
                r["status"],
                r["verdict"],
                r["scope_type"],
                r["scope_ref"],
                r["feature_code"],
                r["base_commit"],
                r["compares_to"],
                r["round_number"],
                r["supersedes"],
                r["followup_destination"],
                json.dumps(dj) if dj is not None else None,
                r["path_relative"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _copy_project_documents(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, project_id, doc_type, status, intake_kind, source_mode, intake_slug,
               path_relative, created_at, updated_at
        FROM project_documents
        """,
    ):
        cur.execute(
            """
            INSERT INTO project_documents (id, project_id, doc_type, status, intake_kind, source_mode,
              intake_slug, path_relative, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["project_id"],
                r["doc_type"],
                r["status"],
                r["intake_kind"],
                r["source_mode"],
                r["intake_slug"],
                r["path_relative"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _copy_documents(slc: sqlite3.Connection, cur: Any) -> None:
    for r in _rows(
        slc,
        """
        SELECT id, path_relative, kind, project_id, feature_id, user_story_id, task_id,
               feature_audit_id, title, body_markdown, front_matter_json,
               content_hash, file_mtime, indexed_at, created_at, updated_at
        FROM documents
        """,
    ):
        fm = r["front_matter_json"]
        if fm is not None and isinstance(fm, str):
            try:
                fm_parsed = json.loads(fm)
                fm = json.dumps(fm_parsed)
            except json.JSONDecodeError:
                fm = None
        elif fm is not None and isinstance(fm, (dict, list)):
            fm = json.dumps(fm)
        cur.execute(
            """
            INSERT INTO documents (id, path_relative, kind, project_id, feature_id, user_story_id,
              task_id, feature_audit_id, title, body_markdown, front_matter_json, content_hash,
              file_mtime, indexed_at, created_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s::timestamptz,%s::timestamptz,%s::timestamptz)
            """,
            (
                r["id"],
                r["path_relative"],
                r["kind"],
                r["project_id"],
                r["feature_id"],
                r["user_story_id"],
                r["task_id"],
                r["feature_audit_id"],
                r["title"],
                r["body_markdown"],
                fm,
                r["content_hash"],
                r["file_mtime"],
                r["indexed_at"],
                r["created_at"],
                r["updated_at"],
            ),
        )


def _sync_sequences(cur: Any, tables: Iterable[str]) -> None:
    for table in tables:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT COALESCE(MAX(id), 1) FROM {table}))")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror OpenClaw SQLite index into Postgres.")
    parser.add_argument("--dry-run", action="store_true", help="Apenas validar ficheiros e env.")
    parser.add_argument("--sqlite-db", type=Path, default=None, help="Override OPENCLAW_PROJECTS_DB.")
    args = parser.parse_args()

    sqlite_path = args.sqlite_db or _default_sqlite_path()
    if not sqlite_path.is_file():
        print(f"SQLite em falta: {sqlite_path}", file=sys.stderr)
        return 1

    _pg_url()  # validate env early

    if args.dry_run:
        print(f"dry-run: sqlite={sqlite_path} ok")
        return 0

    slc = sqlite3.connect(str(sqlite_path))
    slc.row_factory = sqlite3.Row

    with psycopg.connect(_pg_url(), autocommit=False) as pg:
        with pg.cursor() as cur:
            _truncate_pg(cur)
            _copy_projects(slc, cur)
            _copy_features(slc, cur)
            _copy_user_stories(slc, cur)
            _copy_tasks(slc, cur)
            _copy_feature_audits(slc, cur)
            _copy_project_documents(slc, cur)
            _copy_documents(slc, cur)
            cur.execute(
                """
                INSERT INTO sync_runs (status, repo_root, git_head, schema_version, trigger_source, finished_at)
                VALUES ('success', %s, NULL, 'pg-1', 'mirror_sqlite_to_postgres', now())
                """,
                (str(REPO_ROOT),),
            )
            _sync_sequences(
                cur,
                (
                    "projects",
                    "features",
                    "user_stories",
                    "tasks",
                    "feature_audits",
                    "project_documents",
                    "documents",
                    "sync_runs",
                ),
            )

    slc.close()
    print("Mirror concluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
