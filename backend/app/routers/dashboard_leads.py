"""Dashboard de leads (GET /dashboard/leads)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Ativacao, AtivacaoLead, Evento, Lead, LeadEvento, Usuario, UsuarioTipo, now_utc
from app.schemas.dashboard_leads import (
    DashboardLeadsFilters,
    DashboardLeadsKpis,
    DashboardLeadsQuery,
    DashboardLeadsResponse,
    DashboardLeadsSeries,
    DashboardLeadsSeriesItem,
)
from app.schemas.dashboard_leads_report import (
    DashboardLeadsReportQuery,
    DashboardLeadsReportResponse,
)
from app.services.dashboard_leads_report import build_dashboard_leads_report
from app.utils.dashboard_rankings import get_dashboard_rankings
from app.utils.http_errors import raise_http_error

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _normalize_state(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().upper()


def _normalize_city(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def _normalize_event_name(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def _apply_visibility(filters: list, current_user: Usuario) -> None:
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if not current_user.agencia_id:
            raise_http_error(
                403,
                code="FORBIDDEN",
                message="Usuario agencia sem agencia_id",
                field="agencia_id",
            )
        filters.append(Evento.agencia_id == current_user.agencia_id)


def _apply_date_filters(filters: list, data_inicio: date | None, data_fim: date | None) -> None:
    if data_inicio:
        filters.append(func.date(Lead.data_criacao) >= data_inicio)
    if data_fim:
        filters.append(func.date(Lead.data_criacao) <= data_fim)


def _resolve_granularity(params: DashboardLeadsQuery) -> str:
    if params.granularity:
        return params.granularity
    if params.data_inicio and params.data_fim:
        delta = (params.data_fim - params.data_inicio).days
        return "day" if delta <= 31 else "month"
    return "month"


def _from_clause():
    return (
        LeadEvento.__table__.join(Lead, Lead.id == LeadEvento.lead_id)
        .join(Evento, Evento.id == LeadEvento.evento_id)
    )


def _from_clause_ativacoes():
    return (
        LeadEvento.__table__.join(Lead, Lead.id == LeadEvento.lead_id)
        .join(Evento, Evento.id == LeadEvento.evento_id)
        .outerjoin(AtivacaoLead, AtivacaoLead.lead_id == Lead.id)
        .outerjoin(
            Ativacao,
            (Ativacao.id == AtivacaoLead.ativacao_id) & (Ativacao.evento_id == Evento.id),
        )
    )


@router.get("/leads", response_model=DashboardLeadsResponse)
def dashboard_leads(
    params: DashboardLeadsQuery = Depends(),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    estado_norm = _normalize_state(params.estado)
    cidade_norm = _normalize_city(params.cidade)
    evento_nome_norm = _normalize_event_name(params.evento_nome)

    filters: list = []
    _apply_visibility(filters, current_user)
    _apply_date_filters(filters, params.data_inicio, params.data_fim)

    if params.evento_id is not None:
        filters.append(Evento.id == params.evento_id)
    elif evento_nome_norm:
        filters.append(func.lower(Evento.nome) == evento_nome_norm)
    if estado_norm:
        filters.append(func.upper(Evento.estado) == estado_norm)
    if cidade_norm:
        filters.append(func.lower(Evento.cidade) == cidade_norm)

    from_clause = _from_clause()

    leads_total = session.exec(
        select(func.count(func.distinct(LeadEvento.id))).select_from(from_clause).where(*filters)
    ).one()
    eventos_total = session.exec(
        select(func.count(func.distinct(Evento.id))).select_from(from_clause).where(*filters)
    ).one()
    ativacoes_total = session.exec(
        select(func.count(func.distinct(Ativacao.id))).select_from(_from_clause_ativacoes()).where(*filters)
    ).one()

    granularity = _resolve_granularity(params)
    dialect = session.get_bind().dialect.name if session.get_bind() else ""

    if granularity == "day":
        period_expr = func.date(Lead.data_criacao)
        period_order = period_expr
    else:
        if dialect == "sqlite":
            period_expr = func.strftime("%Y-%m", Lead.data_criacao)
            period_order = period_expr
        else:
            period_expr = func.date_trunc("month", Lead.data_criacao)
            period_order = period_expr

    series_rows = session.exec(
        select(
            period_expr.label("periodo"),
            func.count(func.distinct(LeadEvento.id)).label("total"),
        )
        .select_from(from_clause)
        .where(*filters)
        .group_by(period_expr)
        .order_by(period_order)
    ).all()

    series_items: list[DashboardLeadsSeriesItem] = []
    for periodo, total in series_rows:
        if periodo is None:
            continue
        if isinstance(periodo, date):
            label = periodo.isoformat()
        else:
            label = str(periodo)
        series_items.append(DashboardLeadsSeriesItem(periodo=label, total=int(total or 0)))

    rankings = get_dashboard_rankings(session, from_clause, filters, params.limit)

    return DashboardLeadsResponse(
        generated_at=now_utc(),
        filters=DashboardLeadsFilters(
            data_inicio=params.data_inicio,
            data_fim=params.data_fim,
            evento_id=params.evento_id,
            evento_nome=evento_nome_norm,
            estado=estado_norm,
            cidade=cidade_norm,
            limit=params.limit,
            granularity=granularity,
        ),
        kpis=DashboardLeadsKpis(
            leads_total=int(leads_total or 0),
            eventos_total=int(eventos_total or 0),
            ativacoes_total=int(ativacoes_total or 0),
        ),
        series=DashboardLeadsSeries(
            granularity=granularity,
            leads=series_items,
        ),
        rankings=rankings,
    )


@router.get("/leads/relatorio", response_model=DashboardLeadsReportResponse)
def dashboard_leads_relatorio(
    params: DashboardLeadsReportQuery = Depends(),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return build_dashboard_leads_report(session, params, current_user=current_user)
