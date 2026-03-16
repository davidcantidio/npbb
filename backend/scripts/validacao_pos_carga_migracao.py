"""Validacao pos-carga e rollback da migracao F2 (ISSUE-F2-02-002)."""

from __future__ import annotations

import subprocess

from sqlalchemy import create_engine, text

from scripts.migracao_common import (
    check_binary,
    get_env_value,
    is_local_runtime,
    list_public_table_data_entries,
    load_backend_env,
    normalize_db_target,
    require_latest_artifact,
    validate_dump_with_pg_restore,
)


def _validate_pg_restore_help(pg_restore_path: str) -> None:
    """Confirma que o caminho de restore segue operacionalmente viavel."""
    result = subprocess.run(
        [pg_restore_path, "--help"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            "ERRO: pg_restore --help falhou. O caminho de rollback nao esta operacionalmente viavel.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


def _collect_public_snapshot(url: str, selected_tables: list[str] | None = None) -> tuple[list[str], dict[str, int]]:
    """Lista tabelas public e coleta um snapshot simples de contagem com uma conexao unica."""
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                      AND table_name != 'alembic_version'
                    ORDER BY table_name
                    """
                )
            )
            available_tables = [row[0] for row in result]
            tables_to_count = selected_tables or available_tables
            row_counts = {}
            for table_name in tables_to_count:
                count_result = conn.execute(text(f'SELECT COUNT(*) FROM public."{table_name}"'))
                row_counts[table_name] = int(count_result.scalar_one())
            return available_tables, row_counts
    except Exception as exc:
        raise SystemExit(
            "ERRO: Nao foi possivel coletar o snapshot de tabelas do Supabase recarregado.\n"
            f"Detalhe: {exc}"
        ) from exc


def _validate_connectivity(direct_url: str, runtime_url: str) -> None:
    """Confirma conectividade minima nas duas rotas usadas pela fase."""
    for label, url in (("DIRECT_URL", direct_url), ("DATABASE_URL", runtime_url)):
        engine = create_engine(url)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as exc:
            raise SystemExit(
                f"ERRO: {label} nao conecta. A validacao pos-carga nao pode prosseguir.\n"
                f"Detalhe: {exc}"
            ) from exc


def run_validacao_pos_carga() -> dict[str, object]:
    """Executa o checklist minimo de integridade pos-carga e rollback."""
    load_backend_env()

    pg_restore_path = check_binary("pg_restore")
    _validate_pg_restore_help(pg_restore_path)

    direct_url = get_env_value(
        ("SUPABASE_DIRECT_URL", "DIRECT_URL"),
        "ERRO: SUPABASE_DIRECT_URL ou DIRECT_URL nao configurado. "
        "Configure no .env a conexao direct do Supabase para a validacao pos-carga.",
    )
    runtime_url = get_env_value(
        ("DATABASE_URL",),
        "ERRO: DATABASE_URL nao configurada. Configure no .env o runtime apontando para o Supabase alvo.",
    )
    if is_local_runtime(runtime_url):
        raise SystemExit(
            "ERRO: DATABASE_URL aponta para PostgreSQL local (127.0.0.1/localhost). "
            "A validacao pos-carga exige runtime apontando para o Supabase alvo."
        )

    backup_path = require_latest_artifact(
        "backup_supabase",
        "Execute primeiro:\n  cd backend && python -m scripts.backup_export_migracao",
    )
    export_path = require_latest_artifact(
        "export_local",
        "Execute primeiro:\n  cd backend && python -m scripts.backup_export_migracao",
    )

    validate_dump_with_pg_restore(pg_restore_path, backup_path, "backup do Supabase")
    validate_dump_with_pg_restore(pg_restore_path, export_path, "export local")

    if normalize_db_target(direct_url) != normalize_db_target(runtime_url):
        raise SystemExit(
            "ERRO: DATABASE_URL aponta para alvo diferente da conexao direct usada na recarga. "
            "A validacao pos-carga exige runtime e manutencao alinhados ao mesmo projeto Supabase."
        )

    _validate_connectivity(direct_url, runtime_url)

    exported_tables = list_public_table_data_entries(pg_restore_path, export_path)
    available_tables, row_counts = _collect_public_snapshot(direct_url, exported_tables or None)
    if not available_tables:
        raise SystemExit(
            "ERRO: Nenhuma tabela de aplicacao foi encontrada no schema public do Supabase recarregado."
        )

    missing_tables = [table for table in exported_tables if table not in available_tables]
    if missing_tables:
        raise SystemExit(
            "ERRO: O Supabase recarregado nao contem todas as tabelas listadas no export local.\n"
            f"Tabelas ausentes: {', '.join(missing_tables)}"
        )

    rollback_triggers = [
        "DATABASE_URL e DIRECT_URL deixarem de apontar para o mesmo projeto Supabase.",
        "backup_supabase mais recente ficar ilegivel ou indisponivel para pg_restore.",
        "qualquer tabela exportada no dump local ficar ausente ou inacessivel no Supabase recarregado.",
        "checagens de conectividade ou de contagem de tabelas falharem durante a validacao final da F3.",
    ]

    return {
        "backup_path": backup_path,
        "export_path": export_path,
        "exported_tables": exported_tables,
        "available_tables": available_tables,
        "row_counts": row_counts,
        "rollback_triggers": rollback_triggers,
    }


def main() -> None:
    """Executa a validacao pos-carga e imprime o checklist consolidado."""
    result = run_validacao_pos_carga()

    backup_path = result["backup_path"]
    export_path = result["export_path"]
    exported_tables = result["exported_tables"]
    available_tables = result["available_tables"]
    row_counts = result["row_counts"]
    rollback_triggers = result["rollback_triggers"]

    print("=== Validacao Pos-Carga - Migracao F2 (Supabase) ===\n")
    print("Checklist de integridade:")
    print(f"[x] Backup preservado e legivel: {backup_path}")
    print(f"[x] Export local preservado e legivel: {export_path}")
    print("[x] pg_restore disponivel para eventual rollback nao destrutivo")
    print("[x] DIRECT_URL e DATABASE_URL conectam e apontam para o mesmo Supabase alvo")
    print(f"[x] Tabelas public disponiveis no alvo: {len(available_tables)}")
    if exported_tables:
        print(f"[x] Tabelas com TABLE DATA no export presentes no alvo: {len(exported_tables)}")
    else:
        print("[x] Export local legivel, sem entradas TABLE DATA em public; revisar contexto do dataset")

    print("\nSnapshot de contagem por tabela:")
    for table_name, count in row_counts.items():
        print(f"- public.{table_name}: {count}")

    print("\nCriterios objetivos para rollback:")
    for trigger in rollback_triggers:
        print(f"- {trigger}")

    print("\nResultado: validacao pos-carga concluida. F2 apta para liberar F3 se nao houver outras divergencias.")


if __name__ == "__main__":
    main()
