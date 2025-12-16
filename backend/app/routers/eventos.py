"""Rotas de eventos (listagem, dicionarios e detalhes)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Evento, Usuario, UsuarioTipo
from app.schemas.evento import EventoListItem, EventoRead

router = APIRouter(prefix="/evento", tags=["evento"])


def _apply_visibility(query, current_user: Usuario):
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario agencia sem agencia_id",
            )
        return query.where(Evento.agencia_id == current_user.agencia_id)
    return query


@router.get("", response_model=list[EventoListItem])
@router.get("/", response_model=list[EventoListItem])
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
):
    """Lista eventos com paginação e filtros opcionais.

    Filtros:
    - search: busca por nome (case-insensitive)
    - estado: UF (case-insensitive)
    - cidade: cidade (case-insensitive)
    - data: retorna eventos cujo periodo (previsto/realizado) contem a data

    Header `X-Total-Count` contem o total (com filtros aplicados).
    """
    query = select(Evento)
    count_query = select(func.count()).select_from(Evento)

    query = _apply_visibility(query, current_user)
    count_query = _apply_visibility(count_query, current_user)

    if search:
        like = f"%{search.strip()}%"
        query = query.where(Evento.nome.ilike(like))
        count_query = count_query.where(Evento.nome.ilike(like))

    if estado:
        uf = estado.strip().lower()
        query = query.where(func.lower(Evento.estado) == uf)
        count_query = count_query.where(func.lower(Evento.estado) == uf)

    if cidade:
        city = cidade.strip().lower()
        query = query.where(func.lower(Evento.cidade) == city)
        count_query = count_query.where(func.lower(Evento.cidade) == city)

    if data:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        count_query = (
            count_query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        )

    total = session.exec(count_query).one()
    items = session.exec(query.order_by(Evento.id.desc()).offset(skip).limit(limit)).all()
    response.headers["X-Total-Count"] = str(total)
    return items


@router.get("/all/cidades", response_model=list[str])
def listar_cidades(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Evento.cidade).where(Evento.cidade.is_not(None)).distinct()
    query = _apply_visibility(query, current_user)
    rows = session.exec(query.order_by(func.lower(Evento.cidade))).all()
    values = [c for c in rows if c and str(c).strip()]
    return values


@router.get("/all/estados", response_model=list[str])
def listar_estados(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Evento.estado).where(Evento.estado.is_not(None)).distinct()
    query = _apply_visibility(query, current_user)
    rows = session.exec(query.order_by(func.lower(Evento.estado))).all()
    values = [uf for uf in rows if uf and str(uf).strip()]
    return values


@router.get("/{evento_id}", response_model=EventoRead)
def obter_evento(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = session.get(Evento, evento_id)
    if not evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA and current_user.agencia_id:
        if evento.agencia_id != current_user.agencia_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento nao encontrado")

    return EventoRead.model_validate(evento, from_attributes=True)

