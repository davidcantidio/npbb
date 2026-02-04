"""Rankings do dashboard de leads (agregados no banco)."""

from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import Ativacao, AtivacaoLead, Evento, Lead
from app.schemas.dashboard_leads import (
    DashboardLeadsRankCidade,
    DashboardLeadsRankEstado,
    DashboardLeadsRankEvento,
    DashboardLeadsRankings,
)


def get_dashboard_rankings(
    session: Session,
    from_clause,
    filters: list,
    limit: int,
) -> DashboardLeadsRankings:
    """Retorna rankings agregados no banco (GROUP BY)."""
    count_distinct_leads = func.count(func.distinct(Lead.id))

    estados_rows = session.exec(
        select(
            func.upper(Evento.estado).label("estado"),
            count_distinct_leads.label("total"),
        )
        .select_from(from_clause)
        .where(*filters)
        .group_by(func.upper(Evento.estado))
        .order_by(count_distinct_leads.desc(), func.upper(Evento.estado))
        .limit(limit)
    ).all()
    estados = [
        DashboardLeadsRankEstado(estado=str(estado), total=int(total or 0))
        for estado, total in estados_rows
        if estado is not None
    ]

    cidades_rows = session.exec(
        select(
            func.min(Evento.cidade).label("cidade"),
            count_distinct_leads.label("total"),
        )
        .select_from(from_clause)
        .where(*filters)
        .group_by(func.lower(Evento.cidade))
        .order_by(count_distinct_leads.desc(), func.min(Evento.cidade))
        .limit(limit)
    ).all()
    cidades = [
        DashboardLeadsRankCidade(cidade=str(cidade), total=int(total or 0))
        for cidade, total in cidades_rows
        if cidade is not None
    ]

    eventos_rows = session.exec(
        select(
            Evento.id.label("evento_id"),
            Evento.nome.label("evento_nome"),
            count_distinct_leads.label("total"),
        )
        .select_from(from_clause)
        .where(*filters)
        .group_by(Evento.id, Evento.nome)
        .order_by(count_distinct_leads.desc(), Evento.id)
        .limit(limit)
    ).all()
    eventos = [
        DashboardLeadsRankEvento(
            evento_id=int(evento_id),
            evento_nome=str(evento_nome),
            total=int(total or 0),
        )
        for evento_id, evento_nome, total in eventos_rows
        if evento_id is not None and evento_nome is not None
    ]

    return DashboardLeadsRankings(
        por_estado=estados,
        por_cidade=cidades,
        por_evento=eventos,
    )
