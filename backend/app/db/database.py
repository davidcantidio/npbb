"""Configuracao de conexao e utilitarios de sessao do SQLModel."""

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

from sqlmodel import create_engine, Session

from app.db.metadata import SQLModel
from dotenv import load_dotenv


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
        "DATABASE_URL nao configurada e fallback SQLite desabilitado para producao/homologacao."
    )


def _build_engine():
    _load_env()
    url = _get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    return create_engine(url, echo=echo, connect_args=connect_args)


engine = _build_engine()


def get_session():
    """Fornece uma sessao de banco para injecao de dependencia."""
    with Session(engine) as session:
        yield session


def init_db():
    """Cria as tabelas com base nos metadados do SQLModel."""
    SQLModel.metadata.create_all(engine)
