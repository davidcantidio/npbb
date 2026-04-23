"""Configuracao de conexao, contexto RLS e utilitarios de sessao do SQLModel."""

import os
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from sqlalchemy import event, text
from sqlmodel import create_engine, Session

from app.db.metadata import SQLModel
from dotenv import load_dotenv


def _env_int(name: str, default: int, *, min_value: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if min_value is not None:
        return max(min_value, value)
    return value


def _safe_db_endpoint(url: str) -> dict:
    """Host/porta para logs (sem credenciais)."""
    if url.startswith("sqlite"):
        return {"driver": "sqlite"}
    raw = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    try:
        p = urlparse(raw)
        return {
            "driver": "postgresql",
            "host": p.hostname,
            "port": p.port,
            "uses_supabase_pooler_6543": p.port == 6543,
        }
    except Exception:
        return {"driver": "postgresql", "parse": "failed"}


def _should_enforce_supabase_runtime_guard() -> bool:
    raw = os.getenv("DB_REQUIRE_SUPABASE_POOLER", "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _validate_supabase_runtime_url(url: str) -> None:
    if not _should_enforce_supabase_runtime_guard() or url.startswith("sqlite"):
        return
    raw = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    if "supabase" not in host:
        return
    if parsed.port != 6543:
        hint = ""
        if host.startswith("db.") and host.endswith(".supabase.co"):
            hint = (
                " Parece que DATABASE_URL esta com o host direto (tipico de DIRECT_URL/worker). "
                "Para a API use o transaction pooler na porta 6543 e uma role dedicada (ex.: npbb_api), "
                "conforme backend/.env.example."
            )
        raise RuntimeError(
            "DATABASE_URL de runtime da API deve usar o transaction pooler do Supabase (:6543), "
            "nao a conexao direta :5432." + hint
        )
    username = (parsed.username or "").lower()
    if username.startswith("postgres"):
        raise RuntimeError(
            "DATABASE_URL de runtime da API nao pode usar a role postgres/BYPASSRLS. Configure uma role dedicada de runtime."
        )


def get_database_endpoint_info() -> dict:
    """Retorna informacoes nao sensiveis do banco configurado."""
    return _safe_db_endpoint(str(engine.url))


def _load_env() -> None:
    """Carrega variaveis de ambiente do .env mais alto disponivel."""
    candidate_paths = [
        Path(__file__).resolve().parents[2] / ".env",  # backend/.env
        Path(__file__).resolve().parent.parent / ".env",  # app/.env (legado)
    ]
    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path)
            return
    load_dotenv()


def _get_database_url() -> str:
    # pytest sets up imports before executing tests; `PYTEST_CURRENT_TEST` is not reliable
    # at module-import time. Detecting `pytest` in sys.modules keeps tests local/offline.
    is_test = os.getenv("TESTING", "").lower() == "true" or "pytest" in sys.modules
    if is_test:
        url_test = os.getenv("DATABASE_URL_TEST")
        if url_test:
            return url_test
        url = os.getenv("DATABASE_URL")
        if url and os.getenv("FORCE_DATABASE_URL_IN_TESTS", "").lower() == "true":
            return url
        return "sqlite:///./app.db"

    url = os.getenv("DATABASE_URL")
    if url:
        return url

    user = (
        os.getenv("DB_USER")
        or os.getenv("USER")
        or os.getenv("user")
    )
    password = (
        os.getenv("DB_PASSWORD")
        or os.getenv("PASSWORD")
        or os.getenv("password")
    )
    host = (
        os.getenv("DB_HOST")
        or os.getenv("HOST")
        or os.getenv("host")
    )
    port = (
        os.getenv("DB_PORT")
        or os.getenv("PORT")
        or os.getenv("port")
        or "5432"
    )
    dbname = (
        os.getenv("DB_NAME")
        or os.getenv("DBNAME")
        or os.getenv("dbname")
    )
    if user and password and host and dbname:
        sslmode = os.getenv("DB_SSLMODE", "require")
        user_enc = quote_plus(user)
        password_enc = quote_plus(password)
        return (
            f"postgresql+psycopg2://{user_enc}:{password_enc}"
            f"@{host}:{port}/{dbname}?sslmode={sslmode}"
        )
    raise RuntimeError(
        "DATABASE_URL obrigatoria (fora de testes): edite backend/.env e preencha DATABASE_URL "
        "(Supabase ou Postgres local). Copiar .env.example sem substituir o valor deixa a chave vazia e falha ao subir a API."
    )


def get_worker_database_url() -> str:
    _load_env()
    worker_url = (os.getenv("WORKER_DATABASE_URL") or os.getenv("DIRECT_URL") or "").strip()
    if worker_url:
        return worker_url
    return _get_database_url()


def _pool_kwargs_for_url(url: str) -> dict:
    """Opções de pool para Postgres remoto (ex.: Supabase + PgBouncer)."""
    if url.startswith("sqlite"):
        return {}
    kwargs: dict = {
        "pool_pre_ping": True,
        "pool_recycle": _env_int("DB_POOL_RECYCLE", 2800, min_value=1),
        "pool_timeout": _env_int("DB_POOL_TIMEOUT", 5, min_value=1),
    }
    if os.getenv("DB_POOL_SIZE"):
        kwargs["pool_size"] = _env_int("DB_POOL_SIZE", 5, min_value=1)
    if os.getenv("DB_MAX_OVERFLOW"):
        kwargs["max_overflow"] = _env_int("DB_MAX_OVERFLOW", 5)
    return kwargs


def _postgres_connect_args() -> dict:
    connect_args: dict = {
        "connect_timeout": _env_int("DB_CONNECT_TIMEOUT", 5, min_value=1),
        "keepalives": 1,
        "keepalives_idle": _env_int("DB_KEEPALIVES_IDLE", 30, min_value=1),
        "keepalives_interval": _env_int("DB_KEEPALIVES_INTERVAL", 10, min_value=1),
        "keepalives_count": _env_int("DB_KEEPALIVES_COUNT", 3, min_value=1),
    }
    statement_timeout_ms = _env_int("DB_STATEMENT_TIMEOUT_MS", 15000, min_value=0)
    db_options = os.getenv("DB_OPTIONS", "").strip()
    options: list[str] = []
    if db_options:
        options.append(db_options)
    if statement_timeout_ms > 0:
        options.append(f"-c statement_timeout={statement_timeout_ms}")
    if options:
        connect_args["options"] = " ".join(options)
    return connect_args


def _build_engine_from_url(url: str):
    if url.startswith("sqlite"):
        connect_args: dict = {"check_same_thread": False}
    else:
        connect_args = _postgres_connect_args()
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    engine_kwargs: dict = {"echo": echo, "connect_args": connect_args, **_pool_kwargs_for_url(url)}
    return create_engine(url, **engine_kwargs)


def _dialect_name_for_session(session: Session) -> str:
    bind = session.get_bind()
    return str(getattr(getattr(bind, "dialect", None), "name", "") or "").lower()


def _is_postgres_session(session: Session) -> bool:
    return _dialect_name_for_session(session) == "postgresql"


def _build_engine():
    _load_env()
    url = _get_database_url()
    _validate_supabase_runtime_url(url)
    return _build_engine_from_url(url)


engine = _build_engine()


def set_db_request_context(
    session: Session,
    *,
    user_id: int | None,
    user_type: str | None = None,
    agencia_id: int | None = None,
) -> None:
    context_payload = {
        "user_id": str(user_id or ""),
        "user_type": str(user_type or ""),
        "agencia_id": str(agencia_id or ""),
    }
    session.info["npbb_db_context"] = context_payload
    if not _is_postgres_session(session):
        return
    session.execute(
        text(
            """
            select
                set_config('app.user_id', :user_id, true),
                set_config('app.user_type', :user_type, true),
                set_config('app.agencia_id', :agencia_id, true)
            """
        ),
        context_payload,
    )


def set_internal_service_db_context(session: Session) -> None:
    set_db_request_context(session, user_id=None, user_type="npbb", agencia_id=None)


@event.listens_for(Session, "after_begin")
def _reapply_db_request_context(session: Session, transaction, connection) -> None:
    context_payload = session.info.get("npbb_db_context")
    if not isinstance(context_payload, dict):
        return
    if str(getattr(connection.dialect, "name", "") or "").lower() != "postgresql":
        return
    connection.execute(
        text(
            """
            select
                set_config('app.user_id', :user_id, true),
                set_config('app.user_type', :user_type, true),
                set_config('app.agencia_id', :agencia_id, true)
            """
        ),
        context_payload,
    )


@lru_cache(maxsize=1)
def _build_cached_worker_engine():
    return _build_engine_from_url(get_worker_database_url())


def build_worker_engine():
    if os.getenv("TESTING", "").strip().lower() == "true":
        return engine
    return _build_cached_worker_engine()


def get_session():
    """Fornece uma sessao de banco para injecao de dependencia."""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise


def init_db():
    """Cria as tabelas com base nos metadados do SQLModel."""
    SQLModel.metadata.create_all(engine)
