"""Configuração de conexão e utilitários de sessão do SQLModel."""

import os
from pathlib import Path

from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv


def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # fallback apenas para testes locais ou execução sem env
    return "sqlite:///./app.db"


def _build_engine():
    _load_env()
    url = _get_database_url()
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    return create_engine(url, echo=echo, connect_args=connect_args)


engine = _build_engine()


def get_session():
    """Fornece uma sessão de banco para injeção de dependência."""
    with Session(engine) as session:
        yield session


def init_db():
    """Cria as tabelas com base nos metadados do SQLModel."""
    SQLModel.metadata.create_all(engine)
