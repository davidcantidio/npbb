"""Configuração de conexão e utilitários de sessão do SQLModel."""

import os

from sqlmodel import create_engine, SQLModel, Session


def _build_engine():
    """Cria engine lendo DATABASE_URL do ambiente; fallback local para dev/test."""
    url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, echo=os.getenv("SQL_ECHO", "false").lower() == "true", connect_args=connect_args)


engine = _build_engine()


def get_session():
    """Fornece uma sessão de banco para injeção de dependência."""
    with Session(engine) as session:
        yield session


def init_db():
    """Cria as tabelas com base nos metadados do SQLModel."""
    SQLModel.metadata.create_all(engine)
