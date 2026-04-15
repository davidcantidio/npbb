"""Configuracao de conexao e utilitarios de sessao do SQLModel."""

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus, urlparse

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


def _agent_debug_ndjson(
    location: str,
    message: str,
    data: dict,
    hypothesis_id: str,
) -> None:
    # #region agent log
    try:
        # Raiz do backend (npbb/backend/debug-649b68.log), visível junto ao .env / .venv
        log_path = Path(__file__).resolve().parents[2] / "debug-649b68.log"
        line = json.dumps(
            {
                "sessionId": "649b68",
                "timestamp": int(time.time() * 1000),
                "location": location,
                "message": message,
                "data": data,
                "hypothesisId": hypothesis_id,
            },
            ensure_ascii=False,
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass
    # #endregion


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


def _build_engine():
    _load_env()
    url = _get_database_url()
    if url.startswith("sqlite"):
        connect_args: dict = {"check_same_thread": False}
    else:
        connect_args = _postgres_connect_args()
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    engine_kwargs: dict = {"echo": echo, "connect_args": connect_args, **_pool_kwargs_for_url(url)}
    # #region agent log
    eng = create_engine(url, **engine_kwargs)
    pool = eng.pool
    _agent_debug_ndjson(
        "database.py:_build_engine",
        "engine_created",
        {
            "endpoint": _safe_db_endpoint(url),
            "pool_pre_ping": getattr(pool, "_pre_ping", None),
            "pool_class": type(pool).__name__,
            "pool_recycle": getattr(pool, "_recycle", None),
        },
        "H1",
    )
    # #endregion
    return eng


engine = _build_engine()


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
