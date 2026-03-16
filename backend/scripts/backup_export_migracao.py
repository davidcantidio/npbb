"""
Automação de backup do Supabase e export do PostgreSQL local (F2 - Migração).

Objetivo: produzir os artefatos da rodada de dados (backup Supabase + export local)
com comandos reproduzíveis e seguros, antes de qualquer passo destrutivo.

Referência: docs/RUNBOOK-MIGRACAO-SUPABASE.md

Interface:
- Inputs: SUPABASE_DIRECT_URL (backup), LOCAL_DIRECT_URL (export)
- Precondições: pg_dump e pg_restore no PATH; credenciais válidas; F1 concluída
- Saídas: backup_supabase_*.dump, export_local_*.dump
- Nenhum passo destrutivo no Supabase.

Contrato de validação final (ISSUE-F2-01-003):
- A automação só anuncia sucesso para F2-02 após validar objetivamente os dumps.
- Validação mínima obrigatória: (1) arquivo existe e tem tamanho > 0;
  (2) pg_restore --list executa sem erro (confirma formato custom legível).
- Se qualquer validação falhar, o fluxo termina com SystemExit sem imprimir
  a mensagem de prontidao. Ordem: backup -> export -> validação final -> sucesso.

Uso:
  cd backend && python -m scripts.backup_export_migracao
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from scripts.migracao_common import (
    ARTIFACTS_DIR,
    check_binary,
    get_env_value,
    load_backend_env,
    sqlalchemy_to_libpq,
    validate_dump_with_pg_restore,
)


def _validate_preconditions() -> tuple[str, str, str, str]:
    """
    Valida precondições e retorna (pg_dump_path, pg_restore_path, supabase_url, local_url).
    Falha imediatamente se credencial ou ferramenta faltar.
    """
    load_backend_env()

    # Interface: SUPABASE_DIRECT_URL (backup), LOCAL_DIRECT_URL (export), pg_dump e pg_restore no PATH
    supabase_url = get_env_value(
        ("SUPABASE_DIRECT_URL", "DIRECT_URL"),
        "ERRO: SUPABASE_DIRECT_URL ou DIRECT_URL nao configurado. "
        "Configure no .env para backup do Supabase.",
    )
    local_url = get_env_value(
        ("LOCAL_DIRECT_URL",),
        "ERRO: LOCAL_DIRECT_URL nao configurado. "
        "Configure no .env para export do PostgreSQL local.",
    )

    pg_dump_path = check_binary("pg_dump")
    pg_restore_path = check_binary("pg_restore")
    return pg_dump_path, pg_restore_path, supabase_url, local_url


def run_backup_supabase(pg_dump: str, supabase_url: str, out_dir: Path) -> Path:
    """Executa backup do Supabase e retorna o caminho do arquivo gerado."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"backup_supabase_{timestamp}.dump"
    libpq_url = sqlalchemy_to_libpq(supabase_url)

    cmd = [
        pg_dump,
        "--format=custom",
        "--no-owner",
        "--no-acl",
        "-f", str(out_file),
        libpq_url,
    ]
    print(f"Executando backup do Supabase -> {out_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"ERRO: pg_dump do Supabase falhou.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    print(f"Backup do Supabase gerado: {out_file}")
    return out_file


def run_export_local(pg_dump: str, local_url: str, out_dir: Path) -> Path:
    """Executa export do PostgreSQL local (data-only) e retorna o caminho do arquivo gerado."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"export_local_{timestamp}.dump"
    libpq_url = sqlalchemy_to_libpq(local_url)

    # ISSUE-F2-02-003: excluir alembic_version do dump para compatibilidade com schema validado em F1
    cmd = [
        pg_dump,
        "--format=custom",
        "--data-only",
        "--no-owner",
        "--no-acl",
        "--exclude-table-data=public.alembic_version",
        "-f", str(out_file),
        libpq_url,
    ]
    print(f"Executando export do PostgreSQL local -> {out_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"ERRO: pg_dump do PostgreSQL local falhou.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    print(f"Export local gerado: {out_file}")
    return out_file


def main() -> None:
    """Ordem: 1) backup Supabase, 2) export local, 3) validação final. Nenhum passo destrutivo."""
    print("=== Backup e Export - Migracao F2 (Supabase) ===\n")

    pg_dump, pg_restore, supabase_url, local_url = _validate_preconditions()
    print("Precondicoes OK: pg_dump, pg_restore disponiveis, credenciais configuradas.\n")

    # 1. Backup do Supabase (antes de qualquer acao destrutiva)
    backup_file = run_backup_supabase(pg_dump, supabase_url, ARTIFACTS_DIR)

    # 2. Export do PostgreSQL local
    export_file = run_export_local(pg_dump, local_url, ARTIFACTS_DIR)

    # 3. Validação final dos artefatos (antes de declarar prontidao para F2-02)
    validate_dump_with_pg_restore(pg_restore, backup_file, "backup do Supabase")
    validate_dump_with_pg_restore(pg_restore, export_file, "export local")

    print("\n=== Artefatos gerados ===")
    print(f"Backup Supabase: {backup_file}")
    print(f"Export local:    {export_file}")
    print("\nArtefatos prontos para a recarga controlada (ISSUE-F2-02).")


if __name__ == "__main__":
    main()
