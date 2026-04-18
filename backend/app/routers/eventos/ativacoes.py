"""Rotas de ativações por evento."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Ativacao, Gamificacao, Usuario, now_utc
from app.schemas.ativacao import AtivacaoCreate, AtivacaoRead
from app.services.default_event_activation import guard_bb_invariant_on_activation_write
from app.services.evento_activation_import import (
    ACTIVATION_IMPORT_REQUIRES_AGENCY_CODE,
    get_activation_import_block_reason,
)
from app.services.landing_pages import (
    build_ativacao_public_access_urls,
    hydrate_ativacao_public_urls,
)

from . import _shared

router = APIRouter()


@router.get("/{evento_id}/ativacoes", response_model=list[AtivacaoRead])
@router.get("/{evento_id}/ativacoes/", response_model=list[AtivacaoRead])
def listar_ativacoes(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    ativacoes = session.exec(
        select(Ativacao).where(Ativacao.evento_id == evento_id).order_by(Ativacao.id)
    ).all()
    items: list[AtivacaoRead] = []
    for ativacao in ativacoes:
        public_urls = build_ativacao_public_access_urls(ativacao.id or 0)
        items.append(
            AtivacaoRead.model_validate(ativacao, from_attributes=True).model_copy(
                update={
                    "landing_url": public_urls["landing_url"],
                    "qr_code_url": public_urls["qr_code_url"],
                    "url_promotor": public_urls["url_promotor"],
                }
            )
        )
    return items


@router.post(
    "/{evento_id}/ativacoes",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{evento_id}/ativacoes/",
    response_model=AtivacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_ativacao(
    evento_id: int,
    payload: AtivacaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = _shared._check_evento_visible_or_404(session, evento_id, current_user)
    block_reason = get_activation_import_block_reason(evento)
    if block_reason is not None:
        _shared._raise_http(
            status.HTTP_400_BAD_REQUEST,
            code=ACTIVATION_IMPORT_REQUIRES_AGENCY_CODE,
            message=block_reason,
            extra={"field": "evento_id"},
        )

    if payload.gamificacao_id is not None:
        gamificacao = session.get(Gamificacao, payload.gamificacao_id)
        if not gamificacao or gamificacao.evento_id != evento_id:
            _shared._raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="GAMIFICACAO_OUT_OF_SCOPE",
                message="Gamificacao invalida para este evento",
                extra={"field": "gamificacao_id"},
            )
    nome = guard_bb_invariant_on_activation_write(
        session,
        evento_id=evento_id,
        nome=payload.nome,
    )

    ativacao = Ativacao(
        evento_id=evento_id,
        nome=nome or payload.nome,
        descricao=payload.descricao,
        mensagem_qrcode=payload.mensagem_qrcode,
        gamificacao_id=payload.gamificacao_id,
        redireciona_pesquisa=payload.redireciona_pesquisa,
        checkin_unico=payload.checkin_unico,
        termo_uso=payload.termo_uso,
        gera_cupom=payload.gera_cupom,
        valor=Decimal("0.00"),
    )
    session.add(ativacao)
    session.commit()

    session.refresh(ativacao)
    if hydrate_ativacao_public_urls(ativacao):
        ativacao.updated_at = now_utc()
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)
    return AtivacaoRead.model_validate(ativacao, from_attributes=True)
