"""Captura top queries de pg_stat_statements para evidencia versionada.

Uso:
  python scripts/capture_pg_stat_statements.py --label before
  python scripts/capture_pg_stat_statements.py --label after
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "auditoria" / "evidencias"

for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _url() -> str:
    url = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not url or url.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL Postgres para consultar pg_stat_statements.")
    return url


def _engine(url: str):
    connect_args: dict = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))}
    if "sslmode=" not in url and "ssl=require" not in url and "127.0.0.1" not in url and "localhost" not in url:
        connect_args["sslmode"] = "require"
    return sa.create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="current", help="Sufixo do arquivo: before, after ou current")
    parser.add_argument(
        "--out-dir",
        default=os.getenv("LEADS_AUDIT_EVIDENCE_DIR", str(DEFAULT_OUT_DIR)),
        help="Diretorio versionado para salvar evidencia.",
    )
    args = parser.parse_args()

    lines = [
        f"# pg_stat_statements top 10",
        f"# label: {args.label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
    ]

    with _engine(_url()).connect() as conn:
        installed = conn.execute(
            sa.text("select exists (select 1 from pg_extension where extname = 'pg_stat_statements')")
        ).scalar()
        if not installed:
            lines.append("ERRO: pg_stat_statements nao esta instalado no banco alvo.")
            out_dir = Path(args.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"pg_stat_statements_top10_{args.label}.txt"
            out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"Escrito: {out_file}")
            raise SystemExit(1)

        rows = conn.execute(
            sa.text(
                """
                select
                  row_number() over (order by total_exec_time desc) as rank,
                  calls,
                  round(total_exec_time::numeric, 3) as total_exec_ms,
                  round(mean_exec_time::numeric, 3) as mean_exec_ms,
                  rows,
                  shared_blks_hit,
                  shared_blks_read,
                  temp_blks_read,
                  temp_blks_written,
                  left(regexp_replace(query, '\\s+', ' ', 'g'), 700) as query_sample
                from pg_stat_statements
                where dbid = (select oid from pg_database where datname = current_database())
                order by total_exec_time desc
                limit 10
                """
            )
        ).fetchall()

        lines.append(
            "rank | calls | total_exec_ms | mean_exec_ms | rows | shared_blks_hit | "
            "shared_blks_read | temp_blks_read | temp_blks_written | query_sample"
        )
        for row in rows:
            lines.append(" | ".join(str(item) for item in row))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"pg_stat_statements_top10_{args.label}.txt"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {out_file}")


if __name__ == "__main__":
    main()
