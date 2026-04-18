"""Helpers para garantir a ativacao obrigatoria BB por evento."""

from __future__ import annotations

from decimal import Decimal

from fastapi import status
from sqlmodel import Session, select

from app.models.models import Ativacao, now_utc
from app.services.landing_pages import hydrate_ativacao_public_urls
from app.utils.http_errors import raise_http_error


BB_ACTIVATION_NAME = "BB"
ATIVACAO_BB_ALREADY_EXISTS = "ATIVACAO_BB_ALREADY_EXISTS"
ATIVACAO_BB_REQUIRED = "ATIVACAO_BB_REQUIRED"


def normalize_activation_name(value: str | None) -> str:
    return (value or "").strip()


def is_bb_activation_name(value: str | None) -> bool:
    return normalize_activation_name(value).upper() == BB_ACTIVATION_NAME


def canonicalize_activation_name(value: str | None) -> str | None:
    normalized = normalize_activation_name(value)
    if not normalized:
        return None
    if is_bb_activation_name(normalized):
        return BB_ACTIVATION_NAME
    return normalized


def get_bb_activation(session: Session, *, evento_id: int) -> Ativacao | None:
    ativacoes = session.exec(
        select(Ativacao).where(Ativacao.evento_id == evento_id).order_by(Ativacao.id)
    ).all()
    for ativacao in ativacoes:
        if is_bb_activation_name(ativacao.nome):
            return ativacao
    return None


def ensure_bb_activation(session: Session, *, evento_id: int) -> Ativacao:
    ativacao = get_bb_activation(session, evento_id=evento_id)
    if ativacao is None:
        ativacao = Ativacao(
            evento_id=evento_id,
            nome=BB_ACTIVATION_NAME,
            descricao=None,
            gamificacao_id=None,
            landing_url=None,
            qr_code_url=None,
            url_promotor=None,
            valor=Decimal("0.00"),
            mensagem_qrcode=None,
            redireciona_pesquisa=False,
            checkin_unico=False,
            termo_uso=False,
            gera_cupom=False,
        )
        session.add(ativacao)
        session.flush()

    canonical_name = canonicalize_activation_name(ativacao.nome)
    if canonical_name is not None and ativacao.nome != canonical_name:
        ativacao.nome = canonical_name
        session.add(ativacao)

    if hydrate_ativacao_public_urls(ativacao):
        ativacao.updated_at = now_utc()
        session.add(ativacao)

    return ativacao


def guard_bb_invariant_on_activation_write(
    session: Session,
    *,
    evento_id: int,
    nome: str | None = None,
    ativacao_id: int | None = None,
    deleting: bool = False,
) -> str | None:
    bb_activation = get_bb_activation(session, evento_id=evento_id)

    if deleting:
        if bb_activation is not None and bb_activation.id == ativacao_id:
            raise_http_error(
                status.HTTP_409_CONFLICT,
                code=ATIVACAO_BB_REQUIRED,
                message="A ativacao obrigatoria BB nao pode ser excluida.",
            )
        return None

    canonical_name = canonicalize_activation_name(nome)
    if canonical_name is None:
        return None

    if canonical_name != BB_ACTIVATION_NAME:
        if bb_activation is not None and bb_activation.id == ativacao_id:
            raise_http_error(
                status.HTTP_409_CONFLICT,
                code=ATIVACAO_BB_REQUIRED,
                message="A ativacao obrigatoria BB nao pode ser renomeada.",
                field="nome",
            )
        return canonical_name

    if bb_activation is not None and bb_activation.id != ativacao_id:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code=ATIVACAO_BB_ALREADY_EXISTS,
            message="O evento ja possui a ativacao obrigatoria BB.",
            field="nome",
        )
    return BB_ACTIVATION_NAME
