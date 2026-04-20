"""Gate de banco para hardening do fluxo de importacao de leads.

Este script nao aplica migrations e nao cria roles. Ele consulta o Postgres alvo
e falha quando a evidencia minima de RLS/roles/storage nao esta presente.

Uso:
  python scripts/verify_leads_hardening_db.py

Requer DIRECT_URL ou DATABASE_URL em backend/.env. Para inspecao de catalogo,
prefira DIRECT_URL.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import sqlalchemy as sa
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
REQUIRED_ALEMBIC_VERSION = "a9b8c7d6e5f4"

CENTRAL_RLS_TABLES = (
    "usuario",
    "evento",
    "ativacao",
    "ativacao_lead",
    "lead",
    "lead_evento",
)

IMPORT_RLS_TABLES = (
    "lead_batches",
    "leads_silver",
    "lead_import_etl_preview_session",
    "lead_import_etl_job",
    "lead_import_etl_staging",
    "lead_column_aliases",
)

REQUIRED_POLICIES: dict[str, set[str]] = {
    "usuario": {"usuario_select", "usuario_insert", "usuario_update", "usuario_delete"},
    "evento": {"evento_select", "evento_insert", "evento_update", "evento_delete"},
    "ativacao": {"ativacao_select", "ativacao_insert", "ativacao_update", "ativacao_delete"},
    "ativacao_lead": {
        "ativacao_lead_select",
        "ativacao_lead_insert",
        "ativacao_lead_update",
        "ativacao_lead_delete",
    },
    "lead": {"lead_select", "lead_insert", "lead_update", "lead_delete"},
    "lead_evento": {
        "lead_evento_select",
        "lead_evento_insert",
        "lead_evento_update",
        "lead_evento_delete",
    },
    "lead_batches": {
        "lead_batches_select",
        "lead_batches_insert",
        "lead_batches_update",
        "lead_batches_delete",
    },
    "leads_silver": {
        "leads_silver_select",
        "leads_silver_insert",
        "leads_silver_update",
        "leads_silver_delete",
    },
    "lead_import_etl_preview_session": {
        "lead_import_etl_preview_session_select",
        "lead_import_etl_preview_session_insert",
        "lead_import_etl_preview_session_update",
        "lead_import_etl_preview_session_delete",
    },
    "lead_import_etl_job": {
        "lead_import_etl_job_select",
        "lead_import_etl_job_insert",
        "lead_import_etl_job_update",
        "lead_import_etl_job_delete",
    },
    "lead_import_etl_staging": {
        "lead_import_etl_staging_select",
        "lead_import_etl_staging_insert",
        "lead_import_etl_staging_update",
        "lead_import_etl_staging_delete",
    },
    "lead_column_aliases": {
        "lead_column_aliases_select",
        "lead_column_aliases_insert",
        "lead_column_aliases_update",
        "lead_column_aliases_delete",
    },
}

RUNTIME_ROLES = ("npbb_api", "npbb_worker")
REQUIRED_CONTEXT_FUNCTIONS = (
    "npbb_current_user_id",
    "npbb_current_user_type",
    "npbb_current_agencia_id",
    "npbb_is_internal_user",
)


for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
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
    raise SystemExit("Defina DIRECT_URL ou DATABASE_URL para verificar o schema alvo.")


def _quote_list(values: tuple[str, ...]) -> str:
    return ", ".join("'" + value.replace("'", "''") + "'" for value in values)


def _print_rows(title: str, rows: list[tuple]) -> None:
    print(title)
    if not rows:
        print("  <sem linhas>")
        return
    for row in rows:
        print("  " + " | ".join(str(item) for item in row))


def _connect_engine(url: str):
    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "15"))
    connect_args: dict = {"connect_timeout": connect_timeout}
    if (
        "sqlite" not in url.lower()
        and "sslmode=" not in url
        and "ssl=require" not in url
        and "127.0.0.1" not in url
        and "localhost" not in url
    ):
        connect_args["sslmode"] = "require"
    if "sqlite" in url.lower():
        return sa.create_engine(url)
    return sa.create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def main() -> None:
    failures: list[str] = []
    url = _database_url()
    engine = _connect_engine(url)

    with engine.connect() as conn:
        if conn.dialect.name != "postgresql":
            raise SystemExit("Este gate exige Postgres; SQLite nao tem pg_policies/RLS.")

        runtime = conn.execute(
            sa.text(
                """
                select current_user, session_user, inet_server_addr()::text, inet_server_port()
                """
            )
        ).fetchone()
        print("runtime_connection:", tuple(runtime) if runtime else None)

        versions = [
            row[0]
            for row in conn.execute(sa.text("select version_num from alembic_version order by version_num")).fetchall()
        ]
        print("alembic_version:", versions)
        if REQUIRED_ALEMBIC_VERSION not in versions:
            failures.append(f"migration {REQUIRED_ALEMBIC_VERSION} nao aplicada no banco alvo")

        funcs = [
            row[0]
            for row in conn.execute(
                sa.text(
                    """
                    select p.proname
                    from pg_proc p
                    join pg_namespace n on n.oid = p.pronamespace
                    where n.nspname = 'public'
                      and p.proname in (
                        'npbb_current_user_id',
                        'npbb_current_user_type',
                        'npbb_current_agencia_id',
                        'npbb_is_internal_user'
                      )
                    order by 1
                    """
                )
            ).fetchall()
        ]
        print("funcoes_contexto_rls:", funcs)
        missing_funcs = sorted(set(REQUIRED_CONTEXT_FUNCTIONS) - set(funcs))
        if missing_funcs:
            failures.append(f"funcoes de contexto RLS ausentes: {missing_funcs}")

        all_tables = CENTRAL_RLS_TABLES + IMPORT_RLS_TABLES
        table_filter = _quote_list(all_tables)
        rls_rows = conn.execute(
            sa.text(
                f"""
                select c.relname, c.relrowsecurity, c.relforcerowsecurity
                from pg_class c
                join pg_namespace n on n.oid = c.relnamespace
                where n.nspname = 'public'
                  and c.relname in ({table_filter})
                order by c.relname
                """
            )
        ).fetchall()
        _print_rows("rls_tables: relname | relrowsecurity | relforcerowsecurity", rls_rows)
        rls_by_table = {row[0]: bool(row[1]) for row in rls_rows}
        missing_tables = sorted(set(all_tables) - set(rls_by_table))
        if missing_tables:
            failures.append(f"tabelas RLS esperadas ausentes no schema: {missing_tables}")
        disabled_tables = sorted(table for table, enabled in rls_by_table.items() if not enabled)
        if disabled_tables:
            failures.append(f"RLS desligada em tabelas esperadas: {disabled_tables}")

        policy_rows = conn.execute(
            sa.text(
                f"""
                select tablename, policyname, cmd
                from pg_policies
                where schemaname = 'public'
                  and tablename in ({table_filter})
                order by tablename, policyname
                """
            )
        ).fetchall()
        _print_rows("pg_policies: tablename | policyname | cmd", policy_rows)
        policies_by_table: dict[str, set[str]] = {}
        for table_name, policy_name, _cmd in policy_rows:
            policies_by_table.setdefault(table_name, set()).add(policy_name)
        for table_name, required in REQUIRED_POLICIES.items():
            missing = sorted(required - policies_by_table.get(table_name, set()))
            if missing:
                failures.append(f"policies ausentes em {table_name}: {missing}")

        role_filter = _quote_list(RUNTIME_ROLES)
        role_rows = conn.execute(
            sa.text(
                f"""
                select rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb
                from pg_roles
                where rolname in ({role_filter})
                order by rolname
                """
            )
        ).fetchall()
        _print_rows("runtime_roles: rolname | rolsuper | rolbypassrls | rolcreaterole | rolcreatedb", role_rows)
        roles_by_name = {row[0]: row for row in role_rows}
        missing_roles = sorted(set(RUNTIME_ROLES) - set(roles_by_name))
        if missing_roles:
            failures.append(f"roles dedicadas ausentes: {missing_roles}")
        for role_name, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb in role_rows:
            if rolsuper or rolbypassrls or rolcreaterole or rolcreatedb:
                failures.append(
                    "role runtime insegura: "
                    f"{role_name} rolsuper={rolsuper} rolbypassrls={rolbypassrls} "
                    f"rolcreaterole={rolcreaterole} rolcreatedb={rolcreatedb}"
                )

        storage_cols = conn.execute(
            sa.text(
                """
                select column_name
                from information_schema.columns
                where table_schema = 'public'
                  and table_name = 'lead_batches'
                  and column_name in (
                    'arquivo_bronze',
                    'bronze_storage_bucket',
                    'bronze_storage_key',
                    'bronze_content_type',
                    'bronze_size_bytes',
                    'bronze_uploaded_at'
                  )
                order by column_name
                """
            )
        ).fetchall()
        _print_rows("lead_batches_storage_columns", storage_cols)
        expected_storage_cols = {
            "arquivo_bronze",
            "bronze_storage_bucket",
            "bronze_storage_key",
            "bronze_content_type",
            "bronze_size_bytes",
            "bronze_uploaded_at",
        }
        present_storage_cols = {row[0] for row in storage_cols}
        if not expected_storage_cols.issubset(present_storage_cols):
            failures.append(f"colunas de storage ausentes: {sorted(expected_storage_cols - present_storage_cols)}")

        pending = conn.execute(
            sa.text(
                """
                select 'lead_batches' as table_name, count(*)::bigint as pending
                from lead_batches
                where arquivo_bronze is not null
                  and coalesce(bronze_storage_key, '') = ''
                union all
                select 'lead_import_etl_job' as table_name, count(*)::bigint as pending
                from lead_import_etl_job
                where file_blob is not null
                  and coalesce(file_storage_key, '') = ''
                order by table_name
                """
            )
        ).fetchall()
        _print_rows("storage_backfill_pending: table_name | pending", pending)

        idx = conn.execute(
            sa.text(
                """
                select schemaname, tablename, indexname
                from pg_indexes
                where schemaname = 'public'
                  and indexname in (
                    'idx_lead_data_compra_not_null',
                    'idx_lead_evento_evento_id_lead_id',
                    'ix_lead_batch_id',
                    'ix_lead_batches_evento_id',
                    'ix_lead_batches_ativacao_id',
                    'ix_leads_silver_batch_id_row_index'
                  )
                order by tablename, indexname
                """
            )
        ).fetchall()
        _print_rows("indices_operacionais", idx)

    if failures:
        print("FAILURES:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)

    print("OK: hardening de leads verificado no banco alvo.")


if __name__ == "__main__":
    main()
