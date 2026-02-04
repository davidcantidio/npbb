from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.models import Lead


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_lead_dedupe_por_evento_e_sessao():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        lead1 = Lead(
            nome="Joao",
            sobrenome="Silva",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1990, 1, 1),
            evento_nome="Evento A",
            sessao="Sessao 1",
        )
        session.add(lead1)
        session.commit()

        lead2 = Lead(
            nome="Maria",
            sobrenome="Souza",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1991, 2, 2),
            evento_nome="Evento B",
            sessao="Sessao 1",
        )
        session.add(lead2)
        session.commit()

        lead3 = Lead(
            nome="Joao",
            sobrenome="Silva",
            cpf="12345678900",
            email="joao@example.com",
            data_nascimento=date(1990, 1, 1),
            evento_nome="Evento A",
            sessao="Sessao 1",
        )
        session.add(lead3)
        with pytest.raises(IntegrityError):
            session.commit()
