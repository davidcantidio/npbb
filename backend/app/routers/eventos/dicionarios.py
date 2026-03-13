"""Rotas de dicionários (all/*) e tags."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    DivisaoDemandante,
    Diretoria,
    Evento,
    FormularioLandingTemplate,
    StatusEvento,
    SubtipoEvento,
    Tag,
    Territorio,
    TipoEvento,
    Usuario,
)
from app.schemas.dominios import (
    DivisaoDemandanteRead,
    DiretoriaRead,
    StatusEventoRead,
    SubtipoEventoRead,
    TagCreate,
    TagRead,
    TerritorioRead,
    TipoEventoRead,
)
from app.schemas.formulario_lead import FormularioLandingTemplateRead
from app.services.formulario_lead_catalog import FORMULARIO_CAMPOS_CATALOGO

from . import _shared

router = APIRouter()


@router.get("/all/cidades", response_model=list[str])
def listar_cidades(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    estado: str | None = Query(None, min_length=1, max_length=10),
):
    query = select(Evento.cidade).where(Evento.cidade.is_not(None)).distinct()
    query = _shared._apply_visibility(query, current_user)
    if estado:
        uf = estado.strip().lower()
        query = query.where(func.lower(Evento.estado) == uf)
    rows = session.exec(query.order_by(func.lower(Evento.cidade))).all()
    return [c for c in rows if c and str(c).strip()]


@router.get("/all/estados", response_model=list[str])
def listar_estados(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    query = select(Evento.estado).where(Evento.estado.is_not(None)).distinct()
    query = _shared._apply_visibility(query, current_user)
    rows = session.exec(query.order_by(func.lower(Evento.estado))).all()
    return [uf for uf in rows if uf and str(uf).strip()]


@router.get("/all/status-evento", response_model=list[StatusEventoRead])
def listar_status_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(StatusEvento)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(StatusEvento.nome.ilike(like))
    desired = [
        _shared.STATUS_PREVISTO,
        _shared.STATUS_A_CONFIRMAR,
        _shared.STATUS_CONFIRMADO,
        _shared.STATUS_REALIZADO,
        _shared.STATUS_CANCELADO,
    ]
    order_case = case(
        *[
            (func.lower(StatusEvento.nome) == nome.lower(), idx)
            for idx, nome in enumerate(desired, start=1)
        ],
        else_=99,
    )
    return session.exec(query.order_by(order_case, StatusEvento.nome)).all()


@router.get("/all/divisoes-demandantes", response_model=list[DivisaoDemandanteRead])
def listar_divisoes_demandantes(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(DivisaoDemandante)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(DivisaoDemandante.nome.ilike(like))
    return session.exec(query.order_by(DivisaoDemandante.nome)).all()


@router.get("/all/diretorias", response_model=list[DiretoriaRead])
def listar_diretorias(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Diretoria)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Diretoria.nome.ilike(like))
    return session.exec(query.order_by(Diretoria.nome)).all()


@router.get("/all/tipos-evento", response_model=list[TipoEventoRead])
def listar_tipos_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(TipoEvento)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(TipoEvento.nome.ilike(like))
    return session.exec(query.order_by(TipoEvento.nome)).all()


@router.get("/all/subtipos-evento", response_model=list[SubtipoEventoRead])
def listar_subtipos_evento(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    tipo_id: int | None = Query(None, ge=1),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(SubtipoEvento)
    if tipo_id is not None:
        query = query.where(SubtipoEvento.tipo_id == tipo_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(SubtipoEvento.nome.ilike(like))
    return session.exec(query.order_by(SubtipoEvento.nome)).all()


@router.get("/all/territorios", response_model=list[TerritorioRead])
def listar_territorios(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Territorio)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Territorio.nome.ilike(like))
    return session.exec(query.order_by(Territorio.nome)).all()


@router.get("/all/tags", response_model=list[TagRead])
def listar_tags(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    query = select(Tag)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(Tag.nome.ilike(like))
    return session.exec(query.order_by(Tag.nome)).all()


@router.get("/all/formulario-templates", response_model=list[FormularioLandingTemplateRead])
def listar_formulario_templates(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    search: str | None = Query(None, min_length=1, max_length=100),
):
    """Lista temas/templates disponíveis para a landing de leads."""
    query = select(FormularioLandingTemplate)
    if search:
        like = f"%{search.strip()}%"
        query = query.where(FormularioLandingTemplate.nome.ilike(like))
    return session.exec(query.order_by(FormularioLandingTemplate.nome)).all()


@router.get("/all/formulario-campos", response_model=list[str])
def listar_formulario_campos(
    current_user: Usuario = Depends(get_current_user),
):
    """Lista o catálogo de campos possíveis para o Formulário de Lead (MVP)."""
    return FORMULARIO_CAMPOS_CATALOGO


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def criar_tag(
    payload: TagCreate,
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    nome = _shared._normalize_str(payload.nome)
    if not nome:
        _shared._raise_http(
            status.HTTP_400_BAD_REQUEST, code="TAG_NAME_REQUIRED", message="nome obrigatorio"
        )

    existing = session.exec(select(Tag).where(func.lower(Tag.nome) == nome.lower())).first()
    if existing:
        response.status_code = status.HTTP_200_OK
        return existing

    tag = Tag(nome=nome)
    session.add(tag)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = session.exec(select(Tag).where(func.lower(Tag.nome) == nome.lower())).first()
        if existing:
            response.status_code = status.HTTP_200_OK
            return existing
        raise

    session.refresh(tag)
    return tag
