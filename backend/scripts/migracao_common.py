"""Helpers compartilhados pelos scripts de migracao F2."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR.parent / "artifacts_migracao"
ARTIFACTS_DIR.mkdir(exist_ok=True)

_TABLE_DATA_PATTERN = re.compile(r"TABLE DATA public ([^ ]+)")


def load_backend_env() -> None:
    """Carrega backend/.env e falha cedo quando o arquivo nao existe."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        raise SystemExit(
            "ERRO: backend/.env nao encontrado. Crie a partir de .env.example e configure "
            "as variaveis de migracao antes de continuar."
        )
    load_dotenv(env_path)


def get_env_value(names: tuple[str, ...], error_message: str) -> str:
    """Retorna o primeiro env var nao vazio entre os nomes informados."""
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    raise SystemExit(error_message)


def check_binary(name: str, install_hint: str | None = None) -> str:
    """Valida que um binario externo esta disponivel no PATH."""
    path = shutil.which(name)
    if not path:
        hint = install_hint or (
            f"Instale o cliente PostgreSQL (ex.: brew install postgresql@16) "
            f"e garanta que {name} esteja no PATH."
        )
        raise SystemExit(f"ERRO: {name} nao encontrado no PATH. {hint}")
    return path


def sqlalchemy_to_libpq(url: str) -> str:
    """Converte URL SQLAlchemy (postgresql+psycopg2://...) para libpq."""
    if not url:
        return ""
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        return url
    return url


def find_latest_artifact(prefix: str) -> Path | None:
    """Retorna o dump mais recente para um prefixo conhecido."""
    matches = sorted(ARTIFACTS_DIR.glob(f"{prefix}_*.dump"), reverse=True)
    return matches[0] if matches else None


def require_latest_artifact(prefix: str, guidance: str) -> Path:
    """Exige que exista um artefato com o prefixo informado."""
    path = find_latest_artifact(prefix)
    if path and path.exists():
        return path
    raise SystemExit(
        f"ERRO: Artefato {prefix} nao encontrado.\n"
        f"{guidance}\n"
        f"Artefatos esperados em: {ARTIFACTS_DIR}"
    )


def validate_dump_with_pg_restore(pg_restore_path: str, path: Path, label: str) -> str:
    """Valida existencia, tamanho e legibilidade de um dump custom."""
    if not path.exists():
        raise SystemExit(f"ERRO: {label} nao encontrado: {path}")
    if path.stat().st_size == 0:
        raise SystemExit(f"ERRO: {label} vazio (tamanho 0): {path}")

    result = subprocess.run(
        [pg_restore_path, "--list", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"ERRO: {label} ilegivel: {path}\n"
            f"pg_restore --list falhou.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return (result.stdout or "") + (result.stderr or "")


def list_public_table_data_entries(pg_restore_path: str, path: Path) -> list[str]:
    """Lista as tabelas public com TABLE DATA presentes em um dump custom."""
    toc = validate_dump_with_pg_restore(pg_restore_path, path, "dump")
    tables = []
    for line in toc.splitlines():
        match = _TABLE_DATA_PATTERN.search(line)
        if not match:
            continue
        table = match.group(1).strip('"')
        if table != "alembic_version":
            tables.append(table)
    return sorted(set(tables))


def validate_export_contract(pg_restore_path: str, export_path: Path) -> None:
    """Bloqueia exports que ainda carregam dados de alembic_version."""
    toc = validate_dump_with_pg_restore(pg_restore_path, export_path, "artefato de export")
    if "alembic_version" in toc:
        raise SystemExit(
            f"ERRO: Artefato incompativel com schema validado em F1: {export_path}\n"
            "O dump contem dados de alembic_version. Execute novamente o backup_export_migracao "
            "com a versao corrigida do script (--exclude-table-data=public.alembic_version)."
        )


def is_local_runtime(url: str) -> bool:
    """True quando a URL aponta para localhost/127.0.0.1."""
    lower = url.lower()
    return "127.0.0.1" in lower or "localhost" in lower


def normalize_db_target(url: str) -> tuple[str, str]:
    """Normaliza host/database para comparar pooler e direct do mesmo projeto."""
    parsed = make_url(url)
    host = (parsed.host or "").lower()
    database = (parsed.database or "postgres").lower()
    if ".supabase.co" in host and "-pooler" in host:
        host = host.replace("-pooler", "")
    return host, database

