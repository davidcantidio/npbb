"""Verifica estado pos-migrations de leads (Alembic, RLS helpers, policies).

Uso (a partir da raiz do repo ou de backend/):
  python scripts/verify_leads_hardening_db.py

Requer DIRECT_URL ou DATABASE_URL em backend/.env (preferir DIRECT_URL :5432
para inspecao; evita pooler para queries administrativas leves).

Quando o Supabase MCP (execute_sql) estiver disponivel no Cursor, as mesmas
queries podem ser coladas no painel SQL do projeto com o mesmo efeito.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _database_url() -> str:
    direct = (os.getenv("DIRECT_URL") or "").strip()
    if direct:
        return direct
    db = (os.getenv("DATABASE_URL") or "").strip()
    if db:
        return db
    raise SystemExit(
        "Defina DIRECT_URL ou DATABASE_URL em backend/.env para verificar o schema."
    )


def main() -> None:
    url = _database_url()
    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "15"))
    connect_args: dict = {"connect_timeout": connect_timeout}
    if "sqlite" in url.lower():
        engine = sa.create_engine(url)
    else:
        if "sslmode=" not in url and "ssl=require" not in url and "127.0.0.1" not in url and "localhost" not in url:
            connect_args["sslmode"] = "require"
        engine = sa.create_engine(url, connect_args=connect_args)

    with engine.connect() as conn:
        rows = conn.execute(
            sa.text("SELECT version_num FROM alembic_version ORDER BY version_num")
        ).fetchall()
        versions = [r[0] for r in rows]
        print("alembic_version:", versions)
        required_any = ("3f7b9c2d1e4a", "7a3c8d1e2f4b")
        if not any(v in versions for v in required_any):
            print(
                "AVISO: migrations de hardening de leads ausentes — rode "
                "`alembic upgrade head` com DIRECT_URL no Postgres alvo.",
                file=sys.stderr,
            )

        funcs = conn.execute(
            sa.text(
                """
                SELECT proname
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'public' AND proname LIKE 'npbb_%'
                ORDER BY 1
                """
            )
        ).fetchall()
        print("funcoes_npbb:", [r[0] for r in funcs])

        pol = conn.execute(
            sa.text(
                """
                SELECT tablename, policyname
                FROM pg_policies
                WHERE schemaname = 'public'
                  AND tablename IN (
                    'lead_batches', 'leads_silver', 'lead_import_etl_preview_session',
                    'lead_import_etl_job', 'lead_import_etl_staging', 'lead_column_aliases'
                  )
                ORDER BY tablename, policyname
                """
            )
        ).fetchall()
        print(f"policies_fluxo_importacao: {len(pol)} linhas")
        for r in pol:
            print(f"  {r[0]}.{r[1]}")

        idx = conn.execute(
            sa.text(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'lead'
                  AND indexname = 'idx_lead_data_compra_not_null'
                """
            )
        ).fetchone()
        print("idx_lead_data_compra_not_null:", "ok" if idx else "ausente")

        col = conn.execute(
            sa.text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'lead_batches'
                  AND column_name IN (
                    'bronze_storage_bucket', 'bronze_storage_key', 'arquivo_bronze'
                  )
                ORDER BY column_name
                """
            )
        ).fetchall()
        print("colunas_lead_batches_storage:", [r[0] for r in col])


if __name__ == "__main__":
    main()
