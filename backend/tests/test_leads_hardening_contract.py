from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RLS_MIGRATION = REPO_ROOT / "backend" / "alembic" / "versions" / "8b6f4c2d9a1e_apply_central_leads_rls_policies.py"
ROLES_SQL = REPO_ROOT / "backend" / "scripts" / "sql" / "create_npbb_runtime_roles.sql"
RUNTIME_ENV_GATE = REPO_ROOT / "backend" / "scripts" / "verify_leads_runtime_env.py"
DB_GATE = REPO_ROOT / "backend" / "scripts" / "verify_leads_hardening_db.py"


def test_central_leads_rls_migration_covers_core_tables_and_policies() -> None:
    contents = RLS_MIGRATION.read_text(encoding="utf-8")
    assert 'down_revision = "7a3c8d1e2f4b"' in contents
    assert "CENTRAL_RLS_TABLES = (" in contents
    assert 'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY' in contents

    for table_name in ("usuario", "evento", "ativacao", "ativacao_lead", "lead", "lead_evento"):
        assert f'    "{table_name}",' in contents

    for policy_name in (
        "usuario_select",
        "evento_select",
        "ativacao_select",
        "ativacao_lead_select",
        "lead_select",
        "lead_evento_select",
    ):
        assert policy_name in contents

    assert "npbb_current_user_id" in contents
    assert "npbb_current_user_type" in contents
    assert "npbb_current_agencia_id" in contents
    assert "npbb_is_internal_user" in contents


def test_runtime_roles_sql_explicitly_removes_bypassrls_from_dedicated_roles() -> None:
    contents = ROLES_SQL.read_text(encoding="utf-8")
    assert "CREATE ROLE npbb_api WITH LOGIN" in contents
    assert "CREATE ROLE npbb_worker WITH LOGIN" in contents
    assert "ALTER ROLE npbb_api WITH NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION NOBYPASSRLS;" in contents
    assert "ALTER ROLE npbb_worker WITH NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION NOBYPASSRLS;" in contents


def test_leads_deploy_gates_fail_closed_on_runtime_and_db_hardening() -> None:
    runtime_gate = RUNTIME_ENV_GATE.read_text(encoding="utf-8")
    db_gate = DB_GATE.read_text(encoding="utf-8")

    assert "OBJECT_STORAGE_BACKEND=local nao e permitido em producao" in runtime_gate
    assert "DATABASE_URL da API Supabase deve usar transaction pooler na porta 6543" in runtime_gate
    assert "worker requer WORKER_DATABASE_URL ou DIRECT_URL" in runtime_gate

    assert 'REQUIRED_ALEMBIC_VERSION = "8b6f4c2d9a1e"' in db_gate
    assert "roles dedicadas ausentes" in db_gate
    assert "RLS desligada em tabelas esperadas" in db_gate
    assert "rolbypassrls" in db_gate
