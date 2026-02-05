"""Rotas de ativos (cotas de ingressos por evento/diretoria)."""

from __future__ import annotations

import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    CotaCortesia,
    Diretoria,
    Evento,
    SolicitacaoIngresso,
    SolicitacaoIngressoStatus,
    Usuario,
    UsuarioTipo,
)
from app.schemas.ativos import AtivoAssignPayload, AtivoListItem
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/ativos", tags=["ativos"])

CSV_EXPORT_LIMIT = 10_000


def _apply_visibility(query, current_user: Usuario):
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                extra={"field": "agencia_id"},
            )
        return query.where(Evento.agencia_id == current_user.agencia_id)
    return query


def _apply_filters(query, *, evento_id: int | None, diretoria_id: int | None, data: date | None):
    if evento_id is not None:
        query = query.where(CotaCortesia.evento_id == evento_id)
    if diretoria_id is not None:
        query = query.where(CotaCortesia.diretoria_id == diretoria_id)
    if data is not None:
        data_inicio = func.coalesce(Evento.data_inicio_prevista, Evento.data_inicio_realizada)
        data_fim = func.coalesce(Evento.data_fim_prevista, Evento.data_fim_realizada, data_inicio)
        query = query.where(data_inicio <= data, data_fim >= data)
    return query


def _build_usados_subquery():
    return (
        select(SolicitacaoIngresso.cota_id, func.count().label("usados"))
        .where(SolicitacaoIngresso.status == SolicitacaoIngressoStatus.SOLICITADO)
        .group_by(SolicitacaoIngresso.cota_id)
        .subquery()
    )


def _count_usados(session: Session, cota_id: int) -> int:
    result = session.exec(
        select(func.count(SolicitacaoIngresso.id)).where(
            SolicitacaoIngresso.cota_id == cota_id,
            SolicitacaoIngresso.status == SolicitacaoIngressoStatus.SOLICITADO,
        )
    ).one()
    return int(result[0] if not isinstance(result, int) else result)


def _build_item(cota: CotaCortesia, evento: Evento, diretoria: Diretoria, usados: int) -> AtivoListItem:
    total = int(cota.quantidade)
    usados_int = int(usados)
    disponiveis = max(total - usados_int, 0)
    percentual = usados_int / total if total > 0 else 0.0
    data_inicio = evento.data_inicio_prevista or evento.data_inicio_realizada
    data_fim = evento.data_fim_prevista or evento.data_fim_realizada or data_inicio

    return AtivoListItem(
        id=int(cota.id),
        evento_id=int(evento.id),
        evento_nome=str(evento.nome),
        diretoria_id=int(diretoria.id),
        diretoria_nome=str(diretoria.nome),
        total=total,
        usados=usados_int,
        disponiveis=disponiveis,
        percentual_usado=percentual,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )


@router.get("", response_model=list[AtivoListItem])
@router.get("/", response_model=list[AtivoListItem])
def listar_ativos(
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    evento_id: int | None = Query(None, ge=1),
    diretoria_id: int | None = Query(None, ge=1),
    data: date | None = Query(None),
):
    usados_subq = _build_usados_subquery()

    base_query = (
        select(
            CotaCortesia,
            Evento,
            Diretoria,
            func.coalesce(usados_subq.c.usados, 0).label("usados"),
        )
        .join(Evento, CotaCortesia.evento_id == Evento.id)
        .join(Diretoria, CotaCortesia.diretoria_id == Diretoria.id)
        .outerjoin(usados_subq, usados_subq.c.cota_id == CotaCortesia.id)
    )
    base_query = _apply_visibility(base_query, current_user)
    base_query = _apply_filters(
        base_query, evento_id=evento_id, diretoria_id=diretoria_id, data=data
    )

    count_query = (
        select(func.count())
        .select_from(CotaCortesia)
        .join(Evento, CotaCortesia.evento_id == Evento.id)
        .join(Diretoria, CotaCortesia.diretoria_id == Diretoria.id)
    )
    count_query = _apply_visibility(count_query, current_user)
    count_query = _apply_filters(
        count_query, evento_id=evento_id, diretoria_id=diretoria_id, data=data
    )

    total_row = session.exec(count_query).one()
    total = int(total_row[0] if not isinstance(total_row, int) else total_row)
    response.headers["X-Total-Count"] = str(total)

    rows = session.exec(
        base_query.order_by(CotaCortesia.id.desc()).offset(skip).limit(limit)
    ).all()

    return [_build_item(cota, evento, diretoria, usados) for cota, evento, diretoria, usados in rows]


@router.post("/{evento_id}/{diretoria_id}/atribuir", response_model=AtivoListItem)
def atribuir_cota(
    payload: AtivoAssignPayload,
    evento_id: int,
    diretoria_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    if payload.quantidade < 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="COTA_NEGATIVE",
            message="Quantidade nao pode ser negativa",
        )

    evento = session.get(Evento, evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
        )

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                extra={"field": "agencia_id"},
            )
        if evento.agencia_id != current_user.agencia_id:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="EVENTO_NOT_FOUND",
                message="Evento nao encontrado",
            )

    diretoria = session.get(Diretoria, diretoria_id)
    if not diretoria:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="DIRETORIA_NOT_FOUND",
            message="Diretoria nao encontrada",
        )

    cota = session.exec(
        select(CotaCortesia).where(
            CotaCortesia.evento_id == evento_id,
            CotaCortesia.diretoria_id == diretoria_id,
        )
    ).first()

    usados = 0
    if cota and cota.id is not None:
        usados = _count_usados(session, int(cota.id))
        if payload.quantidade < usados:
            raise_http_error(
                status.HTTP_409_CONFLICT,
                code="COTA_BELOW_USED",
                message="Quantidade nao pode ser menor que o total usado",
            )
        cota.quantidade = payload.quantidade
    else:
        cota = CotaCortesia(
            evento_id=evento_id,
            diretoria_id=diretoria_id,
            quantidade=payload.quantidade,
        )
        session.add(cota)

    session.commit()
    session.refresh(cota)

    usados = _count_usados(session, int(cota.id))
    return _build_item(cota, evento, diretoria, usados)


@router.delete("/{cota_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cota(
    cota_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    cota = session.get(CotaCortesia, cota_id)
    if not cota:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="COTA_NOT_FOUND",
            message="Cota nao encontrada",
        )

    evento = session.get(Evento, cota.evento_id)
    if not evento:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="EVENTO_NOT_FOUND",
            message="Evento nao encontrado",
        )

    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise_http_error(
                status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                extra={"field": "agencia_id"},
            )
        if evento.agencia_id != current_user.agencia_id:
            raise_http_error(
                status.HTTP_404_NOT_FOUND,
                code="COTA_NOT_FOUND",
                message="Cota nao encontrada",
            )

    usados = _count_usados(session, int(cota.id))
    if usados > 0:
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="COTA_HAS_USED",
            message="Nao e possivel excluir uma cota com solicitacoes emitidas",
        )

    session.delete(cota)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/export/csv")
def exportar_csv(
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    evento_id: int | None = Query(None, ge=1),
    diretoria_id: int | None = Query(None, ge=1),
    data: date | None = Query(None),
):
    usados_subq = _build_usados_subquery()

    base_query = (
        select(
            CotaCortesia,
            Evento,
            Diretoria,
            func.coalesce(usados_subq.c.usados, 0).label("usados"),
        )
        .join(Evento, CotaCortesia.evento_id == Evento.id)
        .join(Diretoria, CotaCortesia.diretoria_id == Diretoria.id)
        .outerjoin(usados_subq, usados_subq.c.cota_id == CotaCortesia.id)
    )
    base_query = _apply_visibility(base_query, current_user)
    base_query = _apply_filters(
        base_query, evento_id=evento_id, diretoria_id=diretoria_id, data=data
    )

    count_query = (
        select(func.count())
        .select_from(CotaCortesia)
        .join(Evento, CotaCortesia.evento_id == Evento.id)
        .join(Diretoria, CotaCortesia.diretoria_id == Diretoria.id)
    )
    count_query = _apply_visibility(count_query, current_user)
    count_query = _apply_filters(
        count_query, evento_id=evento_id, diretoria_id=diretoria_id, data=data
    )

    total_row = session.exec(count_query).one()
    total = int(total_row[0] if not isinstance(total_row, int) else total_row)
    if total > CSV_EXPORT_LIMIT:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="CSV_LIMIT_EXCEEDED",
            message="Limite de exportacao excedido",
        )

    rows = session.exec(base_query.order_by(CotaCortesia.id.desc())).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Evento",
            "Diretoria",
            "Data inicio",
            "Data fim",
            "Total",
            "Usados",
            "Disponiveis",
            "Percentual",
        ]
    )

    for cota, evento, diretoria, usados in rows:
        item = _build_item(cota, evento, diretoria, int(usados))
        writer.writerow(
            [
                item.evento_nome,
                item.diretoria_nome,
                item.data_inicio.isoformat() if item.data_inicio else "",
                item.data_fim.isoformat() if item.data_fim else "",
                item.total,
                item.usados,
                item.disponiveis,
                f"{item.percentual_usado:.2f}",
            ]
        )

    response.headers["Content-Disposition"] = "attachment; filename=ativos.csv"
    return Response(content=buffer.getvalue(), media_type="text/csv")
