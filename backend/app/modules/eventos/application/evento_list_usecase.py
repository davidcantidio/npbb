"""Use case para listagem de eventos com filtros e enriquecimento."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import (
    Evento,
    EventoTag,
    EventoTerritorio,
    StatusEvento,
    Usuario,
    now_utc,
)
from app.schemas.evento import DataHealthRead, EventoListItem
from app.services.data_health import compute_event_data_health
from app.services.landing_pages import hydrate_evento_public_urls


def listar_eventos_usecase(
    session: Session,
    current_user: Usuario,
    apply_visibility,
    raise_http,
    *,
    skip: int = 0,
    limit: int = 25,
    search: str | None = None,
    estado: str | None = None,
    cidade: str | None = None,
    data: date | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    diretoria_id: int | None = None,
) -> tuple[list[EventoListItem], int]:
    """Lista eventos com paginação e filtros. Retorna (items, total_count)."""
    from fastapi import status

    query = select(Evento)
    count_query = select(func.count()).select_from(Evento)

    query = apply_visibility(query, current_user)
    count_query = apply_visibility(count_query, current_user)

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

    if diretoria_id is not None:
        query = query.where(Evento.diretoria_id == diretoria_id)
        count_query = count_query.where(Evento.diretoria_id == diretoria_id)

    if data_inicio and data_fim and data_fim < data_inicio:
        raise_http(
            status.HTTP_400_BAD_REQUEST,
            code="DATE_RANGE_INVALID",
            message="data_fim deve ser maior/igual a data_inicio",
        )

    if data_inicio or data_fim:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None))
        count_query = count_query.where(inicio.is_not(None))

        if data_inicio:
            query = query.where(fim >= data_inicio)
            count_query = count_query.where(fim >= data_inicio)
        if data_fim:
            query = query.where(inicio <= data_fim)
            count_query = count_query.where(inicio <= data_fim)
    elif data:
        inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, inicio)
        query = query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        count_query = (
            count_query.where(inicio.is_not(None)).where(inicio <= data).where(fim >= data)
        )

    total = session.exec(count_query).one()
    eventos = session.exec(query.order_by(Evento.id.desc()).offset(skip).limit(limit)).all()

    if not eventos:
        return [], total

    changed = False
    for evento in eventos:
        changed = hydrate_evento_public_urls(evento) or changed
    if changed:
        for evento in eventos:
            evento.updated_at = now_utc()
            session.add(evento)
        session.commit()
        for evento in eventos:
            session.refresh(evento)

    evento_ids = [e.id for e in eventos if e.id is not None]
    status_ids = {e.status_id for e in eventos if e.status_id is not None}

    status_nome_by_id: dict[int, str] = {}
    if status_ids:
        rows = session.exec(
            select(StatusEvento.id, StatusEvento.nome).where(
                StatusEvento.id.in_(sorted(status_ids))
            )
        ).all()
        status_nome_by_id = {
            int(row_id): str(nome)
            for row_id, nome in rows
            if row_id is not None and nome is not None
        }

    tag_ids_by_evento: dict[int, list[int]] = {}
    territorio_ids_by_evento: dict[int, list[int]] = {}
    if evento_ids:
        tag_rows = session.exec(
            select(EventoTag.evento_id, EventoTag.tag_id)
            .where(EventoTag.evento_id.in_(evento_ids))
            .order_by(EventoTag.evento_id, EventoTag.tag_id)
        ).all()
        for evento_id, tag_id in tag_rows:
            if evento_id is None or tag_id is None:
                continue
            tag_ids_by_evento.setdefault(int(evento_id), []).append(int(tag_id))

        territorio_rows = session.exec(
            select(EventoTerritorio.evento_id, EventoTerritorio.territorio_id)
            .where(EventoTerritorio.evento_id.in_(evento_ids))
            .order_by(EventoTerritorio.evento_id, EventoTerritorio.territorio_id)
        ).all()
        for evento_id, territorio_id in territorio_rows:
            if evento_id is None or territorio_id is None:
                continue
            territorio_ids_by_evento.setdefault(int(evento_id), []).append(int(territorio_id))

    items: list[EventoListItem] = []
    for evento in eventos:
        eid = int(evento.id) if evento.id is not None else None
        proxy_data = evento.model_dump()
        proxy_data["tag_ids"] = tag_ids_by_evento.get(eid, []) if eid else []
        proxy_data["territorio_ids"] = territorio_ids_by_evento.get(eid, []) if eid else []

        data_health = compute_event_data_health(
            SimpleNamespace(**proxy_data),
            status_name=status_nome_by_id.get(evento.status_id),
        )
        data_health_model = DataHealthRead.model_validate(data_health)

        item = EventoListItem.model_validate(evento, from_attributes=True)
        items.append(item.model_copy(update={"data_health": data_health_model}))

    return items, total
