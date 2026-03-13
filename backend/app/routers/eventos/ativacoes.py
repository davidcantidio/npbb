"""Rotas de ativações por evento."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Ativacao, Gamificacao, Usuario, now_utc
from app.schemas.ativacao import AtivacaoCreate, AtivacaoRead
from app.services.landing_pages import hydrate_ativacao_public_urls

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
    changed = False
    for ativacao in ativacoes:
        changed = hydrate_ativacao_public_urls(ativacao) or changed
    if changed:
        for ativacao in ativacoes:
            ativacao.updated_at = now_utc()
            session.add(ativacao)
        session.commit()
        for ativacao in ativacoes:
            session.refresh(ativacao)
    return [AtivacaoRead.model_validate(a, from_attributes=True) for a in ativacoes]


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
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    if payload.gamificacao_id is not None:
        gamificacao = session.get(Gamificacao, payload.gamificacao_id)
        if not gamificacao or gamificacao.evento_id != evento_id:
            _shared._raise_http(
                status.HTTP_400_BAD_REQUEST,
                code="GAMIFICACAO_OUT_OF_SCOPE",
                message="Gamificacao invalida para este evento",
                extra={"field": "gamificacao_id"},
            )

    ativacao = Ativacao(
        evento_id=evento_id,
        nome=payload.nome,
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
