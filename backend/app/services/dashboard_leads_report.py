"""Servico de relatorio agregado para dashboard de leads."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Integer, case, cast, func
from sqlmodel import Session, select

from app.models.models import Evento, Lead, LeadEvento, Usuario, UsuarioTipo, now_utc
from app.schemas.dashboard_leads_report import (
    DashboardLeadsClientesBB,
    DashboardLeadsDistribuicaoItem,
    DashboardLeadsPerfilPublico,
    DashboardLeadsPreVenda,
    DashboardLeadsRedes,
    DashboardLeadsReportBigNumbers,
    DashboardLeadsReportFilters,
    DashboardLeadsReportQuery,
    DashboardLeadsReportResponse,
)
from app.utils.http_errors import raise_http_error


def _normalize_event_name(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def _safe_percent(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


def _resolve_event(session: Session, params: DashboardLeadsReportQuery) -> Evento | None:
    if params.evento_id:
        return session.exec(select(Evento).where(Evento.id == params.evento_id)).first()
    if params.evento_nome:
        evento_nome_norm = _normalize_event_name(params.evento_nome)
        if evento_nome_norm:
            return session.exec(
                select(Evento).where(func.lower(Evento.nome) == evento_nome_norm)
            ).first()
    return None


def _apply_auth_visibility(evento: Evento | None, current_user: Usuario | None) -> None:
    if current_user is None:
        return
    if current_user.tipo_usuario == UsuarioTipo.AGENCIA:
        if evento is None or evento.agencia_id != current_user.agencia_id:
            raise_http_error(
                403,
                code="FORBIDDEN",
                message="Filtro por evento_id obrigatorio para agencia",
            )


def _reference_date(evento: Evento | None) -> date:
    if evento and (evento.data_inicio_realizada or evento.data_inicio_prevista):
        return evento.data_inicio_realizada or evento.data_inicio_prevista
    return date.today()


def _from_clause():
    return (
        LeadEvento.__table__.join(Lead, Lead.id == LeadEvento.lead_id)
        .join(Evento, Evento.id == LeadEvento.evento_id)
    )


def _age_expr(dialect: str, ref_date: date):
    if dialect == "sqlite":
        return cast(func.strftime("%Y", ref_date), Integer) - cast(
            func.strftime("%Y", Lead.data_nascimento), Integer
        )
    return func.date_part("year", func.age(ref_date, Lead.data_nascimento))


def _age_bucket_expr(age_expr):
    return case(
        (age_expr < 18, "0-17"),
        (age_expr.between(18, 24), "18-24"),
        (age_expr.between(25, 34), "25-34"),
        (age_expr.between(35, 44), "35-44"),
        (age_expr.between(45, 54), "45-54"),
        else_="55+",
    )


def _gender_bucket_expr():
    genero_norm = func.lower(func.trim(Lead.genero))
    return case(
        (genero_norm.in_(["m", "masculino", "male", "homem"]), "masculino"),
        (genero_norm.in_(["f", "feminino", "female", "mulher"]), "feminino"),
        (genero_norm.is_(None), "nao_informado"),
        (genero_norm == "", "nao_informado"),
        else_="outros",
    )


def build_dashboard_leads_report(
    session: Session,
    params: DashboardLeadsReportQuery,
    current_user: Usuario | None = None,
) -> DashboardLeadsReportResponse:
    evento = _resolve_event(session, params)
    _apply_auth_visibility(evento, current_user)

    evento_nome_norm = _normalize_event_name(
        evento.nome if evento else params.evento_nome
    )

    filtros: list = []
    from_clause = _from_clause()
    if evento is not None:
        filtros.append(Evento.id == evento.id)
    elif evento_nome_norm:
        filtros.append(Evento.id == -1)

    data_ref_expr = func.date(func.coalesce(Lead.data_compra, Lead.data_criacao))
    if params.data_inicio:
        filtros.append(data_ref_expr >= params.data_inicio)
    if params.data_fim:
        filtros.append(data_ref_expr <= params.data_fim)

    total_leads = session.exec(
        select(func.count(func.distinct(LeadEvento.id))).select_from(from_clause).where(*filtros)
    ).one()
    compras_count = session.exec(
        select(func.count(func.distinct(LeadEvento.id)))
        .select_from(from_clause)
        .where(*filtros, Lead.data_compra.is_not(None))
    ).one()
    ingressos_sum = session.exec(
        select(func.sum(Lead.ingresso_qtd)).select_from(from_clause).where(*filtros)
    ).one()

    if compras_count and int(compras_count) > 0:
        total_compras = int(compras_count)
        criterio_compras = "contagem_compras_por_data_compra"
    elif ingressos_sum and int(ingressos_sum) > 0:
        total_compras = int(ingressos_sum)
        criterio_compras = "soma_ingresso_qtd"
    else:
        total_compras = 0
        criterio_compras = "sem_dados_de_compra"

    dados_faltantes: list[str] = []

    total_publico = int(total_leads or 0)
    criterio_publico = "leads_total"
    if evento:
        if evento.publico_realizado is not None:
            total_publico = int(evento.publico_realizado)
            criterio_publico = "evento.publico_realizado"
        elif evento.publico_projetado is not None:
            total_publico = int(evento.publico_projetado)
            criterio_publico = "evento.publico_projetado"
        else:
            dados_faltantes.append("Evento sem publico_realizado/projetado.")
    else:
        dados_faltantes.append("Evento nao encontrado para criterio de publico/pre-venda.")

    taxa_conversao = _safe_percent(total_compras, int(total_leads or 0))

    total_leads_int = int(total_leads or 0)
    dialect = session.get_bind().dialect.name if session.get_bind() else ""
    ref_date = _reference_date(evento)
    age_expr = _age_expr(dialect, ref_date)
    age_bucket = _age_bucket_expr(age_expr)

    total_with_age = session.exec(
        select(func.count(func.distinct(LeadEvento.id)))
        .select_from(from_clause)
        .where(*filtros, Lead.data_nascimento.is_not(None))
    ).one()
    idade_rows = session.exec(
        select(age_bucket.label("faixa"), func.count(func.distinct(LeadEvento.id)).label("total"))
        .select_from(from_clause)
        .where(*filtros, Lead.data_nascimento.is_not(None))
        .group_by(age_bucket)
        .order_by(func.count(func.distinct(LeadEvento.id)).desc(), age_bucket)
    ).all()

    distribuicao_idade = [
        DashboardLeadsDistribuicaoItem(
            faixa=str(faixa),
            total=int(total or 0),
            percentual=_safe_percent(int(total or 0), int(total_with_age or 0)),
        )
        for faixa, total in idade_rows
        if faixa is not None
    ]

    percent_sem_idade = _safe_percent(
        total_leads_int - int(total_with_age or 0), total_leads_int
    )

    gender_bucket = _gender_bucket_expr()
    genero_rows = session.exec(
        select(gender_bucket.label("faixa"), func.count(func.distinct(LeadEvento.id)).label("total"))
        .select_from(from_clause)
        .where(*filtros)
        .group_by(gender_bucket)
        .order_by(func.count(func.distinct(LeadEvento.id)).desc(), gender_bucket)
    ).all()

    total_sem_genero = 0
    distribuicao_genero: list[DashboardLeadsDistribuicaoItem] = []
    for faixa, total in genero_rows:
        if faixa == "nao_informado":
            total_sem_genero = int(total or 0)
            continue
        distribuicao_genero.append(
            DashboardLeadsDistribuicaoItem(
                faixa=str(faixa),
                total=int(total or 0),
                percentual=_safe_percent(int(total or 0), total_leads_int),
            )
        )

    percent_sem_genero = _safe_percent(total_sem_genero, total_leads_int)

    janela_pre_venda = None
    volume_pre_venda = 0
    volume_venda_geral = int(compras_count or 0)
    observacao_pre_venda = None
    if evento and (evento.data_inicio_realizada or evento.data_inicio_prevista):
        evento_inicio = evento.data_inicio_realizada or evento.data_inicio_prevista
        janela_pre_venda = f"ate {evento_inicio.isoformat()}"
        volume_pre_venda = session.exec(
            select(func.count(func.distinct(LeadEvento.id))).select_from(from_clause).where(
                *filtros, Lead.data_compra.is_not(None), func.date(Lead.data_compra) < evento_inicio
            )
        ).one()
        observacao_pre_venda = "Pre-venda definida ate a data de inicio do evento."
    else:
        dados_faltantes.append("Sem data de inicio do evento para calcular pre-venda.")
        observacao_pre_venda = "Pre-venda nao calculada (data do evento ausente)."

    if total_leads_int == 0:
        dados_faltantes.append("Sem leads para o filtro informado.")

    dados_faltantes.append("Nao ha indicador de clientes BB nos leads.")
    dados_faltantes.append("Nao ha dados de redes sociais no sistema.")

    return DashboardLeadsReportResponse(
        generated_at=now_utc(),
        filters=DashboardLeadsReportFilters(
            data_inicio=params.data_inicio,
            data_fim=params.data_fim,
            evento_id=params.evento_id,
            evento_nome=evento_nome_norm,
        ),
        big_numbers=DashboardLeadsReportBigNumbers(
            total_leads=total_leads_int,
            total_compras=int(total_compras),
            total_publico=int(total_publico),
            taxa_conversao=taxa_conversao,
            criterio_publico=criterio_publico,
            criterio_compras=criterio_compras,
        ),
        perfil_publico=DashboardLeadsPerfilPublico(
            distribuicao_idade=distribuicao_idade,
            distribuicao_genero=distribuicao_genero,
            percent_sem_idade=percent_sem_idade,
            percent_sem_genero=percent_sem_genero,
        ),
        clientes_bb=DashboardLeadsClientesBB(
            total_clientes_bb=0,
            percentual_clientes_bb=0.0,
            criterio_usado="sem_dados_no_sistema",
        ),
        pre_venda=DashboardLeadsPreVenda(
            janela_pre_venda=janela_pre_venda,
            volume_pre_venda=int(volume_pre_venda or 0),
            volume_venda_geral=int(volume_venda_geral or 0),
            observacao=observacao_pre_venda,
        ),
        redes=DashboardLeadsRedes(
            status="sem_dados",
            observacao="Sem dados de redes sociais no sistema.",
            metricas=None,
        ),
        dados_faltantes=sorted(set(dados_faltantes)),
    )
