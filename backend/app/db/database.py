"""Configuração de conexão e utilitários de sessão do SQLModel."""

import os
from pathlib import Path

from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv


def _load_env():
    """Carrega variáveis de ambiente do .env mais alto disponível.

    Priorizamos o .env na raiz de backend/ (onde o .env.example está),
    mas mantemos o fallback para app/.env para compatibilidade.
    """
    candidate_paths = [
        Path(__file__).resolve().parents[2] / ".env",  # backend/.env
        Path(__file__).resolve().parent.parent / ".env",  # app/.env (legado)
    ]
    for env_path in candidate_paths:
        if env_path.exists():
            load_dotenv(env_path)
            return
    # Fallback: respeita variáveis já carregadas pelo ambiente
    load_dotenv()


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
