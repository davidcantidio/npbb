"""
Seed de dados para execução de smoke/end-to-end do F3 (playwright cross-template).

Objetivo:
- criar evento base de landing público para referência de issue 001;
- criar 7 eventos dedicados com template_override dos templates F3;
- criar uma gamificação e uma ativação para cada um desses 7 eventos;
- gravar fixture determinística para E2E (eventos/ativacoes por template) em
  `artifacts/phase-f3/evidence/issue-f3-01-003-fixtures.json`.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select

from app.models.models import Ativacao, Evento, Gamificacao, StatusEvento

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
EVIDENCE_DIR = PROJECT_ROOT / "artifacts" / "phase-f3" / "evidence"
EVIDENCE_FILE = EVIDENCE_DIR / "issue-f3-01-003-fixtures.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


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
    database_url = os.getenv("DATABASE_URL")
    direct_url = os.getenv("DIRECT_URL")
    if direct_url and direct_url.strip():
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


def ensure_status(session: Session) -> StatusEvento:
    status = session.exec(select(StatusEvento).where(StatusEvento.nome == "Confirmado")).first()
    if status:
        return status

    status = StatusEvento(nome="Confirmado")
    session.add(status)
    session.commit()
    session.refresh(status)
    return status


def ensure_evento(
    session: Session,
    *,
    nome: str,
    status_id: int,
    template_override: str | None,
    descricao: str,
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
            cidade="Brasilia",
            estado="DF",
            data_inicio_prevista=PLAYWRIGHT_START_DATE,
            data_fim_prevista=PLAYWRIGHT_START_DATE,
            data_inicio_realizada=PLAYWRIGHT_START_DATE,
            data_fim_realizada=PLAYWRIGHT_START_DATE,
        )
        session.add(evento)
        session.commit()
        session.refresh(evento)
        return evento

    if evento.status_id != status_id:
        evento.status_id = status_id
        changed = True
    if evento.template_override != normalized_template:
        evento.template_override = normalized_template
        changed = True
    if evento.descricao != descricao:
        evento.descricao = descricao
        changed = True
    if evento.descricao_curta != descricao:
        evento.descricao_curta = descricao
        changed = True
    if evento.cidade != "Brasilia":
        evento.cidade = "Brasilia"
        changed = True
    if evento.estado != "DF":
        evento.estado = "DF"
        changed = True

    if changed:
        session.add(evento)
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
    gamificacao_id: int,
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
    with Session(engine) as session:
        status = ensure_status(session)
        if not status.id:
            raise RuntimeError("Status Confirmado nao conseguiu ser criado.")

        ensure_evento(
            session,
            nome="Evento Playwright NPBB - base",
            status_id=status.id,
            template_override=None,
            descricao="Landing base para regressao visual e QA de tema F3.",
        )

        fixtures: list[dict[str, object]] = []
        for row in TEMPLATE_ROWS:
            template_key = row["template_key"]
            evento = ensure_evento(
                session,
                nome=row["evento_nome"],
                status_id=status.id,
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
