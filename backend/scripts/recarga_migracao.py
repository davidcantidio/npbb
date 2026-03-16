"""
Recarga controlada de dados no Supabase (F2 - Migração, ISSUE-F2-02-001).

Objetivo: substituir os dados antigos do Supabase pelos dados do PostgreSQL local,
com limpeza controlada e import conforme runbook aprovado.

Referência: docs/RUNBOOK-MIGRACAO-SUPABASE.md

Interface:
- Inputs: SUPABASE_DIRECT_URL (ou DIRECT_URL), artefatos em artifacts_migracao/
- Pré-requisitos: backup Supabase e export local existentes; pg_restore no PATH
- Caminho de recarga: pg_restore (formato custom do backup_export_migracao)

Uso:
  cd backend && python -m scripts.recarga_migracao
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# Garante que o pacote app seja encontrado
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ARTIFACTS_DIR = BASE_DIR.parent / "artifacts_migracao"

# Caminho de recarga: pg_restore (export usa --format=custom)
RECARGA_PATH = "pg_restore"


def _load_env() -> None:
    """Carrega .env do backend."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        raise SystemExit(
            "ERRO: backend/.env nao encontrado. Crie a partir de .env.example e configure "
            "SUPABASE_DIRECT_URL (ou DIRECT_URL) para a recarga."
        )
    load_dotenv(env_path)


def _get_supabase_url() -> str:
    """Retorna a URL direta do Supabase."""
    url = os.getenv("SUPABASE_DIRECT_URL") or os.getenv("DIRECT_URL")
    if not url or not url.strip():
        raise SystemExit(
            "ERRO: SUPABASE_DIRECT_URL ou DIRECT_URL nao configurado. "
            "Configure no .env para recarga no Supabase."
        )
    return url.strip()


def _check_pg_restore() -> str:
    """Verifica se pg_restore está disponível."""
    path = shutil.which("pg_restore")
    if not path:
        raise SystemExit(
            "ERRO: pg_restore nao encontrado no PATH. Instale o cliente PostgreSQL "
            "(ex.: brew install postgresql@16) e garanta que o binario esteja no PATH."
        )
    return path


def _sqlalchemy_to_libpq(url: str) -> str:
    """Converte URL SQLAlchemy (postgresql+psycopg2://...) para formato libpq (postgresql://...)."""
    if not url:
        return ""
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        return url
    return url


def _find_latest_artifact(prefix: str) -> Path | None:
    """Retorna o artefato mais recente com o prefixo dado."""
    if not ARTIFACTS_DIR.exists():
        return None
    matches = sorted(ARTIFACTS_DIR.glob(f"{prefix}_*.dump"), reverse=True)
    return matches[0] if matches else None


def _validate_artifact_contract(pg_restore_path: str, export_path: Path) -> None:
    """
    ISSUE-F2-02-003: Pre-valida o artefato de export antes de qualquer passo destrutivo.
    Bloqueia a recarga se o dump contiver dados de alembic_version (contrato incompatível com F1).
    """
    cmd = [pg_restore_path, "--list", str(export_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"ERRO: Artefato ilegivel para pre-validacao: {export_path}\n"
            f"pg_restore --list falhou.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    combined = (result.stdout or "") + (result.stderr or "")
    if "alembic_version" in combined:
        raise SystemExit(
            f"ERRO: Artefato incompativel com schema validado em F1: {export_path}\n"
            "O dump contem dados de alembic_version. Execute novamente o backup_export_migracao "
            "com a versao corrigida do script (--exclude-table-data=public.alembic_version)."
        )


def validate_preconditions() -> tuple[str, str, Path, Path]:
    """
    T1: Valida precondições e retorna (pg_restore_path, supabase_url, backup_path, export_path).
    Bloqueia execução se backup, export ou credenciais faltarem.
    """
    _load_env()

    # 1. Confirmar caminho de recarga (pg_restore)
    pg_restore_path = _check_pg_restore()

    # 2. Confirmar backup do Supabase e export local
    backup_path = _find_latest_artifact("backup_supabase")
    export_path = _find_latest_artifact("export_local")

    if not backup_path or not backup_path.exists():
        raise SystemExit(
            "ERRO: Backup do Supabase nao encontrado. Execute primeiro:\n"
            "  cd backend && python -m scripts.backup_export_migracao\n"
            f"Artefatos esperados em: {ARTIFACTS_DIR}"
        )
    if not export_path or not export_path.exists():
        raise SystemExit(
            "ERRO: Export local nao encontrado. Execute primeiro:\n"
            "  cd backend && python -m scripts.backup_export_migracao\n"
            f"Artefatos esperados em: {ARTIFACTS_DIR}"
        )

    # 3. Conferir DIRECT_URL do Supabase
    supabase_url = _get_supabase_url()

    # 4. ISSUE-F2-02-003: Pre-validar contrato do artefato (antes de qualquer passo destrutivo)
    _validate_artifact_contract(pg_restore_path, export_path)

    return pg_restore_path, supabase_url, backup_path, export_path


def run_limpeza_controlada(supabase_url: str) -> None:
    """
    T2: Executa limpeza controlada do Supabase na ordem segura (TRUNCATE CASCADE).
    Interrompe imediatamente em erro de FK ou transacional.
    """
    engine = create_engine(supabase_url)

    with engine.connect() as conn:
        # Obter tabelas do schema public (excluindo alembic_version)
        result = conn.execute(
            text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                  AND table_name != 'alembic_version'
                ORDER BY table_name
            """)
        )
        tables = [row[0] for row in result]

    if not tables:
        raise SystemExit("ERRO: Nenhuma tabela encontrada no schema public.")

    # TRUNCATE ... CASCADE: PostgreSQL resolve dependências de FK automaticamente
    tables_quoted = ", ".join(f'"{t}"' for t in tables)
    truncate_sql = f"TRUNCATE TABLE {tables_quoted} CASCADE"

    print("Executando limpeza controlada (TRUNCATE CASCADE)...")
    with engine.begin() as conn:
        try:
            conn.execute(text(truncate_sql))
        except Exception as e:
            raise SystemExit(
                f"ERRO: Limpeza falhou. Ordem segura nao garantida ou risco nao previsto.\n"
                f"Detalhe: {e}\n"
                "Nao prossiga. Verifique o runbook e o backup do Supabase."
            ) from e

    print("Limpeza concluida. Ambiente alvo pronto para importacao.")


def run_importacao(pg_restore_path: str, supabase_url: str, export_path: Path) -> None:
    """
    T3: Importa no Supabase o dataset do PostgreSQL local via pg_restore.
    ISSUE-F2-02-003: --single-transaction garante atomicidade; qualquer erro faz rollback.
    Interrompe imediatamente em retorno nao zero (fail-fast).
    """
    libpq_url = _sqlalchemy_to_libpq(supabase_url)

    cmd = [
        pg_restore_path,
        "--data-only",
        "--no-owner",
        "--no-acl",
        "--single-transaction",
        "-d", libpq_url,
        str(export_path),
    ]
    print(f"Executando importacao: pg_restore -> Supabase")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"ERRO: Importacao falhou. Falha estrutural ou schema fora do escopo aprovado.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    print("Importacao concluida. Dados locais carregados no Supabase.")


def _get_runtime_url() -> str | None:
    """Retorna DATABASE_URL (contrato de runtime) ou None se ausente."""
    url = os.getenv("DATABASE_URL")
    return url.strip() if url and url.strip() else None


def _is_local_runtime(url: str) -> bool:
    """True se a URL aponta para PostgreSQL local (127.0.0.1, localhost)."""
    lower = url.lower()
    return "127.0.0.1" in lower or "localhost" in lower


def _normalize_db_target(url: str) -> tuple[str, str]:
    """
    ISSUE-F2-02-004: Retorna (host_normalizado, database) para comparacao de alvo.
    Para Supabase, pooler e direct do mesmo projeto compartilham o host apos remover -pooler.
    """
    parsed = make_url(url)
    host = (parsed.host or "").lower()
    database = (parsed.database or "postgres").lower()
    if ".supabase.co" in host and "-pooler" in host:
        host = host.replace("-pooler", "")
    return (host, database)


def run_consolidacao(supabase_url: str, backup_path: Path, export_path: Path) -> None:
    """
    T4: Consolida o estado final da recarga para a etapa de validação.
    Valida contrato de manutenção (DIRECT_URL) e contrato de runtime (DATABASE_URL).
    Só libera para ISSUE-F2-02-002 quando DATABASE_URL estiver alinhada ao mesmo
    Supabase alvo da recarga (ISSUE-F2-02-004: conectividade remota isolada não basta).
    """
    # 1. Validar conexão direta (manutenção) - já usada na limpeza/import
    engine_direct = create_engine(supabase_url)
    try:
        with engine_direct.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise SystemExit(
            f"ERRO: Supabase recarregado nao acessivel via DIRECT_URL. Ambiente nao apto para validacao pos-carga.\n"
            f"Detalhe: {e}"
        ) from e

    # 2. ISSUE-F2-02-003: Validar contrato de runtime (DATABASE_URL) para liberar F2-02-002
    runtime_url = _get_runtime_url()
    if not runtime_url:
        raise SystemExit(
            "ERRO: DATABASE_URL nao configurada. A consolidacao so libera para ISSUE-F2-02-002 "
            "quando o contrato de runtime (DATABASE_URL) estiver configurado para o Supabase. "
            "Configure DATABASE_URL no .env apontando para o pooler do Supabase (porta 6543)."
        )
    if _is_local_runtime(runtime_url):
        raise SystemExit(
            "ERRO: DATABASE_URL aponta para PostgreSQL local (127.0.0.1/localhost). "
            "A consolidacao so libera para ISSUE-F2-02-002 quando DATABASE_URL estiver "
            "configurada para o Supabase (pooler ou direct). Ajuste o .env e execute novamente."
        )

    # 3. Validar que o runtime (DATABASE_URL) conecta
    engine_runtime = create_engine(runtime_url)
    try:
        with engine_runtime.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise SystemExit(
            f"ERRO: DATABASE_URL (runtime) nao conecta. Ambiente nao apto para validacao pos-carga.\n"
            f"Detalhe: {e}\n"
            "Verifique se DATABASE_URL aponta para o pooler/direct do Supabase e se as credenciais estao corretas."
        ) from e

    # 4. ISSUE-F2-02-004: Validar alinhamento entre runtime e alvo recarregado
    target_supabase = _normalize_db_target(supabase_url)
    target_runtime = _normalize_db_target(runtime_url)
    if target_supabase != target_runtime:
        raise SystemExit(
            "ERRO: DATABASE_URL aponta para alvo diferente do Supabase recarregado. "
            "A consolidacao so libera quando o runtime (DATABASE_URL) estiver alinhado ao mesmo "
            "Supabase da recarga (DIRECT_URL). Conectividade remota isolada nao basta. "
            "Ajuste DATABASE_URL no .env para o pooler/direct do Supabase alvo e execute novamente."
        )

    print("\n=== Consolidacao da rodada ===")
    print("Caminho usado: pg_restore (formato custom)")
    print(f"Backup Supabase preservado: {backup_path}")
    print(f"Export local utilizado: {export_path}")
    print("Resultado: recarga concluida com sucesso")
    print("Contratos validados: DIRECT_URL (manutencao) e DATABASE_URL (runtime) alinhados ao Supabase alvo da recarga.")
    print("\nBackup do Supabase preservado ate o encerramento da validacao da F3.")
    print("Ambiente pronto para validacao pos-carga (ISSUE-F2-02-002).")


def main() -> None:
    """Ordem: 1) validar precondições, 2) limpar, 3) importar, 4) consolidar."""
    pg_restore_path, supabase_url, backup_path, export_path = validate_preconditions()

    print("=== Recarga Controlada - Migracao F2 (Supabase) ===\n")
    print("Precondicoes OK:")
    print(f"  - Caminho de recarga: {RECARGA_PATH}")
    print(f"  - Backup Supabase: {backup_path}")
    print(f"  - Export local: {export_path}")
    print(f"  - Supabase DIRECT_URL configurada\n")

    # T2: Limpeza controlada
    run_limpeza_controlada(supabase_url)

    # T3: Importação
    run_importacao(pg_restore_path, supabase_url, export_path)

    # T4: Consolidação
    run_consolidacao(supabase_url, backup_path, export_path)


if __name__ == "__main__":
    main()
