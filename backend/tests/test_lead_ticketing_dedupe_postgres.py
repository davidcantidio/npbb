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

from datetime import datetime, timezone
import os
import threading
from typing import TYPE_CHECKING

import pytest
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
    from app.modules.lead_imports.application.etl_import.persistence import persist_lead_batch

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


def test_gold_set_based_insert_reimport_anchored_by_evento_id_reuses_existing_lead(
    postgres_engine: "Engine",
    tmp_path,
) -> None:
    from app.models.lead_batch import BatchStage, LeadBatch
    from app.models.models import Lead, LeadEvento, Usuario
    from app.services.lead_pipeline_service import _inserir_leads_gold
    from app.utils.security import hash_password

    with Session(postgres_engine) as session:
        evento = _seed_minimal_evento(session)
        user = Usuario(
            email="gold-postgres@test.npbb",
            password_hash=hash_password("senha123"),
            tipo_usuario="npbb",
            ativo=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        batch1 = LeadBatch(
            enviado_por=int(user.id),
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="gold-1.csv",
            stage=BatchStage.SILVER,
            evento_id=int(evento.id),
            origem_lote="proponente",
        )
        session.add(batch1)
        session.commit()
        session.refresh(batch1)

        csv1 = tmp_path / "gold-1.csv"
        csv1.write_text(
            "nome,cpf,email,telefone,evento,sessao\n"
            "Alice,52998224725,alice@ex.com,11999990000,Evento Dedupe Postgres,Sao Paulo-SP\n",
            encoding="utf-8",
        )
        created = _inserir_leads_gold(batch1, csv1, session)
        session.commit()
        assert created == 1

        lead = session.exec(select(Lead).where(Lead.email == "alice@ex.com")).one()
        first_lead_id = int(lead.id)

        evento.nome = "Evento Dedupe Postgres Renomeado"
        session.add(evento)
        session.commit()

        batch2 = LeadBatch(
            enviado_por=int(user.id),
            plataforma_origem="email",
            data_envio=datetime.now(timezone.utc),
            nome_arquivo_original="gold-2.csv",
            stage=BatchStage.SILVER,
            evento_id=int(evento.id),
            origem_lote="proponente",
        )
        session.add(batch2)
        session.commit()
        session.refresh(batch2)

        csv2 = tmp_path / "gold-2.csv"
        csv2.write_text(
            "nome,cpf,email,telefone,evento,sessao\n"
            "Alice Corrigida,52998224725,alice@ex.com,11999990000,Evento Dedupe Postgres Renomeado,Sao Paulo-SP\n",
            encoding="utf-8",
        )
        created_again = _inserir_leads_gold(batch2, csv2, session)
        session.commit()
        assert created_again == 0

        leads = session.exec(select(Lead).where(Lead.email == "alice@ex.com")).all()
        assert len(leads) == 1
        assert int(leads[0].id) == first_lead_id

        lead_eventos = session.exec(
            select(LeadEvento)
            .where(LeadEvento.lead_id == first_lead_id)
            .where(LeadEvento.evento_id == int(evento.id))
        ).all()
        assert len(lead_eventos) == 1
