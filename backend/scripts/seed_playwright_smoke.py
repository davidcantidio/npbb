from __future__ import annotations

from datetime import date, datetime, timezone

import app.main  # noqa: F401
from sqlmodel import Session, select

from app.db.database import engine
from app.db.metadata import SQLModel
from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind
from app.models.models import Diretoria, Evento, Lead, StatusEvento, Usuario, UsuarioTipo
from app.utils.security import hash_password

SEEDED_USER_EMAIL = "david.cantidio@npbb.com.br"
SEEDED_USER_PASSWORD = "Senha123!"
SEEDED_EVENT_NAME = "Evento Playwright NPBB"
SEEDED_LEAD_EMAIL = "lead.playwright@npbb.com.br"
SEEDED_SOURCE_ID = "SRC_PLAYWRIGHT"


def _first(model, *conditions):
    statement = select(model)
    for condition in conditions:
        statement = statement.where(condition)
    return statement


def seed_user(session: Session) -> Usuario:
    user = session.exec(_first(Usuario, Usuario.email == SEEDED_USER_EMAIL)).first()
    password_hash = hash_password(SEEDED_USER_PASSWORD)
    if user is None:
        user = Usuario(
            email=SEEDED_USER_EMAIL,
            password_hash=password_hash,
            tipo_usuario=UsuarioTipo.NPBB,
            ativo=True,
        )
    else:
        user.password_hash = password_hash
        user.tipo_usuario = UsuarioTipo.NPBB
        user.ativo = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_event_domain(session: Session) -> tuple[Diretoria, StatusEvento, Evento]:
    diretoria = session.exec(_first(Diretoria, Diretoria.nome == "DIPES")).first()
    if diretoria is None:
        diretoria = Diretoria(nome="DIPES")
        session.add(diretoria)
        session.commit()
        session.refresh(diretoria)

    status = session.exec(_first(StatusEvento, StatusEvento.nome == "Planejado")).first()
    if status is None:
        status = StatusEvento(nome="Planejado")
        session.add(status)
        session.commit()
        session.refresh(status)

    evento = session.exec(_first(Evento, Evento.nome == SEEDED_EVENT_NAME)).first()
    if evento is None:
        evento = Evento(
            nome=SEEDED_EVENT_NAME,
            descricao="Seed E2E arquitetura",
            cidade="Sao Paulo",
            estado="SP",
            diretoria_id=diretoria.id,
            status_id=status.id,
            data_inicio_prevista=date(2026, 3, 10),
            data_fim_prevista=date(2026, 3, 12),
            concorrencia=False,
        )
    else:
        evento.descricao = "Seed E2E arquitetura"
        evento.cidade = "Sao Paulo"
        evento.estado = "SP"
        evento.diretoria_id = diretoria.id
        evento.status_id = status.id
        evento.data_inicio_prevista = date(2026, 3, 10)
        evento.data_fim_prevista = date(2026, 3, 12)
        evento.concorrencia = False
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return diretoria, status, evento


def seed_lead(session: Session) -> Lead:
    lead = session.exec(
        _first(
            Lead,
            Lead.email == SEEDED_LEAD_EMAIL,
            Lead.evento_nome == SEEDED_EVENT_NAME,
        )
    ).first()
    if lead is None:
        lead = Lead(
            nome="Lead Playwright",
            email=SEEDED_LEAD_EMAIL,
            cpf="12345678901",
            evento_nome=SEEDED_EVENT_NAME,
            sessao="sessao teste",
        )
    else:
        lead.nome = "Lead Playwright"
        lead.cpf = "12345678901"
        lead.evento_nome = SEEDED_EVENT_NAME
        lead.sessao = "sessao teste"
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


def seed_etl_registry(session: Session) -> tuple[Source, IngestionRun]:
    source = session.exec(_first(Source, Source.source_id == SEEDED_SOURCE_ID)).first()
    if source is None:
        source = Source(
            source_id=SEEDED_SOURCE_ID,
            kind=SourceKind.XLSX,
            uri="file:///tmp/playwright.xlsx",
            display_name="playwright.xlsx",
            is_active=True,
        )
    else:
        source.kind = SourceKind.XLSX
        source.uri = "file:///tmp/playwright.xlsx"
        source.display_name = "playwright.xlsx"
        source.is_active = True
    session.add(source)
    session.commit()
    session.refresh(source)

    ingestion = session.exec(
        _first(
            IngestionRun,
            IngestionRun.source_pk == source.id,
            IngestionRun.extractor_name == "playwright_seed",
        )
    ).first()
    started_at = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)
    finished_at = datetime(2026, 3, 2, 12, 5, tzinfo=timezone.utc)
    if ingestion is None:
        ingestion = IngestionRun(
            source_pk=source.id,
            status=IngestionStatus.SUCCESS,
            started_at=started_at,
            finished_at=finished_at,
            extractor_name="playwright_seed",
            notes="seeded for e2e smoke",
        )
    else:
        ingestion.status = IngestionStatus.SUCCESS
        ingestion.started_at = started_at
        ingestion.finished_at = finished_at
        ingestion.extractor_name = "playwright_seed"
        ingestion.notes = "seeded for e2e smoke"
    session.add(ingestion)
    session.commit()
    session.refresh(ingestion)
    return source, ingestion


def main() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = seed_user(session)
        _, _, evento = seed_event_domain(session)
        lead = seed_lead(session)
        source, ingestion = seed_etl_registry(session)
        print(
            "seed_playwright_smoke completed",
            {
                "user_id": user.id,
                "event_id": evento.id,
                "lead_id": lead.id,
                "source_id": source.source_id,
                "ingestion_id": ingestion.id,
            },
        )


if __name__ == "__main__":
    main()
