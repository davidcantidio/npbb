"""Configuração de conexão e utilitários de sessão do SQLModel."""

from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "postgresql://USER:PASSWORD@HOST:PORT/DBNAME"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Fornece uma sessão de banco para injeção de dependência."""
    with Session(engine) as session:
        yield session

def init_db():
    """Cria as tabelas com base nos metadados do SQLModel."""
    SQLModel.metadata.create_all(engine)
