"""
Funcoes reutilizaveis de seed para desenvolvimento.

Objetivo: popular tabelas de dominio (lookup tables) de forma idempotente.

Observacao importante (Supabase):
- Para seeds/migrations, prefira `DIRECT_URL` (porta 5432) quando disponivel.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func
from sqlmodel import Session, create_engine, select

# Garante que o pacote app seja encontrado quando o script eh executado diretamente
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.models import (  # noqa: E402
    Agencia,
    Diretoria,
    DivisaoDemandante,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
)

DEFAULT_STATUS_EVENTO = [
    "Previsto",
    "A Confirmar",
    "Confirmado",
    "Realizado",
    "Cancelado",
]

DEFAULT_DIVISOES_DEMANDANTES = [
    "Esportes",
    "Agro",
    "Sustentabilidade/TI",
    "Cultura e Entretenimento",
]

DEFAULT_TIPOS_SUBTIPOS_EVENTO: dict[str, list[str]] = {
    "Esporte": [
        "Vôlei de quadra",
        "Vôlei de praia",
        "Corrida de rua",
        "Surfe",
        "Skate",
        "Canoagem",
    ],
    "Cultura": [
        "Feira",
        "Encontro",
        "Convenção",
        "Festival",
    ],
    "Entretenimento": [
        "Feira",
        "Festival",
        "Show musical",
        "Teatro",
    ],
    "Inovação": [
        "Feira",
        "Simpósio",
        "Congresso",
        "Encontro",
        "Hackathon",
        "Palestra",
    ],
}

DEFAULT_TERRITORIOS = [
    "Tecnologia",
    "Esporte",
    "Sustentabilidade (ASG)",
    "Agro",
]

# Tags sao dinamicas no formulario (usuario pode criar). Mantemos algumas basicas para testes.
DEFAULT_TAGS = [
    "Cultura",
    "Tecnologia",
    "Esporte",
    "Agro",
    "Sustentabilidade (ASG)",
]

DEFAULT_DIRETORIAS = [
    "audit",
    "bb_consorcios",
    "bb_previdencia",
    "bb_seguros",
    "cenop",
    "clients_mpe",
    "clinicassi",
    "coger",
    "crm",
    "dicoi",
    "dicor",
    "dicre",
    "diemp",
    "difin",
    "digov",
    "dimac",
    "dimep",
    "dined",
    "diope",
    "dipes",
    "direc",
    "direo",
    "diris",
    "disec",
    "ditec",
    "dijur",
    "divar",
    "gecor",
    "gecem",
    "gepes",
    "qvt",
    "reunioes",
    "secex",
    "super_adm",
    "uac",
    "uan",
    "uci",
    "ucf",
    "uni_corp_bank",
    "usi",
    "uri",
]

DEFAULT_AGENCIAS: list[tuple[str, int]] = [
    ("V3A", 1),
    ("Sherpa", 1),
    ("Monumenta", 2),
    ("Terrua", 2),
]


def load_env() -> None:
    load_dotenv(BASE_DIR / ".env")


def get_engine_for_scripts():
    """Cria engine preferindo DIRECT_URL (para migrations/seed) quando disponivel."""
    load_env()
    url = os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL/DIRECT_URL nao configurado no ambiente.")

    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    echo = os.getenv("SQL_ECHO", "false").lower() == "true"
    return create_engine(url, echo=echo, connect_args=connect_args)


def ensure_agencias(session: Session, entries: list[tuple[str, int]] | None = None) -> dict[str, Agencia]:
    result: dict[str, Agencia] = {}
    for nome, lote in entries or DEFAULT_AGENCIAS:
        agencia = session.exec(select(Agencia).where(func.lower(Agencia.nome) == nome.lower())).first()
        dominio_slug = "".join(nome.lower().split())
        dominio = f"{dominio_slug}.com.br"

        if not agencia:
            agencia = Agencia(nome=nome, dominio=dominio, lote=lote)
            session.add(agencia)
            session.commit()
            session.refresh(agencia)
        else:
            changed = False
            if agencia.nome != nome:
                agencia.nome = nome
                changed = True
            if not agencia.dominio or "." not in agencia.dominio:
                agencia.dominio = dominio
                changed = True
            if changed:
                session.add(agencia)
                session.commit()
                session.refresh(agencia)

        result[nome] = agencia

    return result


def ensure_diretorias(session: Session, nomes: list[str] | None = None) -> dict[str, Diretoria]:
    result: dict[str, Diretoria] = {}
    for nome in nomes or DEFAULT_DIRETORIAS:
        diretoria = session.exec(select(Diretoria).where(Diretoria.nome == nome)).first()
        if not diretoria:
            diretoria = Diretoria(nome=nome)
            session.add(diretoria)
            session.commit()
            session.refresh(diretoria)
        result[nome] = diretoria
    return result


def ensure_divisoes_demandantes(
    session: Session, nomes: list[str] | None = None
) -> dict[str, DivisaoDemandante]:
    result: dict[str, DivisaoDemandante] = {}
    for nome in nomes or DEFAULT_DIVISOES_DEMANDANTES:
        divisao = session.exec(
            select(DivisaoDemandante).where(func.lower(DivisaoDemandante.nome) == nome.lower())
        ).first()
        if not divisao:
            divisao = DivisaoDemandante(nome=nome)
            session.add(divisao)
            session.commit()
            session.refresh(divisao)
        elif divisao.nome != nome:
            divisao.nome = nome
            session.add(divisao)
            session.commit()
            session.refresh(divisao)
        result[nome] = divisao
    return result


def ensure_status_evento(session: Session, nomes: list[str] | None = None) -> dict[str, StatusEvento]:
    result: dict[str, StatusEvento] = {}
    for nome in nomes or DEFAULT_STATUS_EVENTO:
        status_obj = session.exec(
            select(StatusEvento).where(func.lower(StatusEvento.nome) == nome.lower())
        ).first()
        if not status_obj:
            status_obj = StatusEvento(nome=nome)
            session.add(status_obj)
            session.commit()
            session.refresh(status_obj)
        elif status_obj.nome != nome:
            status_obj.nome = nome
            session.add(status_obj)
            session.commit()
            session.refresh(status_obj)
        result[nome] = status_obj
    return result


def ensure_tipos_subtipos_evento(
    session: Session, mapping: dict[str, list[str]] | None = None
) -> dict[str, TipoEvento]:
    mapping = mapping or DEFAULT_TIPOS_SUBTIPOS_EVENTO

    tipos: dict[str, TipoEvento] = {}
    for tipo_nome in mapping.keys():
        tipo = session.exec(
            select(TipoEvento).where(func.lower(TipoEvento.nome) == tipo_nome.lower())
        ).first()
        if not tipo:
            tipo = TipoEvento(nome=tipo_nome)
            session.add(tipo)
            session.commit()
            session.refresh(tipo)
        elif tipo.nome != tipo_nome:
            tipo.nome = tipo_nome
            session.add(tipo)
            session.commit()
            session.refresh(tipo)
        tipos[tipo_nome] = tipo

    for tipo_nome, subtipos in mapping.items():
        tipo = tipos[tipo_nome]
        for subtipo_nome in subtipos:
            exists = session.exec(
                select(SubtipoEvento).where(
                    SubtipoEvento.tipo_id == tipo.id,
                    func.lower(SubtipoEvento.nome) == subtipo_nome.lower(),
                )
            ).first()
            if exists:
                if exists.nome != subtipo_nome:
                    exists.nome = subtipo_nome
                    session.add(exists)
                continue
            session.add(SubtipoEvento(tipo_id=tipo.id, nome=subtipo_nome))
        session.commit()

    return tipos


def ensure_territorios(session: Session, nomes: list[str] | None = None) -> dict[str, Territorio]:
    result: dict[str, Territorio] = {}
    for nome in nomes or DEFAULT_TERRITORIOS:
        territorio = session.exec(select(Territorio).where(func.lower(Territorio.nome) == nome.lower())).first()
        if not territorio:
            territorio = Territorio(nome=nome)
            session.add(territorio)
            session.commit()
            session.refresh(territorio)
        elif territorio.nome != nome:
            territorio.nome = nome
            session.add(territorio)
            session.commit()
            session.refresh(territorio)
        result[nome] = territorio
    return result


def ensure_tags(session: Session, nomes: list[str] | None = None) -> dict[str, Tag]:
    result: dict[str, Tag] = {}
    for nome in nomes or DEFAULT_TAGS:
        tag = session.exec(select(Tag).where(func.lower(Tag.nome) == nome.lower())).first()
        if not tag:
            tag = Tag(nome=nome)
            session.add(tag)
            session.commit()
            session.refresh(tag)
        elif tag.nome != nome:
            tag.nome = nome
            session.add(tag)
            session.commit()
            session.refresh(tag)
        result[nome] = tag
    return result

