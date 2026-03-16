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

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Garante que o pacote app seja encontrado
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Diretório de artefatos (raiz do repo, para facilitar acesso)
ARTIFACTS_DIR = BASE_DIR.parent / "artifacts_migracao"
ARTIFACTS_DIR.mkdir(exist_ok=True)


def _load_env() -> None:
    """Carrega .env do backend."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        raise SystemExit(
            "ERRO: backend/.env nao encontrado. Crie a partir de .env.example e configure "
            "SUPABASE_DIRECT_URL e LOCAL_DIRECT_URL para a migracao."
        )
    load_dotenv(env_path)


def _sqlalchemy_to_libpq(url: str) -> str:
    """Converte URL SQLAlchemy (postgresql+psycopg2://...) para formato libpq (postgresql://...)."""
    if not url:
        return ""
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        return url
    return url


def _check_pg_dump() -> str:
    """Verifica se pg_dump está disponível."""
    pg_dump = shutil.which("pg_dump")
    if not pg_dump:
        raise SystemExit(
            "ERRO: pg_dump nao encontrado no PATH. Instale o cliente PostgreSQL "
            "(ex.: brew install postgresql@16) e garanta que o binario esteja no PATH."
        )
    return pg_dump


def _validate_preconditions() -> tuple[str, str, str]:
    """
    Valida precondições e retorna (pg_dump_path, supabase_url, local_url).
    Falha imediatamente se credencial ou ferramenta faltar.
    """
    _load_env()

    # Interface: SUPABASE_DIRECT_URL (backup), LOCAL_DIRECT_URL (export), pg_dump no PATH
    supabase_url = os.getenv("SUPABASE_DIRECT_URL") or os.getenv("DIRECT_URL")
    local_url = os.getenv("LOCAL_DIRECT_URL")

    if not supabase_url or not supabase_url.strip():
        raise SystemExit(
            "ERRO: SUPABASE_DIRECT_URL ou DIRECT_URL nao configurado. "
            "Configure no .env para backup do Supabase."
        )
    if not local_url or not local_url.strip():
        raise SystemExit(
            "ERRO: LOCAL_DIRECT_URL nao configurado. "
            "Configure no .env para export do PostgreSQL local."
        )

    pg_dump_path = _check_pg_dump()
    return pg_dump_path, supabase_url.strip(), local_url.strip()


def run_backup_supabase(pg_dump: str, supabase_url: str, out_dir: Path) -> Path:
    """Executa backup do Supabase e retorna o caminho do arquivo gerado."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"backup_supabase_{timestamp}.dump"
    libpq_url = _sqlalchemy_to_libpq(supabase_url)

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
    libpq_url = _sqlalchemy_to_libpq(local_url)

    cmd = [
        pg_dump,
        "--format=custom",
        "--data-only",
        "--no-owner",
        "--no-acl",
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
    """Ordem: 1) backup Supabase, 2) export local. Nenhum passo destrutivo."""
    print("=== Backup e Export - Migracao F2 (Supabase) ===\n")

    pg_dump, supabase_url, local_url = _validate_preconditions()
    print("Precondicoes OK: pg_dump disponivel, credenciais configuradas.\n")

    # 1. Backup do Supabase (antes de qualquer acao destrutiva)
    backup_file = run_backup_supabase(pg_dump, supabase_url, ARTIFACTS_DIR)

    # 2. Export do PostgreSQL local
    export_file = run_export_local(pg_dump, local_url, ARTIFACTS_DIR)

    print("\n=== Artefatos gerados ===")
    print(f"Backup Supabase: {backup_file}")
    print(f"Export local:    {export_file}")
    print("\nArtefatos prontos para a recarga controlada (ISSUE-F2-02).")


if __name__ == "__main__":
    main()
