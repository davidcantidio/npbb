"""
Seed compartilhado para a suíte Playwright canônica.

Objetivo:
- preparar schema completo no SQLite efêmero usado pelo backend E2E;
- criar dados-base para os smokes protegidos (auth, eventos, leads e ETL);
- manter as fixtures públicas da F3 usadas pelos testes de landing;
- gravar fixture determinística para E2E em
  `artifacts/phase-f3/evidence/issue-f3-01-003-fixtures.json`.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
EVIDENCE_DIR = PROJECT_ROOT / "artifacts" / "phase-f3" / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "issue-f3-01-003-fixtures.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select

import app.models.etl_registry  # noqa: F401
import app.models.models  # noqa: F401
from app.db.metadata import SQLModel
from app.models.etl_registry import IngestionRun as CatalogIngestionRun
from app.models.etl_registry import IngestionStatus, Source as CatalogSource, SourceKind
from app.models.models import (
    Ativacao,
    AtivacaoLead,
    Diretoria,
    Evento,
    Gamificacao,
    Lead,
    StatusEvento,
    Usuario,
    UsuarioTipo,
)
from app.services.default_event_activation import ensure_bb_activation
from app.utils.security import hash_password, verify_password


TEMPLATE_ROWS = (
    {
        "template_key": "corporativo",
        "evento_nome": "Evento Playwright F3 - corporativo",
        "evento_descricao": "Evento de QA F3 para template corporativo com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - corporativo",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "esporte_convencional",
        "evento_nome": "Evento Playwright F3 - esporte_convencional",
        "evento_descricao": "Evento de QA F3 para template esporte_convencional com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - esporte_convencional",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "esporte_radical",
        "evento_nome": "Evento Playwright F3 - esporte_radical",
        "evento_descricao": "Evento de QA F3 para template esporte_radical com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - esporte_radical",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "evento_cultural",
        "evento_nome": "Evento Playwright F3 - evento_cultural",
        "evento_descricao": "Evento de QA F3 para template evento_cultural com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - evento_cultural",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "show_musical",
        "evento_nome": "Evento Playwright F3 - show_musical",
        "evento_descricao": "Evento de QA F3 para template show_musical com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - show_musical",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "tecnologia",
        "evento_nome": "Evento Playwright F3 - tecnologia",
        "evento_descricao": "Evento de QA F3 para template tecnologia com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - tecnologia",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
    {
        "template_key": "generico",
        "evento_nome": "Evento Playwright F3 - generico",
        "evento_descricao": "Evento de QA F3 para template generico com gamificacao.",
        "ativacao_nome": "Ativacao Playwright F3 - generico",
        "ativacao_descricao": "Gamificacao aplicada para validar fluxo PUBLICO/landing.",
    },
)


PLAYWRIGHT_START_DATE = date(2026, 4, 10)
PLAYWRIGHT_EVENT_NAME = "Evento Playwright NPBB"
PLAYWRIGHT_LEAD_EMAIL = "lead.playwright@npbb.com.br"
SEEDED_USER_EMAIL = "david.cantidio@npbb.com.br"
SEEDED_USER_PASSWORD = "Senha123!"
PLAYWRIGHT_ETL_SOURCE_ID = "SRC_PLAYWRIGHT"
PLAYWRIGHT_TIMESTAMP = datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc)


def _load_env() -> None:
    candidate_paths = [
        BASE_DIR / ".env",
        PROJECT_ROOT / ".env",
    ]
    for candidate in candidate_paths:
        if candidate.exists():
            load_dotenv(candidate)
            return
    load_dotenv()


def _build_engine():
    _load_env()
    database_url = (os.getenv("DATABASE_URL") or "").strip()
    direct_url = (os.getenv("DIRECT_URL") or "").strip()
    if not database_url and direct_url:
        database_url = direct_url
    if not database_url:
        raise RuntimeError("DATABASE_URL/DIRECT_URL nao configurado.")

    connect_args: dict[str, bool | str] = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    return create_engine(database_url, echo=echo, connect_args=connect_args)


def _normalize_template_key(value: str | None) -> str | None:
    if value is None:
        return None
    template = value.strip().lower()
    return template or None


def _query_evento(session: Session, *, nome: str, template_override: str | None) -> Evento | None:
    query = select(Evento).where(Evento.nome == nome)
    if template_override is None:
        query = query.where(Evento.template_override.is_(None))
    else:
        query = query.where(Evento.template_override == template_override)
    return session.exec(query).first()


def ensure_status(session: Session, nome: str) -> StatusEvento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == nome)).first()
    if status:
        return status

    status = StatusEvento(nome=nome)
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def ensure_diretoria(session: Session, nome: str) -> Diretoria:
    diretoria = session.exec(select(Diretoria).where(Diretoria.nome == nome)).first()
    if diretoria:
        return diretoria

    diretoria = Diretoria(nome=nome)
    session.add(diretoria)
    session.commit()
    session.refresh(diretoria)
    return diretoria


def ensure_user(session: Session, *, email: str, password: str) -> Usuario:
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if usuario is None:
        usuario = Usuario(
            email=email,
            password_hash=hash_password(password),
            tipo_usuario=UsuarioTipo.NPBB,
            ativo=True,
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

    changed = False
    if usuario.tipo_usuario != UsuarioTipo.NPBB:
        usuario.tipo_usuario = UsuarioTipo.NPBB
        changed = True
    if not usuario.ativo:
        usuario.ativo = True
        changed = True
    if not verify_password(password, usuario.password_hash):
        usuario.password_hash = hash_password(password)
        changed = True

    if changed:
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
    return usuario


def ensure_evento(
    session: Session,
    *,
    nome: str,
    status_id: int,
    template_override: str | None,
    descricao: str,
    diretoria_id: int | None = None,
    cidade: str = "Brasilia",
    estado: str = "DF",
) -> Evento:
    evento = _query_evento(session, nome=nome, template_override=template_override)
    normalized_template = _normalize_template_key(template_override)
    changed = False
    if evento is None:
        evento = Evento(
            nome=nome,
            descricao=descricao,
            descricao_curta=descricao,
            template_override=normalized_template,
            status_id=status_id,
            diretoria_id=diretoria_id,
            cidade=cidade,
            estado=estado,
            data_inicio_prevista=PLAYWRIGHT_START_DATE,
            data_fim_prevista=PLAYWRIGHT_START_DATE,
            data_inicio_realizada=PLAYWRIGHT_START_DATE,
            data_fim_realizada=PLAYWRIGHT_START_DATE,
        )
        session.add(evento)
        session.commit()
        ensure_bb_activation(session, evento_id=evento.id)
        session.commit()
        session.refresh(evento)
        return evento

    if evento.status_id != status_id:
        evento.status_id = status_id
        changed = True
    if evento.template_override != normalized_template:
        evento.template_override = normalized_template
        changed = True
    if evento.diretoria_id != diretoria_id:
        evento.diretoria_id = diretoria_id
        changed = True
    if evento.descricao != descricao:
        evento.descricao = descricao
        changed = True
    if evento.descricao_curta != descricao:
        evento.descricao_curta = descricao
        changed = True
    if evento.cidade != cidade:
        evento.cidade = cidade
        changed = True
    if evento.estado != estado:
        evento.estado = estado
        changed = True

    if changed:
        session.add(evento)
        session.commit()
        session.refresh(evento)
    ensure_bb_activation(session, evento_id=evento.id)
    session.commit()
    session.refresh(evento)
    return evento


def ensure_gamificacao(
    session: Session,
    *,
    evento_id: int,
    template_key: str,
) -> Gamificacao:
    nome = f"Gamificacao Playwright F3 - {template_key}"
    gam = session.exec(
        select(Gamificacao)
        .where(Gamificacao.evento_id == evento_id)
        .where(Gamificacao.nome == nome)
    ).first()
    description = (
        f"Gamificacao do template {template_key} para validacao de fluxo de "
        "apresentacao, acao e conclusao no formato landing public."
    )
    if gam is None:
        gam = Gamificacao(
            evento_id=evento_id,
            nome=nome,
            descricao=description,
            premio="Brinde de validacao BB",
            titulo_feedback="Parabens!",
            texto_feedback="Gamificacao concluida com sucesso.",
        )
        session.add(gam)
        session.commit()
        session.refresh(gam)
        return gam

    changed = False
    if gam.descricao != description:
        gam.descricao = description
        changed = True
    if gam.premio != "Brinde de validacao BB":
        gam.premio = "Brinde de validacao BB"
        changed = True
    if gam.titulo_feedback != "Parabens!":
        gam.titulo_feedback = "Parabens!"
        changed = True
    if gam.texto_feedback != "Gamificacao concluida com sucesso.":
        gam.texto_feedback = "Gamificacao concluida com sucesso."
        changed = True

    if changed:
        session.add(gam)
        session.commit()
        session.refresh(gam)
    return gam


def ensure_ativacao(
    session: Session,
    *,
    evento_id: int,
    nome: str,
    descricao: str,
    gamificacao_id: int | None = None,
) -> Ativacao:
    ativacao = session.exec(
        select(Ativacao).where(Ativacao.evento_id == evento_id).where(Ativacao.nome == nome)
    ).first()
    if ativacao is None:
        ativacao = Ativacao(
            evento_id=evento_id,
            nome=nome,
            descricao=descricao,
            mensagem_qrcode="Participe para validar a fase de gamificacao.",
            gamificacao_id=gamificacao_id,
            valor=0,
        )
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
        return ativacao

    changed = False
    if ativacao.gamificacao_id != gamificacao_id:
        ativacao.gamificacao_id = gamificacao_id
        changed = True
    if ativacao.descricao != descricao:
        ativacao.descricao = descricao
        changed = True
    if ativacao.mensagem_qrcode != "Participe para validar a fase de gamificacao.":
        ativacao.mensagem_qrcode = "Participe para validar a fase de gamificacao."
        changed = True

    if changed:
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
    return ativacao


def ensure_lead(
    session: Session,
    *,
    nome: str,
    sobrenome: str,
    email: str,
    cpf: str,
    evento_nome: str,
) -> Lead:
    lead = session.exec(select(Lead).where(Lead.email == email)).first()
    if lead is None:
        lead = Lead(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            cpf=cpf,
            evento_nome=evento_nome,
            cidade="Brasilia",
            estado="DF",
            fonte_origem="playwright_smoke_seed",
            data_criacao=PLAYWRIGHT_TIMESTAMP,
        )
        session.add(lead)
        session.commit()
        session.refresh(lead)
        return lead

    changed = False
    if lead.nome != nome:
        lead.nome = nome
        changed = True
    if lead.sobrenome != sobrenome:
        lead.sobrenome = sobrenome
        changed = True
    if lead.cpf != cpf:
        lead.cpf = cpf
        changed = True
    if lead.evento_nome != evento_nome:
        lead.evento_nome = evento_nome
        changed = True
    if lead.cidade != "Brasilia":
        lead.cidade = "Brasilia"
        changed = True
    if lead.estado != "DF":
        lead.estado = "DF"
        changed = True
    if lead.fonte_origem != "playwright_smoke_seed":
        lead.fonte_origem = "playwright_smoke_seed"
        changed = True
    if lead.data_criacao != PLAYWRIGHT_TIMESTAMP:
        lead.data_criacao = PLAYWRIGHT_TIMESTAMP
        changed = True

    if changed:
        session.add(lead)
        session.commit()
        session.refresh(lead)
    return lead


def ensure_ativacao_lead(session: Session, *, ativacao_id: int, lead_id: int) -> AtivacaoLead:
    link = session.exec(
        select(AtivacaoLead)
        .where(AtivacaoLead.ativacao_id == ativacao_id)
        .where(AtivacaoLead.lead_id == lead_id)
    ).first()
    if link:
        return link

    link = AtivacaoLead(ativacao_id=ativacao_id, lead_id=lead_id)
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def ensure_etl_fixture(session: Session) -> CatalogSource:
    source = session.exec(
        select(CatalogSource).where(CatalogSource.source_id == PLAYWRIGHT_ETL_SOURCE_ID)
    ).first()
    if source is None:
        source = CatalogSource(
            source_id=PLAYWRIGHT_ETL_SOURCE_ID,
            kind=SourceKind.CSV,
            uri="seed://playwright/smoke.csv",
            display_name="Playwright Smoke Seed",
            is_active=True,
        )
        session.add(source)
        session.commit()
        session.refresh(source)
    else:
        changed = False
        if source.kind != SourceKind.CSV:
            source.kind = SourceKind.CSV
            changed = True
        if source.uri != "seed://playwright/smoke.csv":
            source.uri = "seed://playwright/smoke.csv"
            changed = True
        if source.display_name != "Playwright Smoke Seed":
            source.display_name = "Playwright Smoke Seed"
            changed = True
        if not source.is_active:
            source.is_active = True
            changed = True
        if changed:
            session.add(source)
            session.commit()
            session.refresh(source)

    if source.id is None:
        raise RuntimeError("Falha ao persistir fonte ETL compartilhada do Playwright.")

    run = session.exec(
        select(CatalogIngestionRun)
        .where(CatalogIngestionRun.source_pk == source.id)
        .order_by(CatalogIngestionRun.id.desc())
    ).first()
    if run is None:
        run = CatalogIngestionRun(
            source_pk=source.id,
            extractor_name="playwright_smoke_seed",
            status=IngestionStatus.SUCCESS,
            started_at=PLAYWRIGHT_TIMESTAMP,
            finished_at=PLAYWRIGHT_TIMESTAMP,
            records_read=1,
            records_loaded=1,
            notes="Seed fixture for Playwright canonical smoke suite.",
            created_at=PLAYWRIGHT_TIMESTAMP,
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        return source

    changed = False
    if run.extractor_name != "playwright_smoke_seed":
        run.extractor_name = "playwright_smoke_seed"
        changed = True
    if run.status != IngestionStatus.SUCCESS:
        run.status = IngestionStatus.SUCCESS
        changed = True
    if run.started_at != PLAYWRIGHT_TIMESTAMP:
        run.started_at = PLAYWRIGHT_TIMESTAMP
        changed = True
    if run.finished_at != PLAYWRIGHT_TIMESTAMP:
        run.finished_at = PLAYWRIGHT_TIMESTAMP
        changed = True
    if run.records_read != 1:
        run.records_read = 1
        changed = True
    if run.records_loaded != 1:
        run.records_loaded = 1
        changed = True
    if run.notes != "Seed fixture for Playwright canonical smoke suite.":
        run.notes = "Seed fixture for Playwright canonical smoke suite."
        changed = True
    if run.created_at != PLAYWRIGHT_TIMESTAMP:
        run.created_at = PLAYWRIGHT_TIMESTAMP
        changed = True

    if changed:
        session.add(run)
        session.commit()
        session.refresh(run)
    return source


def write_fixtures(data: list[dict[str, object]]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "fixtures": data,
        "issue_id": "ISSUE-F3-01-003",
        "total": len(data),
    }
    EVIDENCE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    engine = _build_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        status_confirmado = ensure_status(session, "Confirmado")
        status_planejado = ensure_status(session, "Planejado")
        diretoria_dipes = ensure_diretoria(session, "DIPES")
        ensure_user(
            session,
            email=SEEDED_USER_EMAIL,
            password=SEEDED_USER_PASSWORD,
        )
        ensure_etl_fixture(session)

        if not status_confirmado.id or not status_planejado.id:
            raise RuntimeError("Status compartilhados do Playwright nao conseguiram ser criados.")
        if not diretoria_dipes.id:
            raise RuntimeError("Diretoria compartilhada do Playwright nao conseguiu ser criada.")

        evento_protegido = ensure_evento(
            session,
            nome=PLAYWRIGHT_EVENT_NAME,
            status_id=status_confirmado.id,
            template_override=None,
            descricao="Evento de QA protegido para validar navegacao autenticada e listagem.",
            diretoria_id=diretoria_dipes.id,
            cidade="Brasilia",
            estado="DF",
        )
        if not evento_protegido.id:
            raise RuntimeError("Falha ao persistir evento compartilhado do Playwright.")

        ativacao_protegida = ensure_ativacao(
            session,
            evento_id=evento_protegido.id,
            nome="Ativacao Playwright NPBB",
            descricao="Ativacao compartilhada para vinculo do lead seedado.",
        )
        if not ativacao_protegida.id:
            raise RuntimeError("Falha ao persistir ativacao compartilhada do Playwright.")

        lead_protegido = ensure_lead(
            session,
            nome="Lead",
            sobrenome="Playwright",
            email=PLAYWRIGHT_LEAD_EMAIL,
            cpf="12345678909",
            evento_nome=PLAYWRIGHT_EVENT_NAME,
        )
        if not lead_protegido.id:
            raise RuntimeError("Falha ao persistir lead compartilhado do Playwright.")

        ensure_ativacao_lead(
            session,
            ativacao_id=ativacao_protegida.id,
            lead_id=lead_protegido.id,
        )

        ensure_evento(
            session,
            nome="Evento Playwright NPBB - base",
            status_id=status_confirmado.id,
            template_override=None,
            descricao="Landing base para regressao visual e QA de tema F3.",
        )

        fixtures: list[dict[str, object]] = []
        for row in TEMPLATE_ROWS:
            template_key = row["template_key"]
            evento = ensure_evento(
                session,
                nome=row["evento_nome"],
                status_id=status_confirmado.id,
                template_override=template_key,
                descricao=row["evento_descricao"],
            )
            if not evento.id:
                raise RuntimeError(f"Falha ao persistir evento {row['evento_nome']}.")

            gamificacao = ensure_gamificacao(session, evento_id=evento.id, template_key=template_key)
            if not gamificacao.id:
                raise RuntimeError(f"Falha ao persistir gamificacao para {row['evento_nome']}.")

            ativacao = ensure_ativacao(
                session,
                evento_id=evento.id,
                nome=row["ativacao_nome"],
                descricao=row["ativacao_descricao"],
                gamificacao_id=gamificacao.id,
            )
            if not ativacao.id:
                raise RuntimeError(f"Falha ao persistir ativacao para {row['evento_nome']}.")

            fixtures.append(
                {
                    "template_key": template_key,
                    "template_category": template_key,
                    "evento_id": evento.id,
                    "evento_nome": evento.nome,
                    "ativacao_id": ativacao.id,
                    "ativacao_nome": ativacao.nome,
                    "gamificacao_id": gamificacao.id,
                }
            )

        write_fixtures(fixtures)
        print(f"Fixtures de QA F3 gravadas em: {EVIDENCE_FILE}")
        print(f"Seed concluido. Fixtures criadas: {len(fixtures)}.")


if __name__ == "__main__":
    main()
