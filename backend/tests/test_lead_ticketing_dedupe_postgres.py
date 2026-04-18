"""PostgreSQL-only concurrency checks for ticketing dedupe (Task 3).

Requires a disposable database; set NPBB_POSTGRES_TEST_URL, e.g.:
postgresql+psycopg2://user:pass@127.0.0.1:5432/npbb_dedupe_test

Post-check query (must return zero rows):

    SELECT cpf,
           COALESCE(TRIM(email), '') AS email_n,
           COALESCE(TRIM(evento_nome), '') AS evento_n,
           COALESCE(TRIM(sessao), '') AS sessao_n,
           COUNT(*) AS n
    FROM lead
    WHERE NULLIF(TRIM(cpf), '') IS NOT NULL
    GROUP BY 1, 2, 3, 4
    HAVING COUNT(*) > 1;
"""

from __future__ import annotations

import os
import threading
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine, select

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

pytestmark = pytest.mark.postgres


def _postgres_url() -> str | None:
    return os.environ.get("NPBB_POSTGRES_TEST_URL")


@pytest.fixture(scope="module")
def postgres_engine() -> "Engine":
    url = _postgres_url()
    if not url:
        pytest.skip("Defina NPBB_POSTGRES_TEST_URL para testes @postgres")

    import app.models.models  # noqa: F401 — regista todas as tabelas no metadata

    engine = create_engine(url, poolclass=NullPool, pool_pre_ping=True)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


def _seed_minimal_evento(session: Session):
    from app.models.models import Evento, StatusEvento

    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    if status is None:
        status = StatusEvento(nome="Previsto")
        session.add(status)
        session.commit()
        session.refresh(status)

    evento = Evento(
        nome="Evento Dedupe Postgres",
        cidade="Brasilia",
        estado="DF",
        status_id=status.id,
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def test_parallel_persist_lead_batch_one_lead(postgres_engine: "Engine") -> None:
    """Dois imports paralelos com mesmo CPF, sessao nula e email ausente não criam dois leads."""

    from app.models.models import Lead
    from app.modules.leads_publicidade.application.etl_import.persistence import persist_lead_batch

    with Session(postgres_engine) as session:
        evento = _seed_minimal_evento(session)
        evento_id = int(evento.id)

    cpf = "10000000019"
    payload: dict[str, object] = {
        "email": None,
        "cpf": cpf,
        "nome": "Lead Concorrente",
        "evento_nome": "Evento Dedupe Postgres",
        "sessao": None,
    }

    barrier = threading.Barrier(2)
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            with Session(postgres_engine) as session:
                barrier.wait()
                persist_lead_batch(session, [(payload, 1)], canonical_evento_id=evento_id)
                session.commit()
        except BaseException as exc:
            errors.append(exc)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert not errors, f"workers failed: {errors!r}"

    with Session(postgres_engine) as session:
        rows = session.exec(select(Lead).where(Lead.cpf == cpf)).all()
        assert len(rows) == 1

        dup_groups = session.execute(
            text(
                """
                SELECT COUNT(*) FROM (
                  SELECT cpf,
                         COALESCE(TRIM(email), '') AS email_n,
                         COALESCE(TRIM(evento_nome), '') AS evento_n,
                         COALESCE(TRIM(sessao), '') AS sessao_n,
                         COUNT(*) AS n
                  FROM lead
                  WHERE NULLIF(TRIM(cpf), '') IS NOT NULL
                  GROUP BY 1, 2, 3, 4
                  HAVING COUNT(*) > 1
                ) AS dupes
                """
            )
        ).scalar_one()
        assert int(dup_groups) == 0
