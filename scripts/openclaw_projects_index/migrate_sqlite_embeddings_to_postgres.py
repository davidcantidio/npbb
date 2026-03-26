#!/usr/bin/env python3
"""
Copia embeddings do SQLite v4 (BLOB float32) para Postgres (pgvector), alinhando por
(path_relative do documento, chunk_index, model).

Pré-requisitos:
  - Postgres já populado com sync --backend postgres e chunk_documents --backend postgres
    (mesmos path_relative e ordem de chunks que no SQLite de origem, após re-sync equivalente).
  - Dimensão do vetor no Postgres (schema_postgres.sql: vector(1536)) deve coincidir com len(blob)/4.

Uso:
  python3 scripts/openclaw_projects_index/migrate_sqlite_embeddings_to_postgres.py \\
    --sqlite-db PATH [--database-url URL]

Variáveis: OPENCLAW_PROJECTS_DATABASE_URL, OPENCLAW_PGSSLMODE (opcional).
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path


def _pg_url(cli: str | None) -> str:
    url = (cli or "").strip() or os.environ.get("OPENCLAW_PROJECTS_DATABASE_URL", "").strip()
    if not url:
        raise SystemExit("Defina OPENCLAW_PROJECTS_DATABASE_URL ou --database-url.")
    sslmode = os.environ.get("OPENCLAW_PGSSLMODE", "").strip()
    if sslmode and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode={sslmode}"
    return url


def blob_to_floats(blob: bytes) -> list[float]:
    if len(blob) % 4 != 0:
        raise ValueError(f"BLOB length {len(blob)} not multiple of 4 (float32)")
    n = len(blob) // 4
    return list(struct.unpack(f"<{n}f", blob))


def main() -> None:
    try:
        import psycopg
        import sqlite3
    except ModuleNotFoundError as exc:
        raise SystemExit("Requer sqlite3 (stdlib) e psycopg instalado.") from exc

    ap = argparse.ArgumentParser(description="Migra embeddings SQLite -> Postgres pgvector.")
    ap.add_argument("--sqlite-db", required=True, type=Path, help="Caminho do openclaw-projects.sqlite")
    ap.add_argument("--database-url", default=None, help="Postgres URL (default: env).")
    ap.add_argument("--dry-run", action="store_true", help="Só contar linhas, não escrever.")
    args = ap.parse_args()

    sqlite_path = args.sqlite_db.expanduser().resolve()
    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite em falta: {sqlite_path}")

    sl = sqlite3.connect(str(sqlite_path))
    sl.row_factory = sqlite3.Row
    cur_sl = sl.cursor()
    cur_sl.execute(
        """
        SELECT e.model, e.embedding, dc.chunk_index, d.path_relative
        FROM embeddings e
        JOIN document_chunks dc ON dc.id = e.chunk_id
        JOIN documents d ON d.id = dc.document_id
        """
    )
    rows = cur_sl.fetchall()
    sl.close()

    if args.dry_run:
        print(f"dry-run: {len(rows)} embeddings a migrar")
        return

    pg_url = _pg_url(args.database_url)

    migrated = 0
    skipped = 0
    with psycopg.connect(pg_url) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM embeddings")
            for row in rows:
                model = row["model"]
                blob = row["embedding"]
                chunk_index = row["chunk_index"]
                path_rel = row["path_relative"]
                try:
                    vec = blob_to_floats(blob)
                except ValueError:
                    skipped += 1
                    continue
                cur.execute(
                    "SELECT id FROM documents WHERE path_relative = %s",
                    (path_rel,),
                )
                drow = cur.fetchone()
                if not drow:
                    skipped += 1
                    continue
                doc_pg_id = drow[0]
                cur.execute(
                    """
                    SELECT id FROM document_chunks
                    WHERE document_id = %s AND chunk_index = %s
                    """,
                    (doc_pg_id, chunk_index),
                )
                crow = cur.fetchone()
                if not crow:
                    skipped += 1
                    continue
                chunk_pg_id = crow[0]
                vec_lit = "[" + ",".join(str(float(x)) for x in vec) + "]"
                cur.execute(
                    """
                    INSERT INTO embeddings (chunk_id, model, embedding)
                    VALUES (%s, %s, CAST(%s AS vector))
                    ON CONFLICT (chunk_id, model) DO UPDATE SET embedding = EXCLUDED.embedding
                    """,
                    (chunk_pg_id, model, vec_lit),
                )
                migrated += 1
        conn.commit()

    print(f"OK: migrados {migrated} embeddings; ignorados {skipped}")


if __name__ == "__main__":
    main()
