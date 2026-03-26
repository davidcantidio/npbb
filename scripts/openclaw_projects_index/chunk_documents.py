#!/usr/bin/env python3
"""
Preenche a tabela document_chunks a partir de documents.body_markdown (pós-sync).

Não gera embeddings; use um pipeline à parte que leia chunks e escreva em `embeddings`.

Uso:
  python3 scripts/openclaw_projects_index/chunk_documents.py [--backend sqlite|postgres] [--db PATH] [--max-chars N]

Postgres: requer OPENCLAW_PROJECTS_DATABASE_URL (ou --database-url).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def default_sqlite_db_path() -> Path:
    env = os.environ.get("OPENCLAW_PROJECTS_DB", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve().parent.parent.parent
    return (here / ".openclaw" / "openclaw-projects.sqlite").resolve()


def split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text] if text else []
    paras = split_paragraphs(text)
    if not paras:
        return []
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for p in paras:
        plen = len(p) + (2 if buf else 0)
        if size + plen > max_chars and buf:
            chunks.append("\n\n".join(buf))
            buf = [p]
            size = len(p)
        else:
            buf.append(p)
            size += plen
    if buf:
        chunks.append("\n\n".join(buf))
    out: list[str] = []
    for c in chunks:
        if len(c) <= max_chars:
            out.append(c)
            continue
        for i in range(0, len(c), max_chars):
            out.append(c[i : i + max_chars])
    return out


def _sync_dir() -> Path:
    return Path(__file__).resolve().parent


def _pg_url(cli_url: str | None) -> str:
    url = (cli_url or "").strip() or os.environ.get("OPENCLAW_PROJECTS_DATABASE_URL", "").strip()
    if not url:
        raise SystemExit(
            "Postgres: defina OPENCLAW_PROJECTS_DATABASE_URL ou passe --database-url."
        )
    sslmode = os.environ.get("OPENCLAW_PGSSLMODE", "").strip()
    if sslmode and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode={sslmode}"
    return url


def run_sqlite(db_path: Path, max_chars: int) -> None:
    if not db_path.is_file():
        print(f"Base em falta: {db_path}", file=sys.stderr)
        sys.exit(1)

    now = _utc_now_iso()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("DELETE FROM embeddings")
    cur.execute("DELETE FROM document_chunks")
    cur.execute(
        """
        SELECT id, path_relative, body_markdown, content_hash
        FROM documents
        WHERE body_markdown IS NOT NULL AND TRIM(body_markdown) != ''
        """
    )
    rows = cur.fetchall()
    total_chunks = 0
    for doc_id, _path_rel, body, _doc_hash in rows:
        pieces = chunk_text(body, max_chars)
        for idx, piece in enumerate(pieces):
            h = hashlib.sha256(piece.encode("utf-8")).hexdigest()
            cur.execute(
                """
                INSERT INTO document_chunks (
                  document_id, chunk_index, text, token_count, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (doc_id, idx, piece, None, h, now),
            )
            total_chunks += 1
    conn.commit()
    conn.close()
    print(f"OK: {len(rows)} documentos -> {total_chunks} chunks (sqlite) em {db_path}")


def run_postgres(database_url: str, max_chars: int) -> None:
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise SystemExit("Instale psycopg: pip install 'psycopg[binary]'") from exc

    from postgres_schema_util import apply_postgres_schema_file

    schema_path = _sync_dir() / "schema_postgres.sql"
    with psycopg.connect(database_url) as conn:
        apply_postgres_schema_file(conn, schema_path)
        conn.commit()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    rows: list = []
    total_chunks = 0
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM embeddings")
            cur.execute("DELETE FROM document_chunks")
            cur.execute(
                """
                SELECT id, path_relative, body_markdown, content_hash
                FROM documents
                WHERE body_markdown IS NOT NULL AND TRIM(body_markdown) <> ''
                """
            )
            rows = list(cur.fetchall())
            for doc_id, _path_rel, body, _doc_hash in rows:
                if body is None:
                    continue
                pieces = chunk_text(str(body), max_chars)
                for idx, piece in enumerate(pieces):
                    h = hashlib.sha256(piece.encode("utf-8")).hexdigest()
                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                          document_id, chunk_index, text, token_count, content_hash, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (doc_id, idx, piece, None, h, now),
                    )
                    total_chunks += 1
        conn.commit()
    print(f"OK: {len(rows)} documentos -> {total_chunks} chunks (postgres)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Chunk documents para RAG (sem embeddings).")
    ap.add_argument(
        "--backend",
        choices=("sqlite", "postgres"),
        default=os.environ.get("OPENCLAW_PROJECTS_INDEX_BACKEND", "sqlite").strip().lower() or "sqlite",
    )
    ap.add_argument(
        "--db",
        default=None,
        help="Caminho do SQLite (default: OPENCLAW_PROJECTS_DB ou openclaw-workspace/.openclaw/).",
    )
    ap.add_argument("--database-url", default=None, help="Override a OPENCLAW_PROJECTS_DATABASE_URL (postgres).")
    ap.add_argument("--max-chars", type=int, default=2000, help="Tamanho máximo aproximado por chunk.")
    args = ap.parse_args()

    if args.backend == "sqlite":
        db_path = Path(args.db).expanduser().resolve() if args.db else default_sqlite_db_path()
        run_sqlite(db_path, args.max_chars)
    else:
        url = _pg_url(args.database_url)
        run_postgres(url, args.max_chars)


if __name__ == "__main__":
    main()
