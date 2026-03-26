#!/usr/bin/env python3
"""
Sincroniza PROJETOS/**/*.md para índice derivado (SQLite ou Postgres; SoT = Git + Markdown).

Uso:
  python3 scripts/openclaw_projects_index/sync.py [--repo-root PATH] [--db PATH]
    [--backend sqlite|postgres] [--dry-run]

Variáveis de ambiente:
  OPENCLAW_REPO_ROOT — raiz do clone (contém PROJETOS/)
  OPENCLAW_PROJECTS_DB — SQLite (default se backend sqlite)
  OPENCLAW_PROJECTS_DATABASE_URL — Postgres (obrigatório se backend postgres)
  OPENCLAW_PGSSLMODE — opcional; anexado à URL se não existir sslmode=
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Permite `import domain` quando o módulo é carregado via importlib (pytest) ou como script.
_sync_dir = Path(__file__).resolve().parent
if str(_sync_dir) not in sys.path:
    sys.path.insert(0, str(_sync_dir))

from domain import (
    POSTGRES_SCHEMA_BUNDLE,
    PROJETOS,
    SQLITE_SCHEMA_VERSION,
    EXPECTED_SQLITE_USER_VERSION,
    bool_int,
    classify_md,
    default_db_path,
    discover_project_slugs,
    feature_number_from_key,
    feature_root_relative,
    file_content_hash,
    first_markdown_title,
    git_head_sha,
    governance_kind_from_filename,
    int_value,
    json_text,
    parse_front_matter,
    posix_relative,
    resolve_postgres_url,
    resolve_repo_root,
    scalar_text,
    user_story_readme_relative,
)

# Re-export para testes e ferramentas que importam o módulo sync
SCHEMA_VERSION = SQLITE_SCHEMA_VERSION
EXPECTED_USER_VERSION = EXPECTED_SQLITE_USER_VERSION


def _here() -> Path:
    return Path(__file__).resolve().parent


def load_schema_sqlite() -> str:
    return (_here() / "schema.sql").read_text(encoding="utf-8")


def load_schema_postgres() -> str:
    return (_here() / "schema_postgres.sql").read_text(encoding="utf-8")


def apply_postgres_schema(conn: Any) -> None:
    from postgres_schema_util import apply_postgres_schema_file

    apply_postgres_schema_file(conn, _here() / "schema_postgres.sql")


def drop_schema_sqlite(cur: sqlite3.Cursor) -> None:
    cur.execute("PRAGMA foreign_keys = OFF")
    for name in (
        "embeddings",
        "document_chunks",
        "documents_fts",
        "documents",
        "project_documents",
        "governance_documents",
        "feature_audits",
        "tasks",
        "user_stories",
        "features",
        "projects",
        "sync_meta",
        "audit_reports",
        "sprints",
        "issues",
        "epics",
        "phases",
    ):
        cur.execute(f"DROP TABLE IF EXISTS {name}")
    cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
    )
    if cur.fetchone():
        cur.execute("DELETE FROM sqlite_sequence")
    cur.execute("PRAGMA foreign_keys = ON")


def ensure_schema_sqlite(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("PRAGMA user_version")
    version = cur.fetchone()[0]
    if version != EXPECTED_SQLITE_USER_VERSION:
        drop_schema_sqlite(cur)
    cur.executescript(load_schema_sqlite())


def clear_derived_sqlite(cur: sqlite3.Cursor) -> None:
    cur.execute("PRAGMA foreign_keys = OFF")
    for table in (
        "embeddings",
        "document_chunks",
        "documents",
        "project_documents",
        "governance_documents",
        "feature_audits",
        "tasks",
        "user_stories",
        "features",
        "projects",
    ):
        cur.execute(f"DELETE FROM {table}")
    cur.execute("DELETE FROM sync_meta")
    cur.execute("PRAGMA foreign_keys = ON")


def rebuild_fts_sqlite(cur: sqlite3.Cursor) -> None:
    cur.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")


def _sql_ph(backend: str, sql: str) -> str:
    if backend == "postgres":
        return sql.replace("?", "%s")
    return sql


def _adapt_front_matter(backend: str, front_matter: dict[str, Any]) -> Any:
    if backend == "postgres":
        from psycopg.types.json import Json

        return Json(front_matter)
    return json_text(front_matter)


def _adapt_decision_refs(backend: str, value: Any) -> Any:
    if value is None:
        return None
    if backend == "postgres":
        from psycopg.types.json import Json

        return Json(value)
    return json_text(value)


def _adapt_ts(backend: str, now_pg: datetime, indexed_at_str: str) -> Any:
    return indexed_at_str if backend == "sqlite" else now_pg


def _exec_insert_id(cur: Any, backend: str, sql_q: str, params: tuple) -> int:
    sql = _sql_ph(backend, sql_q)
    if backend == "postgres":
        sql += " RETURNING id"
        cur.execute(sql, params)
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("INSERT RETURNING id sem linha")
        return int(row[0])
    cur.execute(sql, params)
    return int(cur.lastrowid)


def insert_document(
    cur: Any,
    backend: str,
    *,
    path_relative: str,
    kind: str,
    title: Optional[str],
    body_markdown: str,
    front_matter: dict[str, Any],
    content_hash: str,
    file_mtime: int,
    indexed_at_str: str,
    now_pg: datetime,
    project_id: Optional[int] = None,
    feature_id: Optional[int] = None,
    user_story_id: Optional[int] = None,
    task_id: Optional[int] = None,
    feature_audit_id: Optional[int] = None,
    governance_doc_id: Optional[int] = None,
) -> None:
    relation_values = {
        "project_id": project_id,
        "feature_id": feature_id,
        "user_story_id": user_story_id,
        "task_id": task_id,
        "feature_audit_id": feature_audit_id,
        "governance_doc_id": governance_doc_id,
    }
    columns = ["path_relative", "kind"]
    values: list[Any] = [path_relative, kind]
    for column, value in relation_values.items():
        if value is not None:
            columns.append(column)
            values.append(value)
    ts = _adapt_ts(backend, now_pg, indexed_at_str)
    fm = _adapt_front_matter(backend, front_matter)
    columns.extend(
        [
            "title",
            "body_markdown",
            "front_matter_json",
            "content_hash",
            "file_mtime",
            "indexed_at",
            "updated_at",
        ]
    )
    values.extend(
        [
            title,
            body_markdown,
            fm,
            content_hash,
            file_mtime,
            ts,
            ts,
        ]
    )
    placeholders = ", ".join("?" for _ in values)
    sql_q = f"INSERT INTO documents ({', '.join(columns)}) VALUES ({placeholders})"
    cur.execute(_sql_ph(backend, sql_q), tuple(values))


def clear_derived_postgres(cur: Any) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
          embeddings,
          document_chunks,
          documents,
          governance_documents,
          feature_audits,
          tasks,
          user_stories,
          features,
          project_documents,
          projects
        RESTART IDENTITY CASCADE
        """
    )


def run_index_pass(
    cur: Any,
    backend: str,
    repo_root: Path,
    indexed_at_str: str,
    now_pg: datetime,
) -> int:
    projetos = repo_root / PROJETOS
    all_md = [path for path in projetos.rglob("*.md") if path.is_file()]

    project_ids: dict[str, int] = {}
    feature_ids: dict[tuple[int, str], int] = {}
    user_story_ids: dict[tuple[int, str], int] = {}
    task_ids: dict[str, int] = {}
    feature_audit_ids: dict[str, int] = {}

    ts = _adapt_ts(backend, now_pg, indexed_at_str)

    for slug in discover_project_slugs(projetos):
        pid = _exec_insert_id(
            cur,
            backend,
            "INSERT INTO projects (slug, name_display, updated_at) VALUES (?, ?, ?)",
            (slug, slug, ts),
        )
        project_ids[slug] = pid

    for path in sorted(all_md, key=lambda item: posix_relative(item, repo_root)):
        rel = posix_relative(path, repo_root)
        raw = path.read_text(encoding="utf-8", errors="replace")
        front_matter, body = parse_front_matter(raw, source_name=rel)
        content_hash = file_content_hash(raw)
        file_mtime = int(path.stat().st_mtime)
        title = scalar_text(front_matter.get("doc_id")) or first_markdown_title(body) or path.stem
        classified = classify_md(rel)

        if classified.kind == "governance":
            governance_kind = governance_kind_from_filename(path.name)
            gid = _exec_insert_id(
                cur,
                backend,
                """
                INSERT INTO governance_documents (kind, doc_id, filename, path_relative, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    governance_kind,
                    scalar_text(front_matter.get("doc_id")) or path.stem,
                    path.name,
                    rel,
                    scalar_text(front_matter.get("version")),
                    ts,
                ),
            )
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind="governance",
                governance_doc_id=gid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        pid = project_ids.get(classified.project_slug) if classified.project_slug else None

        if classified.kind == "project_intake" and pid is not None:
            _exec_insert_id(
                cur,
                backend,
                """
                INSERT INTO project_documents (
                  project_id, doc_type, status, intake_kind, source_mode, intake_slug, path_relative, updated_at
                ) VALUES (?, 'intake', ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    scalar_text(front_matter.get("status")),
                    scalar_text(front_matter.get("intake_kind")),
                    scalar_text(front_matter.get("source_mode")),
                    classified.intake_slug,
                    rel,
                    ts,
                ),
            )
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind="intake",
                project_id=pid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        if classified.kind == "project_prd" and pid is not None:
            _exec_insert_id(
                cur,
                backend,
                """
                INSERT INTO project_documents (
                  project_id, doc_type, status, intake_kind, source_mode, intake_slug, path_relative, updated_at
                ) VALUES (?, 'prd', ?, ?, ?, NULL, ?, ?)
                """,
                (
                    pid,
                    scalar_text(front_matter.get("status")),
                    scalar_text(front_matter.get("intake_kind")),
                    scalar_text(front_matter.get("source_mode")),
                    rel,
                    ts,
                ),
            )
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind="prd",
                project_id=pid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        if classified.kind == "project_audit_log" and pid is not None:
            _exec_insert_id(
                cur,
                backend,
                """
                INSERT INTO project_documents (
                  project_id, doc_type, status, intake_kind, source_mode, intake_slug, path_relative, updated_at
                ) VALUES (?, 'audit_log', ?, NULL, NULL, NULL, ?, ?)
                """,
                (pid, scalar_text(front_matter.get("status")), rel, ts),
            )
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind="audit_log",
                project_id=pid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        if classified.kind == "project_closing_report" and pid is not None:
            _exec_insert_id(
                cur,
                backend,
                """
                INSERT INTO project_documents (
                  project_id, doc_type, status, intake_kind, source_mode, intake_slug, path_relative, updated_at
                ) VALUES (?, 'closing_report', ?, NULL, NULL, NULL, ?, ?)
                """,
                (pid, scalar_text(front_matter.get("status")), rel, ts),
            )
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind="closing_report",
                project_id=pid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        if classified.kind in (
            "project_session",
            "project_other",
            "project_root_md",
            "project_nested_other",
        ):
            insert_document(
                cur,
                backend,
                path_relative=rel,
                kind=classified.kind,
                project_id=pid,
                title=title,
                body_markdown=body,
                front_matter=front_matter,
                content_hash=content_hash,
                file_mtime=file_mtime,
                indexed_at_str=indexed_at_str,
                now_pg=now_pg,
            )
            continue

        if classified.feature_key and pid is not None:
            feature_pk = (pid, classified.feature_key)
            if feature_pk not in feature_ids:
                fid = _exec_insert_id(
                    cur,
                    backend,
                    """
                    INSERT INTO features (
                      project_id, feature_key, feature_number, name_display, status, audit_gate, path_relative, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pid,
                        classified.feature_key,
                        feature_number_from_key(classified.feature_key),
                        classified.feature_key,
                        None,
                        None,
                        feature_root_relative(classified.project_slug or "", classified.feature_key),
                        ts,
                    ),
                )
                feature_ids[feature_pk] = fid

            feature_id = feature_ids[feature_pk]

            if classified.kind == "feature_manifest":
                cur.execute(
                    _sql_ph(
                        backend,
                        """
                        UPDATE features
                        SET name_display = COALESCE(?, name_display),
                            status = COALESCE(?, status),
                            audit_gate = COALESCE(?, audit_gate),
                            updated_at = ?
                        WHERE id = ?
                        """,
                    ),
                    (
                        title,
                        scalar_text(front_matter.get("status")),
                        scalar_text(front_matter.get("audit_gate")),
                        ts,
                        feature_id,
                    ),
                )
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="feature_manifest",
                    project_id=pid,
                    feature_id=feature_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

            if classified.kind == "user_story_readme" and classified.user_story_key:
                us_pk = (pid, classified.user_story_key)
                dr = _adapt_decision_refs(backend, front_matter.get("decision_refs"))
                if us_pk not in user_story_ids:
                    uid = _exec_insert_id(
                        cur,
                        backend,
                        """
                        INSERT INTO user_stories (
                          project_id, feature_id, user_story_key, layout, status, task_instruction_mode,
                          decision_refs_json, path_relative, updated_at
                        ) VALUES (?, ?, ?, 'folder', ?, ?, ?, ?, ?)
                        """,
                        (
                            pid,
                            feature_id,
                            classified.user_story_key,
                            scalar_text(front_matter.get("status")),
                            scalar_text(front_matter.get("task_instruction_mode")),
                            dr,
                            rel,
                            ts,
                        ),
                    )
                    user_story_ids[us_pk] = uid
                else:
                    cur.execute(
                        _sql_ph(
                            backend,
                            """
                            UPDATE user_stories
                            SET feature_id = ?,
                                status = COALESCE(?, status),
                                task_instruction_mode = COALESCE(?, task_instruction_mode),
                                decision_refs_json = COALESCE(?, decision_refs_json),
                                updated_at = ?
                            WHERE id = ?
                            """,
                        ),
                        (
                            feature_id,
                            scalar_text(front_matter.get("status")),
                            scalar_text(front_matter.get("task_instruction_mode")),
                            dr,
                            ts,
                            user_story_ids[us_pk],
                        ),
                    )
                user_story_id = user_story_ids[us_pk]
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="user_story",
                    project_id=pid,
                    feature_id=feature_id,
                    user_story_id=user_story_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

            if classified.kind == "task_file" and classified.user_story_key and classified.task_number is not None:
                us_pk = (pid, classified.user_story_key)
                if us_pk not in user_story_ids:
                    uid = _exec_insert_id(
                        cur,
                        backend,
                        """
                        INSERT INTO user_stories (
                          project_id, feature_id, user_story_key, layout, status, task_instruction_mode,
                          decision_refs_json, path_relative, updated_at
                        ) VALUES (?, ?, ?, 'folder', NULL, NULL, NULL, ?, ?)
                        """,
                        (
                            pid,
                            feature_id,
                            classified.user_story_key,
                            user_story_readme_relative(
                                classified.project_slug or "",
                                classified.feature_key,
                                classified.user_story_key,
                            ),
                            ts,
                        ),
                    )
                    user_story_ids[us_pk] = uid
                user_story_id = user_story_ids[us_pk]

                tdd_sqlite = bool_int(front_matter.get("tdd_aplicavel"), default=0)
                tdd_val: Any = bool(tdd_sqlite) if backend == "postgres" else tdd_sqlite

                if rel not in task_ids:
                    tid = _exec_insert_id(
                        cur,
                        backend,
                        """
                        INSERT INTO tasks (
                          user_story_id, task_number, task_id, status, tdd_aplicavel, path_relative, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            user_story_id,
                            classified.task_number,
                            scalar_text(front_matter.get("task_id")) or f"T{classified.task_number}",
                            scalar_text(front_matter.get("status")),
                            tdd_val,
                            rel,
                            ts,
                        ),
                    )
                    task_ids[rel] = tid
                else:
                    cur.execute(
                        _sql_ph(
                            backend,
                            """
                            UPDATE tasks
                            SET task_id = COALESCE(?, task_id),
                                status = COALESCE(?, status),
                                tdd_aplicavel = ?,
                                updated_at = ?
                            WHERE id = ?
                            """,
                        ),
                        (
                            scalar_text(front_matter.get("task_id")) or f"T{classified.task_number}",
                            scalar_text(front_matter.get("status")),
                            tdd_val,
                            ts,
                            task_ids[rel],
                        ),
                    )
                task_id = task_ids[rel]
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="task",
                    project_id=pid,
                    feature_id=feature_id,
                    user_story_id=user_story_id,
                    task_id=task_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

            if classified.kind == "user_story_other_md" and classified.user_story_key:
                us_pk = (pid, classified.user_story_key)
                user_story_id = user_story_ids.get(us_pk)
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="user_story_other",
                    project_id=pid,
                    feature_id=feature_id,
                    user_story_id=user_story_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

            if classified.kind == "feature_audit_file" and classified.report_key:
                dr = _adapt_decision_refs(backend, front_matter.get("decision_refs"))
                if rel not in feature_audit_ids:
                    aid = _exec_insert_id(
                        cur,
                        backend,
                        """
                        INSERT INTO feature_audits (
                          feature_id, report_key, status, verdict, scope_type, scope_ref, feature_code,
                          base_commit, compares_to, round_number, supersedes, followup_destination,
                          decision_refs_json, path_relative, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            feature_id,
                            classified.report_key,
                            scalar_text(front_matter.get("status")),
                            scalar_text(front_matter.get("verdict") or front_matter.get("veredito")),
                            scalar_text(front_matter.get("scope_type")),
                            scalar_text(front_matter.get("scope_ref")),
                            scalar_text(front_matter.get("feature_id") or front_matter.get("feature"))
                            or classified.feature_key,
                            scalar_text(front_matter.get("base_commit")),
                            scalar_text(front_matter.get("compares_to")),
                            int_value(front_matter.get("round")),
                            scalar_text(front_matter.get("supersedes")),
                            scalar_text(front_matter.get("followup_destination")),
                            dr,
                            rel,
                            ts,
                        ),
                    )
                    feature_audit_ids[rel] = aid
                else:
                    cur.execute(
                        _sql_ph(
                            backend,
                            """
                            UPDATE feature_audits
                            SET status = COALESCE(?, status),
                                verdict = COALESCE(?, verdict),
                                scope_type = COALESCE(?, scope_type),
                                scope_ref = COALESCE(?, scope_ref),
                                feature_code = COALESCE(?, feature_code),
                                base_commit = COALESCE(?, base_commit),
                                compares_to = COALESCE(?, compares_to),
                                round_number = COALESCE(?, round_number),
                                supersedes = COALESCE(?, supersedes),
                                followup_destination = COALESCE(?, followup_destination),
                                decision_refs_json = COALESCE(?, decision_refs_json),
                                updated_at = ?
                            WHERE id = ?
                            """,
                        ),
                        (
                            scalar_text(front_matter.get("status")),
                            scalar_text(front_matter.get("verdict") or front_matter.get("veredito")),
                            scalar_text(front_matter.get("scope_type")),
                            scalar_text(front_matter.get("scope_ref")),
                            scalar_text(front_matter.get("feature_id") or front_matter.get("feature"))
                            or classified.feature_key,
                            scalar_text(front_matter.get("base_commit")),
                            scalar_text(front_matter.get("compares_to")),
                            int_value(front_matter.get("round")),
                            scalar_text(front_matter.get("supersedes")),
                            scalar_text(front_matter.get("followup_destination")),
                            dr,
                            ts,
                            feature_audit_ids[rel],
                        ),
                    )
                feature_audit_id = feature_audit_ids[rel]
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="feature_audit",
                    project_id=pid,
                    feature_id=feature_id,
                    feature_audit_id=feature_audit_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

            if classified.kind == "feature_other_md":
                insert_document(
                    cur,
                    backend,
                    path_relative=rel,
                    kind="feature_other",
                    project_id=pid,
                    feature_id=feature_id,
                    title=title,
                    body_markdown=body,
                    front_matter=front_matter,
                    content_hash=content_hash,
                    file_mtime=file_mtime,
                    indexed_at_str=indexed_at_str,
                    now_pg=now_pg,
                )
                continue

        insert_document(
            cur,
            backend,
            path_relative=rel,
            kind="unclassified",
            project_id=pid,
            title=title,
            body_markdown=body,
            front_matter=front_matter,
            content_hash=content_hash,
            file_mtime=file_mtime,
            indexed_at_str=indexed_at_str,
            now_pg=now_pg,
        )

    return len(all_md)


def run_sync_sqlite(repo_root: Path, db_path: Path, dry_run: bool) -> None:
    projetos = repo_root / PROJETOS
    if not projetos.is_dir():
        raise SystemExit(f"Pastas em falta: {projetos}")

    all_md = [path for path in projetos.rglob("*.md") if path.is_file()]
    now_pg = datetime.now(timezone.utc).replace(microsecond=0)
    indexed_at_str = now_pg.isoformat()

    if dry_run:
        print(f"repo_root={repo_root}\ndb_path={db_path}\nbackend=sqlite\nmarkdown_files={len(all_md)}")
        return

    db_path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    ensure_schema_sqlite(conn)
    clear_derived_sqlite(cur)

    n = run_index_pass(cur, "sqlite", repo_root, indexed_at_str, now_pg)

    cur.execute("DELETE FROM sync_meta")
    cur.execute(
        "INSERT INTO sync_meta (key, value) VALUES (?, ?)",
        ("last_sync_at", indexed_at_str),
    )
    cur.execute(
        "INSERT INTO sync_meta (key, value) VALUES (?, ?)",
        ("repo_root", str(repo_root.resolve())),
    )
    cur.execute(
        "INSERT INTO sync_meta (key, value) VALUES (?, ?)",
        ("schema_bundle_version", SQLITE_SCHEMA_VERSION),
    )

    rebuild_fts_sqlite(cur)
    conn.commit()
    conn.close()
    print(f"OK: indexados {n} ficheiros -> sqlite {db_path}")


def run_sync_postgres(repo_root: Path, dry_run: bool, sync_trigger: str) -> None:
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Backend postgres requer o pacote psycopg (pip install 'psycopg[binary]')."
        ) from exc

    projetos = repo_root / PROJETOS
    if not projetos.is_dir():
        raise SystemExit(f"Pastas em falta: {projetos}")

    all_md = [path for path in projetos.rglob("*.md") if path.is_file()]
    now_pg = datetime.now(timezone.utc).replace(microsecond=0)
    indexed_at_str = now_pg.isoformat()
    url = resolve_postgres_url()

    if dry_run:
        print(f"repo_root={repo_root}\nbackend=postgres\nurl={url}\nmarkdown_files={len(all_md)}")
        return

    head = git_head_sha(repo_root)
    n = 0
    with psycopg.connect(url, autocommit=False) as conn:
        apply_postgres_schema(conn)
        conn.commit()

        with conn.cursor() as cur:
            clear_derived_postgres(cur)
            run_id = _exec_insert_id(
                cur,
                "postgres",
                """
                INSERT INTO sync_runs (started_at, finished_at, status, repo_root, git_head, schema_version, trigger_source)
                VALUES (?, NULL, 'running', ?, ?, ?, ?)
                """,
                (now_pg, str(repo_root.resolve()), head, POSTGRES_SCHEMA_BUNDLE, sync_trigger),
            )
        conn.commit()

        try:
            with conn.cursor() as cur:
                n = run_index_pass(cur, "postgres", repo_root, indexed_at_str, now_pg)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sync_runs
                    SET finished_at = now(), status = 'success', git_head = COALESCE(%s, git_head),
                        rows_upserted = %s::jsonb, error_message = NULL
                    WHERE id = %s
                    """,
                    (head, json.dumps({"markdown_files": n}), run_id),
                )
            conn.commit()
        except Exception as exc:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE sync_runs
                    SET finished_at = now(), status = 'failed', error_message = %s
                    WHERE id = %s
                    """,
                    (str(exc)[:8000], run_id),
                )
            conn.commit()
            raise

    print(f"OK: indexados {n} ficheiros -> postgres ({POSTGRES_SCHEMA_BUNDLE})")


def run_sync(
    repo_root: Path,
    backend: str | Path | None = "sqlite",
    db_path: Optional[Path] | bool | None = None,
    dry_run: bool = False,
    sync_trigger: str = "cli",
) -> None:
    """
    Compatível com chamadas antigas: run_sync(repo_root, db_path, dry_run=False).
    """
    resolved_backend = "sqlite"
    resolved_db: Optional[Path] = None
    resolved_dry = dry_run

    if isinstance(backend, Path):
        resolved_db = backend
        resolved_backend = "sqlite"
        if isinstance(db_path, bool):
            resolved_dry = db_path
    elif backend in ("sqlite", "postgres"):
        resolved_backend = backend
        resolved_db = db_path if isinstance(db_path, Path) else None
        if isinstance(db_path, bool):
            resolved_dry = db_path
    elif isinstance(backend, str) and backend not in ("sqlite", "postgres"):
        raise SystemExit(f"Backend desconhecido: {backend}")

    if resolved_backend == "sqlite":
        path = resolved_db if resolved_db else default_db_path(repo_root)
        run_sync_sqlite(repo_root, path, resolved_dry)
    elif resolved_backend == "postgres":
        run_sync_postgres(repo_root, resolved_dry, sync_trigger)
    else:
        raise SystemExit(f"Backend desconhecido: {resolved_backend}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sincroniza PROJETOS/ para índice derivado (SQLite ou Postgres)."
    )
    parser.add_argument("--repo-root", default=None, help="Raiz do repositório (contém PROJETOS/).")
    parser.add_argument(
        "--db",
        default=None,
        help="Caminho do ficheiro SQLite (override a OPENCLAW_PROJECTS_DB; só backend sqlite).",
    )
    parser.add_argument(
        "--backend",
        choices=("sqlite", "postgres"),
        default=os.environ.get("OPENCLAW_PROJECTS_INDEX_BACKEND", "sqlite").strip().lower()
        or "sqlite",
        help="Destino do índice (default: sqlite ou OPENCLAW_PROJECTS_INDEX_BACKEND).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Só mostra caminhos resolvidos.")
    parser.add_argument(
        "--sync-trigger",
        default="cli",
        help="Valor gravado em sync_runs.trigger_source (backend postgres).",
    )
    args = parser.parse_args()
    if args.backend not in ("sqlite", "postgres"):
        args.backend = "sqlite"

    try:
        repo_root = resolve_repo_root(args.repo_root)
        db_path = Path(args.db).expanduser().resolve() if args.db else None
        run_sync(
            repo_root,
            args.backend,
            db_path,
            dry_run=args.dry_run,
            sync_trigger=args.sync_trigger,
        )
    except (RuntimeError, ValueError, sqlite3.Error, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:
        # psycopg e outros erros de I/O no backend postgres
        exc_name = type(exc).__module__ + "." + type(exc).__name__
        if "psycopg" in exc_name or "psycopg" in str(type(exc)):
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        raise


if __name__ == "__main__":
    main()
