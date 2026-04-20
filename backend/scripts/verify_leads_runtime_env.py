"""Gate de ambiente para runtime de importacao de leads.

Valida configuracoes efetivas antes de subir API/worker. O objetivo e impedir
deploy com storage local em producao, API usando conexao direta quando o pooler
e exigido, ou worker sem URL dedicada.

Uso:
  python scripts/verify_leads_runtime_env.py --service api
  python scripts/verify_leads_runtime_env.py --service worker
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent

for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


def _normalized_env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _is_production() -> bool:
    environment = _normalized_env("ENVIRONMENT").lower()
    if environment == "production":
        return True
    public_app_base_url = _normalized_env("PUBLIC_APP_BASE_URL")
    if not public_app_base_url:
        return False
    parsed = urlparse(public_app_base_url)
    return (parsed.hostname or "").lower() not in {"localhost", "127.0.0.1"}


def _safe_db_url_info(url: str) -> dict[str, object]:
    if not url:
        return {"configured": False}
    if url.startswith("sqlite"):
        return {"configured": True, "driver": "sqlite"}
    raw = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    parsed = urlparse(raw)
    return {
        "configured": True,
        "driver": "postgresql",
        "username": parsed.username,
        "host": parsed.hostname,
        "port": parsed.port,
        "database": parsed.path.lstrip("/") or None,
        "pooler_6543": parsed.port == 6543,
        "supabase": "supabase" in (parsed.hostname or "").lower(),
    }


def _should_require_pooler() -> bool:
    raw = _normalized_env("DB_REQUIRE_SUPABASE_POOLER").lower()
    return raw not in {"0", "false", "no", "off"}


def _print_info(service: str, failures: list[str]) -> None:
    print("service:", service)
    print("production_environment:", _is_production())
    print("object_storage_backend:", _normalized_env("OBJECT_STORAGE_BACKEND") or "<unset>")
    print("object_storage_bucket:", _normalized_env("OBJECT_STORAGE_BUCKET") or "<unset>")
    print("database_url:", _safe_db_url_info(_normalized_env("DATABASE_URL")))
    print("direct_url:", _safe_db_url_info(_normalized_env("DIRECT_URL")))
    print("worker_database_url:", _safe_db_url_info(_normalized_env("WORKER_DATABASE_URL")))
    print("db_require_supabase_pooler:", _should_require_pooler())
    if failures:
        print("FAILURES:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)


def _validate_common(failures: list[str]) -> None:
    if _is_production() and (_normalized_env("OBJECT_STORAGE_BACKEND").lower() or "local") == "local":
        failures.append("OBJECT_STORAGE_BACKEND=local nao e permitido em producao")
    if _is_production() and _normalized_env("OBJECT_STORAGE_BACKEND").lower() == "supabase":
        if not (_normalized_env("SUPABASE_STORAGE_URL") or _normalized_env("SUPABASE_URL")):
            failures.append("Supabase storage requer SUPABASE_STORAGE_URL ou SUPABASE_URL")
        if not (_normalized_env("SUPABASE_STORAGE_SERVICE_ROLE_KEY") or _normalized_env("SUPABASE_SERVICE_ROLE_KEY")):
            failures.append("Supabase storage requer service role key")
    if not _normalized_env("OBJECT_STORAGE_BUCKET"):
        failures.append("OBJECT_STORAGE_BUCKET precisa estar definido explicitamente")


def _validate_api(failures: list[str]) -> None:
    database_url = _normalized_env("DATABASE_URL")
    if not database_url:
        failures.append("API requer DATABASE_URL configurada")
        return
    info = _safe_db_url_info(database_url)
    username = str(info.get("username") or "").lower()
    if username.startswith("postgres"):
        failures.append("DATABASE_URL da API nao pode usar role postgres")
    if bool(info.get("supabase")) and _should_require_pooler() and not bool(info.get("pooler_6543")):
        failures.append("DATABASE_URL da API Supabase deve usar transaction pooler na porta 6543")


def _validate_worker(failures: list[str]) -> None:
    worker_url = _normalized_env("WORKER_DATABASE_URL") or _normalized_env("DIRECT_URL")
    if not worker_url:
        failures.append("worker requer WORKER_DATABASE_URL ou DIRECT_URL")
        return
    info = _safe_db_url_info(worker_url)
    username = str(info.get("username") or "").lower()
    if username.startswith("postgres"):
        failures.append("worker nao deve usar role postgres/BYPASSRLS")
    if bool(info.get("supabase")) and bool(info.get("pooler_6543")):
        failures.append("worker Supabase deve usar URL dedicada/direct, nao transaction pooler :6543")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=("api", "worker"), required=True)
    args = parser.parse_args()

    failures: list[str] = []
    _validate_common(failures)
    if args.service == "api":
        _validate_api(failures)
    else:
        _validate_worker(failures)

    _print_info(args.service, failures)
    if failures:
        raise SystemExit(1)
    print("OK: runtime env de leads valido.")


if __name__ == "__main__":
    main()
