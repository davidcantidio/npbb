"""Rotas CRUD de eventos."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.models.models import now_utc
from app.db.database import get_session
from app.models.models import EventoTag, EventoTerritorio, Usuario
from app.modules.eventos.application.evento_list_usecase import listar_eventos_usecase
from app.modules.eventos.application.evento_write_usecases import (
    atualizar_evento_usecase,
    criar_evento_usecase,
    excluir_evento_usecase,
)
from app.schemas.evento import EventoCreate, EventoListItem, EventoRead, EventoUpdate
from app.services.landing_pages import hydrate_evento_public_urls

from . import _shared

router = APIRouter()


def listar_eventos(
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    search: str | None = Query(None, min_length=1, max_length=100),
    estado: str | None = Query(None, min_length=1, max_length=10),
    cidade: str | None = Query(None, min_length=1, max_length=100),
    data: date | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    diretoria_id: int | None = Query(None, ge=1),
):
    """Lista eventos com paginação e filtros opcionais."""
    items, total = listar_eventos_usecase(
        session=session,
        current_user=current_user,
        apply_visibility=_shared._apply_visibility,
        raise_http=_shared._raise_http,
        skip=skip,
        limit=limit,
        search=search,
        estado=estado,
        cidade=cidade,
        data=data,
        data_inicio=data_inicio,
        data_fim=data_fim,
        diretoria_id=diretoria_id,
    )
    response.headers["X-Total-Count"] = str(total)
    return items


def criar_evento(
    payload: EventoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return criar_evento_usecase(payload=payload, session=session, current_user=current_user)


@router.put("/{evento_id}", response_model=EventoRead)
@router.put("/{evento_id}/", response_model=EventoRead)
def atualizar_evento(
    evento_id: int,
    payload: EventoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return atualizar_evento_usecase(
        evento_id=evento_id,
        payload=payload,
        session=session,
        current_user=current_user,
    )


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{evento_id}/", status_code=status.HTTP_204_NO_CONTENT)
def excluir_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return excluir_evento_usecase(evento_id=evento_id, session=session, current_user=current_user)


@router.get("/{evento_id}", response_model=EventoRead)
@router.get("/{evento_id}/", response_model=EventoRead)
def obter_evento(
    evento_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = _shared._check_evento_visible_or_404(session, evento_id, current_user)

    if hydrate_evento_public_urls(evento, backend_base_url=str(request.base_url)):
        evento.updated_at = now_utc()
        session.add(evento)
        session.commit()
        session.refresh(evento)

    tag_ids = session.exec(
        select(EventoTag.tag_id).where(EventoTag.evento_id == evento_id).order_by(EventoTag.tag_id)
    ).all()
    territorio_ids = session.exec(
        select(EventoTerritorio.territorio_id)
        .where(EventoTerritorio.evento_id == evento_id)
        .order_by(EventoTerritorio.territorio_id)
    ).all()

    read = EventoRead.model_validate(evento, from_attributes=True)
    return read.model_copy(
        update={"tag_ids": list(tag_ids), "territorio_ids": list(territorio_ids)}
    )
