from __future__ import annotations

import asyncio
from datetime import date
from io import BytesIO

import pytest
from openpyxl import Workbook
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.models import Evento, Lead, StatusEvento
from app.modules.leads_publicidade.application.leads_import_etl_usecases import (
    commit_leads_with_etl,
    import_leads_with_etl,
)
from fastapi import UploadFile


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _seed_statuses(session: Session) -> None:
    for nome in ["Previsto", "A Confirmar", "Confirmado", "Realizado", "Cancelado"]:
        session.add(StatusEvento(nome=nome))
    session.commit()


def _create_event(session: Session, nome: str = "Evento ETL") -> Evento:
    _seed_statuses(session)
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Previsto")).first()
    evento = Evento(
        nome=nome,
        cidade="Brasilia",
        estado="DF",
        concorrencia=False,
        data_inicio_prevista=date(2099, 1, 1),
        status_id=int(status.id),
    )
    session.add(evento)
    session.commit()
    session.refresh(evento)
    return evento


def _make_upload_file(rows: list[list[object]], *, filename: str = "etl.xlsx") -> UploadFile:
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return UploadFile(filename=filename, file=output)


@pytest.fixture
def engine():
    engine = make_engine()
    SQLModel.metadata.create_all(engine)
    return engine


def test_import_leads_with_etl_preview_and_commit_idempotent(engine) -> None:
    with Session(engine) as session:
        evento = _create_event(session)
        file = _make_upload_file(
            [
                ["Email", "CPF", "Nome", "Sessao"],
                ["etl@example.com", "12345678901", "Lead ETL", "Show 1"],
                ["etl@example.com", "12345678901", "Lead ETL Atualizado", "Show 1"],
            ]
        )

        preview = asyncio.run(import_leads_with_etl(file=file, evento_id=int(evento.id), db=session, strict=False))

        assert preview.total_rows == 2
        assert preview.valid_rows == 2
        assert preview.invalid_rows == 0
        assert preview.session_token
        assert any(item.check_name == "dq.preview.duplicates" for item in preview.dq_report)

        commit = asyncio.run(
            commit_leads_with_etl(
                session_token=preview.session_token,
                evento_id=int(evento.id),
                db=session,
                strict=False,
                force_warnings=True,
            )
        )
        replay = asyncio.run(
            commit_leads_with_etl(
                session_token=preview.session_token,
                evento_id=int(evento.id),
                db=session,
                strict=False,
                force_warnings=True,
            )
        )

        assert commit.created + commit.updated >= 1
        assert replay.created == commit.created
        assert replay.updated == commit.updated

        leads = session.exec(select(Lead)).all()
        assert len(leads) == 1
        assert leads[0].nome == "Lead ETL Atualizado"
        assert leads[0].evento_nome == "Evento ETL"


def test_import_leads_with_etl_strict_blocks_invalid_rows(engine) -> None:
    with Session(engine) as session:
        evento = _create_event(session, nome="Evento Strict")
        file = _make_upload_file(
            [
                ["Email", "CPF", "Nome Completo", "Sessao"],
                ["strict@example.com", "12345678901", "Lead Invalido", "Show 1"],
            ]
        )

        preview = asyncio.run(import_leads_with_etl(file=file, evento_id=int(evento.id), db=session, strict=True))

        assert preview.valid_rows == 0
        assert preview.invalid_rows == 1
        assert preview.has_validation_errors is True

        with pytest.raises(Exception, match="strict=true bloqueia commit"):
            asyncio.run(
                commit_leads_with_etl(
                    session_token=preview.session_token,
                    evento_id=int(evento.id),
                    db=session,
                    strict=True,
                    force_warnings=True,
                )
            )

        leads = session.exec(select(Lead)).all()
        assert leads == []


def test_import_leads_with_etl_non_strict_persists_only_approved_rows(engine) -> None:
    with Session(engine) as session:
        evento = _create_event(session, nome="Evento Non Strict")
        file = _make_upload_file(
            [
                ["Email", "CPF", "Nome Completo", "Sessao"],
                ["valid@example.com", "12345678901", "Lead Invalido", "Show 1"],
            ]
        )

        preview = asyncio.run(import_leads_with_etl(file=file, evento_id=int(evento.id), db=session, strict=False))

        assert preview.valid_rows == 0
        assert preview.invalid_rows == 1
        assert preview.has_validation_errors is True

        result = asyncio.run(
            commit_leads_with_etl(
                session_token=preview.session_token,
                evento_id=int(evento.id),
                db=session,
                strict=False,
                force_warnings=True,
            )
        )

        assert result.status == "committed"
        assert result.created + result.updated == 0

        leads = session.exec(select(Lead)).all()
        assert leads == []
