
"""Listagem, exportacao e conversoes de leads."""

from __future__ import annotations

import csv
import io
import os
import re
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, status
from fastapi import Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, case, func, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text
from sqlmodel import Session, select

from lead_pipeline.constants import TIPO_EVENTO_PADRAO

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.lead_batch import LeadBatch
from app.models.models import Evento, Lead, LeadConversao, LeadEvento, LeadEventoSourceKind, TipoEvento, Usuario, now_utc
from app.schemas.lead_conversao import LeadConversaoCreate, LeadConversaoRead
from app.schemas.lead_list import LeadListItemRead, LeadListQuery, LeadListResponse
from app.utils.http_errors import raise_http_error

router = APIRouter()


def _format_data_csv_dia_meia_noite(d: date | None) -> str | None:
    if d is None:
        return None
    return f"{d.isoformat()} 00:00:00"


def _format_data_evento_export(
    evento_data: date | None,
    data_conversao: datetime | None,
) -> str | None:
    if evento_data is not None:
        return _format_data_csv_dia_meia_noite(evento_data)
    if data_conversao is not None:
        return _format_data_csv_dia_meia_noite(data_conversao.date())
    return None


def _ano_evento_export(evento_data: date | None, data_conversao: datetime | None) -> int | None:
    if evento_data is not None:
        return int(evento_data.year)
    if data_conversao is not None:
        return int(data_conversao.year)
    return None


def _ref_date_for_age(evento_data: date | None, data_conversao: datetime | None) -> date | None:
    if evento_data is not None:
        return evento_data
    if data_conversao is not None:
        return data_conversao.date()
    return None


def _idade_na_data_ref(data_nascimento: date | None, ref: date | None) -> int | None:
    if data_nascimento is None or ref is None:
        return None
    age = ref.year - data_nascimento.year
    if (ref.month, ref.day) < (data_nascimento.month, data_nascimento.day):
        age -= 1
    return max(0, age)


def _faixa_etaria_export_data2(idade: int | None) -> str | None:
    if idade is None:
        return None
    if idade < 18:
        return "0-17"
    if idade <= 40:
        return "18-40"
    return "40+"


def _format_local_evento_export(cidade: str | None, estado: str | None) -> str | None:
    cidade_value = (cidade or "").strip()
    estado_value = (estado or "").strip()
    if not cidade_value and not estado_value:
        return None
    if cidade_value and estado_value:
        return f"{cidade_value}-{estado_value}"
    return cidade_value or estado_value


def _lead_evento_source_priority_expr(source_kind_col):
    return case(
        (source_kind_col == LeadEventoSourceKind.EVENT_NAME_BACKFILL, 1),
        (source_kind_col == LeadEventoSourceKind.LEAD_BATCH, 2),
        (source_kind_col == LeadEventoSourceKind.EVENT_DIRECT, 3),
        (source_kind_col == LeadEventoSourceKind.ACTIVATION, 4),
        (source_kind_col == LeadEventoSourceKind.MANUAL_RECONCILED, 5),
        else_=0,
    )


def _preferred_lead_evento_subquery():
    ranked = (
        select(
            LeadEvento.lead_id.label("lead_id"),
            LeadEvento.evento_id.label("evento_id"),
            func.row_number()
            .over(
                partition_by=LeadEvento.lead_id,
                order_by=(
                    _lead_evento_source_priority_expr(LeadEvento.source_kind).desc(),
                    LeadEvento.updated_at.desc(),
                    LeadEvento.created_at.desc(),
                    LeadEvento.id.desc(),
                ),
            )
            .label("row_num"),
        )
        .subquery()
    )
    return (
        select(
            ranked.c.lead_id,
            ranked.c.evento_id,
        )
        .where(ranked.c.row_num == 1)
        .subquery()
    )


def _lead_list_effective_event_id_expr(
    canonical_evento_id_col,
    origem_evento_id_col,
):
    return case(
        (LeadConversao.evento_id.isnot(None), LeadConversao.evento_id),
        (canonical_evento_id_col.isnot(None), canonical_evento_id_col),
        else_=origem_evento_id_col,
    )


def _lead_list_effective_event_name_expr(
    canonical_evento_nome_col,
    origem_evento_nome_col,
):
    return func.coalesce(
        Evento.nome,
        canonical_evento_nome_col,
        origem_evento_nome_col,
        Lead.evento_nome,
    )


def _lead_list_effective_event_date_expr(
    canonical_evento_id_col,
    evento_canonico,
    evento_origem,
):
    """Data do evento usada na listagem (conversao mais recente, LeadEvento, lote)."""
    data_conv = func.coalesce(LeadConversao.data_conversao_evento, LeadConversao.created_at)
    conversao_branch = func.coalesce(Evento.data_inicio_prevista, func.date(data_conv))
    return case(
        (LeadConversao.evento_id.isnot(None), conversao_branch),
        (canonical_evento_id_col.isnot(None), evento_canonico.data_inicio_prevista),
        else_=evento_origem.data_inicio_prevista,
    )


def _lead_list_full_name_expr():
    return func.trim(func.coalesce(Lead.nome, "") + " " + func.coalesce(Lead.sobrenome, ""))


def _lead_list_normalized_text_expr(column):
    return func.lower(func.trim(func.coalesce(column, "")))


def _lead_list_origin_bucket_expr(
    fonte_origem_col,
    origem_lote_col,
    plataforma_origem_col,
):
    origem_lote_expr = _lead_list_normalized_text_expr(origem_lote_col)
    fonte_expr = _lead_list_normalized_text_expr(fonte_origem_col)
    plataforma_expr = _lead_list_normalized_text_expr(plataforma_origem_col)

    def is_ativacao(expr):
        return or_(expr == "ativacao", expr.like("ativ%"), expr.like("%ativ%"))

    def is_proponente(expr):
        return or_(expr == "proponente", expr.like("proponent%"), expr.like("%proponente%"))

    return case(
        (is_ativacao(origem_lote_expr), "ativacao"),
        (is_proponente(origem_lote_expr), "proponente"),
        (is_ativacao(fonte_expr), "ativacao"),
        (is_proponente(fonte_expr), "proponente"),
        (is_ativacao(plataforma_expr), "ativacao"),
        (is_proponente(plataforma_expr), "proponente"),
        else_=None,
    )


def _lead_list_escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _lead_list_search_filter(
    search: str | None,
    *,
    evento_canonico,
    evento_origem,
    origem_bucket_expr,
):
    normalized = (search or "").strip().lower()
    if not normalized:
        return None

    text_pattern = f"{_lead_list_escape_like(normalized)}%"
    digits = re.sub(r"\D+", "", normalized)

    predicates = [
        _lead_list_normalized_text_expr(Lead.nome).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(Lead.sobrenome).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(_lead_list_full_name_expr()).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(Lead.email).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(
            _lead_list_effective_event_name_expr(evento_canonico.nome, evento_origem.nome)
        ).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(Lead.cidade).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(Lead.estado).like(text_pattern, escape="\\"),
        _lead_list_normalized_text_expr(origem_bucket_expr).like(text_pattern, escape="\\"),
    ]
    if digits:
        digits_pattern = f"{digits}%"
        predicates.extend(
            [
                func.coalesce(Lead.cpf, "").like(digits_pattern, escape="\\"),
                func.coalesce(Lead.telefone, "").like(digits_pattern, escape="\\"),
            ]
        )
    return or_(*predicates)


def _lead_list_filters(
    params: LeadListQuery,
    *,
    canonical_evento_id_col=None,
    origem_evento_id_col=None,
    evento_canonico=None,
    evento_origem=None,
    origem_bucket_expr=None,
) -> list:
    filters: list = []
    if params.data_inicio is not None or params.data_fim is not None:
        if (
            evento_origem is None
            or evento_canonico is None
            or canonical_evento_id_col is None
        ):
            raise ValueError("evento_origem/evento_canonico are required when filtering by data_inicio/data_fim")
        eff = _lead_list_effective_event_date_expr(
            canonical_evento_id_col,
            evento_canonico,
            evento_origem,
        )
        if params.data_inicio is not None:
            filters.append(eff >= params.data_inicio)
        if params.data_fim is not None:
            filters.append(eff <= params.data_fim)
    if params.evento_id is not None:
        if origem_evento_id_col is None or canonical_evento_id_col is None:
            filters.append(LeadConversao.evento_id == params.evento_id)
        else:
            filters.append(
                _lead_list_effective_event_id_expr(
                    canonical_evento_id_col,
                    origem_evento_id_col,
                )
                == params.evento_id
            )
    if params.origem is not None and origem_bucket_expr is not None:
        filters.append(origem_bucket_expr == params.origem)
    search_filter = _lead_list_search_filter(
        params.search,
        evento_canonico=evento_canonico,
        evento_origem=evento_origem,
        origem_bucket_expr=origem_bucket_expr,
    )
    if search_filter is not None:
        filters.append(search_filter)
    return filters


def _build_latest_lead_conversao_subquery():
    return (
        select(
            LeadConversao.lead_id.label("lead_id"),
            func.max(LeadConversao.id).label("latest_conversao_id"),
        )
        .group_by(LeadConversao.lead_id)
        .subquery()
    )


def _lead_list_order_by_clauses(
    params: LeadListQuery,
    *,
    evento_canonico,
    evento_origem,
    origem_bucket_expr,
):
    descending = params.sort_dir == "desc"

    def apply_direction(expression):
        return expression.desc() if descending else expression.asc()

    if params.sort_by == "nome":
        primary_clauses = [apply_direction(_lead_list_normalized_text_expr(_lead_list_full_name_expr()))]
    elif params.sort_by == "email":
        primary_clauses = [apply_direction(_lead_list_normalized_text_expr(Lead.email))]
    elif params.sort_by == "evento":
        primary_clauses = [
            apply_direction(
                _lead_list_normalized_text_expr(
                    _lead_list_effective_event_name_expr(evento_canonico.nome, evento_origem.nome)
                )
            )
        ]
    elif params.sort_by == "origem":
        primary_clauses = [apply_direction(_lead_list_normalized_text_expr(origem_bucket_expr))]
    elif params.sort_by == "local":
        primary_clauses = [
            apply_direction(_lead_list_normalized_text_expr(Lead.cidade)),
            apply_direction(_lead_list_normalized_text_expr(Lead.estado)),
        ]
    else:
        primary_clauses = [apply_direction(Lead.data_criacao)]

    if params.sort_by != "data_criacao":
        primary_clauses.append(Lead.data_criacao.desc())
    primary_clauses.append(Lead.id.desc() if descending else Lead.id.asc())
    return primary_clauses


def _lead_list_has_complex_filters(params: LeadListQuery) -> bool:
    return any(
        (
            params.data_inicio is not None,
            params.data_fim is not None,
            params.evento_id is not None,
            params.origem is not None,
            bool(params.search),
        )
    )


def _lead_list_requires_id_joins(params: LeadListQuery) -> bool:
    return _lead_list_has_complex_filters(params) or params.sort_by in {"evento", "origem"}


def _configure_listar_leads_statement_timeout(session: Session, params: LeadListQuery) -> None:
    if not params.long_running:
        return
    bind = session.get_bind()
    dialect_name = getattr(getattr(bind, "dialect", None), "name", "")
    if dialect_name != "postgresql":
        return
    timeout_ms = max(int(os.getenv("LEADS_EXPORT_STATEMENT_TIMEOUT_MS", "900000")), 0)
    session.exec(text(f"SET LOCAL statement_timeout = {timeout_ms}"))


def listar_leads_impl(
    session: Session,
    current_user: Usuario,
    params: LeadListQuery,
    *,
    compute_total: bool = True,
) -> LeadListResponse:
    """Implementacao interna da listagem; exportacao CSV usa compute_total=False para evitar COUNT por pagina."""
    _ = current_user
    _configure_listar_leads_statement_timeout(session, params)
    offset = (params.page - 1) * params.page_size
    lead_evento_preferido = _preferred_lead_evento_subquery()
    evento_canonico = aliased(Evento)
    tipo_evento_canonico = aliased(TipoEvento)
    evento_origem = aliased(Evento)
    tipo_evento_origem = aliased(TipoEvento)
    latest_conversao_subquery = _build_latest_lead_conversao_subquery()
    origem_bucket_expr = _lead_list_origin_bucket_expr(
        Lead.fonte_origem,
        LeadBatch.origem_lote,
        LeadBatch.plataforma_origem,
    )

    list_filters = _lead_list_filters(
        params,
        canonical_evento_id_col=lead_evento_preferido.c.evento_id,
        origem_evento_id_col=LeadBatch.evento_id,
        evento_canonico=evento_canonico,
        evento_origem=evento_origem,
        origem_bucket_expr=origem_bucket_expr,
    )
    order_by_clauses = _lead_list_order_by_clauses(
        params,
        evento_canonico=evento_canonico,
        evento_origem=evento_origem,
        origem_bucket_expr=origem_bucket_expr,
    )
    has_complex_filters = _lead_list_has_complex_filters(params)
    requires_id_joins = _lead_list_requires_id_joins(params)

    base_ids_stmt = select(Lead.id.label("lead_id")).select_from(Lead)
    if requires_id_joins:
        base_ids_stmt = (
            base_ids_stmt.outerjoin(latest_conversao_subquery, latest_conversao_subquery.c.lead_id == Lead.id)
            .outerjoin(LeadConversao, LeadConversao.id == latest_conversao_subquery.c.latest_conversao_id)
            .outerjoin(Evento, Evento.id == LeadConversao.evento_id)
            .outerjoin(lead_evento_preferido, lead_evento_preferido.c.lead_id == Lead.id)
            .outerjoin(evento_canonico, evento_canonico.id == lead_evento_preferido.c.evento_id)
            .outerjoin(LeadBatch, LeadBatch.id == Lead.batch_id)
            .outerjoin(evento_origem, evento_origem.id == LeadBatch.evento_id)
        )
    if list_filters:
        base_ids_stmt = base_ids_stmt.where(and_(*list_filters))

    total = 0
    if compute_total:
        if has_complex_filters:
            total = int(
                session.exec(
                    select(func.count()).select_from(base_ids_stmt.subquery())
                ).one()
                or 0
            )
        else:
            total = int(session.exec(select(func.count(Lead.id)).select_from(Lead)).one() or 0)
        if total == 0:
            return LeadListResponse(
                page=params.page,
                page_size=params.page_size,
                total=0,
                items=[],
            )

    page_ids = (
        base_ids_stmt.order_by(*order_by_clauses)
        .offset(offset)
        .limit(params.page_size)
        .subquery()
    )

    rows = session.exec(
        select(
            Lead.id,
            Lead.nome,
            Lead.sobrenome,
            Lead.email,
            Lead.cpf,
            Lead.telefone,
            Lead.evento_nome,
            Lead.cidade,
            Lead.estado,
            Lead.data_compra,
            Lead.data_criacao,
            Lead.data_nascimento,
            LeadConversao.tipo,
            LeadConversao.data_conversao_evento,
            LeadConversao.created_at,
            LeadConversao.evento_id,
            Evento.nome.label("evento_convertido_nome"),
            Evento.data_inicio_prevista.label("evento_data_inicio_prevista"),
            Evento.data_fim_prevista.label("evento_data_fim_prevista"),
            Evento.cidade.label("evento_cidade"),
            Evento.estado.label("evento_estado"),
            TipoEvento.nome.label("tipo_evento_nome"),
            lead_evento_preferido.c.evento_id.label("evento_canonico_id"),
            evento_canonico.nome.label("evento_canonico_nome"),
            evento_canonico.data_inicio_prevista.label("evento_canonico_data_inicio_prevista"),
            evento_canonico.data_fim_prevista.label("evento_canonico_data_fim_prevista"),
            evento_canonico.cidade.label("evento_canonico_cidade"),
            evento_canonico.estado.label("evento_canonico_estado"),
            evento_canonico.tipo_id.label("evento_canonico_tipo_id"),
            tipo_evento_canonico.nome.label("tipo_evento_canonico_nome"),
            LeadBatch.evento_id.label("evento_origem_id"),
            evento_origem.nome.label("evento_origem_nome"),
            evento_origem.data_inicio_prevista.label("evento_origem_data_inicio_prevista"),
            evento_origem.data_fim_prevista.label("evento_origem_data_fim_prevista"),
            evento_origem.cidade.label("evento_origem_cidade"),
            evento_origem.estado.label("evento_origem_estado"),
            evento_origem.tipo_id.label("evento_origem_tipo_id"),
            tipo_evento_origem.nome.label("tipo_evento_origem_nome"),
            Lead.rg,
            Lead.genero,
            Lead.is_cliente_bb,
            Lead.is_cliente_estilo,
            Lead.endereco_rua,
            Lead.endereco_numero,
            Lead.complemento,
            Lead.bairro,
            Lead.cep,
            Lead.fonte_origem,
            LeadBatch.origem_lote,
            LeadBatch.plataforma_origem,
        )
        .select_from(page_ids)
        .join(Lead, Lead.id == page_ids.c.lead_id)
        .outerjoin(latest_conversao_subquery, latest_conversao_subquery.c.lead_id == Lead.id)
        .outerjoin(LeadConversao, LeadConversao.id == latest_conversao_subquery.c.latest_conversao_id)
        .outerjoin(Evento, Evento.id == LeadConversao.evento_id)
        .outerjoin(TipoEvento, TipoEvento.id == Evento.tipo_id)
        .outerjoin(lead_evento_preferido, lead_evento_preferido.c.lead_id == Lead.id)
        .outerjoin(evento_canonico, evento_canonico.id == lead_evento_preferido.c.evento_id)
        .outerjoin(tipo_evento_canonico, tipo_evento_canonico.id == evento_canonico.tipo_id)
        .outerjoin(LeadBatch, LeadBatch.id == Lead.batch_id)
        .outerjoin(evento_origem, evento_origem.id == LeadBatch.evento_id)
        .outerjoin(tipo_evento_origem, tipo_evento_origem.id == evento_origem.tipo_id)
        .order_by(*order_by_clauses)
    ).all()

    items: list[LeadListItemRead] = []
    for (
        lead_id,
        nome,
        sobrenome,
        email,
        cpf,
        telefone,
        evento_nome,
        cidade,
        estado,
        data_compra,
        data_criacao,
        data_nascimento,
        tipo_conversao,
        data_conversao_evento,
        data_conversao_criada,
        evento_convertido_id,
        evento_convertido_nome,
        evento_data_inicio_prevista,
        evento_data_fim_prevista,
        evento_cidade,
        evento_estado,
        tipo_evento_nome,
        evento_canonico_id,
        evento_canonico_nome,
        evento_canonico_data_inicio_prevista,
        evento_canonico_data_fim_prevista,
        evento_canonico_cidade,
        evento_canonico_estado,
        evento_canonico_tipo_id,
        tipo_evento_canonico_nome,
        evento_origem_id,
        evento_origem_nome,
        evento_origem_data_inicio_prevista,
        evento_origem_data_fim_prevista,
        evento_origem_cidade,
        evento_origem_estado,
        evento_origem_tipo_id,
        tipo_evento_origem_nome,
        rg,
        genero,
        is_cliente_bb,
        is_cliente_estilo,
        endereco_rua,
        endereco_numero,
        complemento,
        bairro,
        cep,
        fonte_origem,
        origem_lote,
        plataforma_origem,
    ) in rows:
        tipo_conversao_value = None
        if tipo_conversao is not None:
            tipo_conversao_value = (
                tipo_conversao.value if hasattr(tipo_conversao, "value") else str(tipo_conversao)
            )
        nome_completo = " ".join(
            part.strip()
            for part in [nome or "", sobrenome or ""]
            if part and part.strip()
        ) or None
        data_conv = data_conversao_evento or data_conversao_criada
        has_evento_convertido = evento_convertido_id is not None
        evento_origem_resolvido_nome = (
            evento_canonico_nome or evento_origem_nome or evento_nome
        )
        evento_origem_resolvido_inicio = (
            evento_canonico_data_inicio_prevista or evento_origem_data_inicio_prevista
        )
        evento_origem_resolvido_fim = (
            evento_canonico_data_fim_prevista or evento_origem_data_fim_prevista
        )
        evento_origem_resolvido_cidade = (
            evento_canonico_cidade or evento_origem_cidade
        )
        evento_origem_resolvido_estado = (
            evento_canonico_estado or evento_origem_estado
        )

        evento_data_export = (
            evento_data_inicio_prevista
            if has_evento_convertido
            else evento_origem_resolvido_inicio
        )
        evento_fim_export = (
            evento_data_fim_prevista
            if has_evento_convertido
            else evento_origem_resolvido_fim
        )
        local_evento = _format_local_evento_export(
            evento_cidade if has_evento_convertido else evento_origem_resolvido_cidade,
            evento_estado if has_evento_convertido else evento_origem_resolvido_estado,
        )
        tipo_evento_export = tipo_evento_nome
        if not has_evento_convertido:
            if tipo_evento_canonico_nome:
                tipo_evento_export = tipo_evento_canonico_nome
            elif evento_canonico_id is not None and evento_canonico_tipo_id is None:
                tipo_evento_export = TIPO_EVENTO_PADRAO
            elif tipo_evento_origem_nome:
                tipo_evento_export = tipo_evento_origem_nome
            elif evento_origem_id is not None and evento_origem_tipo_id is None:
                tipo_evento_export = TIPO_EVENTO_PADRAO
        ref_date = _ref_date_for_age(evento_data_export, data_conv if has_evento_convertido else None)
        idade_val = _idade_na_data_ref(data_nascimento, ref_date)
        faixa_val = _faixa_etaria_export_data2(idade_val)
        origem_export = _format_origem_lead_export(fonte_origem, origem_lote, plataforma_origem)
        items.append(
            LeadListItemRead(
                id=int(lead_id),
                nome=nome_completo,
                sobrenome=sobrenome,
                email=email,
                cpf=cpf,
                telefone=telefone,
                evento_nome=evento_origem_resolvido_nome,
                cidade=cidade,
                estado=estado,
                data_compra=data_compra,
                data_criacao=data_criacao,
                evento_convertido_id=int(evento_convertido_id) if evento_convertido_id is not None else None,
                evento_convertido_nome=evento_convertido_nome,
                tipo_conversao=tipo_conversao_value,
                data_conversao=data_conv,
                rg=rg,
                genero=genero,
                is_cliente_bb=is_cliente_bb,
                is_cliente_estilo=is_cliente_estilo,
                logradouro=endereco_rua,
                numero=endereco_numero,
                complemento=complemento,
                bairro=bairro,
                cep=cep,
                data_nascimento=data_nascimento,
                data_evento=_format_data_evento_export(
                    evento_data_export,
                    data_conv if has_evento_convertido else None,
                ),
                soma_de_ano_evento=_ano_evento_export(
                    evento_data_export,
                    data_conv if has_evento_convertido else None,
                ),
                tipo_evento=tipo_evento_export,
                local_evento=local_evento,
                faixa_etaria=faixa_val,
                soma_de_idade=idade_val,
                origem=origem_export or None,
                evento_inicio_prevista=evento_data_export,
                evento_fim_prevista=evento_fim_export,
            )
        )

    return LeadListResponse(
        page=params.page,
        page_size=params.page_size,
        total=total,
        items=items,
    )


def listar_leads(
    params: LeadListQuery = Depends(),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return listar_leads_impl(session, current_user, params, compute_total=True)


LEADS_LIST_EXPORT_PAGE_SIZE = 500


LEADS_LIST_EXPORT_HEADERS = [
    "nome",
    "cpf",
    "data_nascimento",
    "email",
    "telefone",
    "origem",
    "evento",
    "local",
    "data_evento",
]


def _get_lead_or_404(*, session: Session, lead_id: int) -> Lead:
    lead = session.get(Lead, lead_id)
    if not lead:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="LEAD_NOT_FOUND",
            message="Lead nao encontrado",
        )
    return lead


def _format_origem_lead_export(
    fonte_origem: str | None,
    origem_lote: str | None,
    plataforma_origem: str | None,
) -> str:
    """Rotulo para CSV: Proponente | Ativação (prioriza metadados do lote, depois fonte do lead)."""
    for raw in (origem_lote, fonte_origem, plataforma_origem):
        if not raw:
            continue
        s = raw.strip().lower()
        if s in ("ativacao", "ativação") or "ativacao" in s or "ativação" in s:
            return "Ativação"
        if s == "proponente" or "proponente" in s:
            return "Proponente"
    return ""


def _format_leads_list_export_date(value: date | datetime | str | None) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        head = value.split(" ", 1)[0]
        try:
            parsed = date.fromisoformat(head)
        except ValueError:
            return value
        return f"{parsed.month}/{parsed.day}/{parsed.year}"
    if isinstance(value, datetime):
        value = value.date()
    return f"{value.month}/{value.day}/{value.year}"


def _resolve_leads_list_export_event(item: LeadListItemRead) -> str:
    return item.evento_convertido_nome or item.evento_nome or ""


def _build_leads_list_export_cells(item: LeadListItemRead) -> list[str]:
    return [
        item.nome or "",
        item.cpf or "",
        _format_leads_list_export_date(item.data_nascimento),
        item.email or "",
        item.telefone or "",
        item.origem or "",
        _resolve_leads_list_export_event(item),
        item.local_evento or "",
        _format_leads_list_export_date(item.data_evento),
    ]


def _iter_leads_list_export_csv(
    session: Session,
    current_user: Usuario,
    first_page: LeadListResponse,
    *,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    evento_id: int | None = None,
    search: str | None = None,
    origem: str | None = None,
):
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer, delimiter=",", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")

    csv_buffer.write("\ufeff")
    writer.writerow(LEADS_LIST_EXPORT_HEADERS)
    for item in first_page.items:
        writer.writerow(_build_leads_list_export_cells(item))
    yield csv_buffer.getvalue().encode("utf-8")
    csv_buffer.seek(0)
    csv_buffer.truncate(0)

    page = 2
    while True:
        result = listar_leads_impl(
            session,
            current_user,
            LeadListQuery(
                page=page,
                page_size=LEADS_LIST_EXPORT_PAGE_SIZE,
                long_running=True,
                data_inicio=data_inicio,
                data_fim=data_fim,
                evento_id=evento_id,
                search=search,
                origem=origem,
            ),
            compute_total=False,
        )

        for item in result.items:
            writer.writerow(_build_leads_list_export_cells(item))

        chunk = csv_buffer.getvalue()
        if chunk:
            yield chunk.encode("utf-8")
        csv_buffer.seek(0)
        csv_buffer.truncate(0)

        if len(result.items) < LEADS_LIST_EXPORT_PAGE_SIZE:
            break
        page += 1


@router.get("/export/csv")
@router.get("/export/csv/")
def exportar_leads_csv(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    evento_id: int | None = Query(None, ge=1),
    search: str | None = Query(None, min_length=2, max_length=120),
    origem: str | None = Query(None, pattern="^(proponente|ativacao)$"),
):
    first_page = listar_leads_impl(
        session,
        current_user,
        LeadListQuery(
            page=1,
            page_size=LEADS_LIST_EXPORT_PAGE_SIZE,
            long_running=True,
            data_inicio=data_inicio,
            data_fim=data_fim,
            evento_id=evento_id,
            search=search,
            origem=origem,
        ),
        compute_total=False,
    )
    if not first_page.items:
        return FastAPIResponse(status_code=204)

    filename = f"leads-{date.today().isoformat()}.csv"
    return StreamingResponse(
        _iter_leads_list_export_csv(
            session,
            current_user,
            first_page,
            data_inicio=data_inicio,
            data_fim=data_fim,
            evento_id=evento_id,
            search=search,
            origem=origem,
        ),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{lead_id}/conversoes", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
@router.post("/{lead_id}/conversoes/", response_model=LeadConversaoRead, status_code=status.HTTP_201_CREATED)
def criar_conversao(
    lead_id: int,
    payload: LeadConversaoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    lead = _get_lead_or_404(session=session, lead_id=lead_id)

    conversao = LeadConversao(
        lead_id=lead.id,
        tipo=payload.tipo,
        acao_nome=payload.acao_nome,
        fonte_origem=payload.fonte_origem,
        evento_id=payload.evento_id,
        data_conversao_evento=payload.data_conversao_evento,
        created_at=now_utc(),
    )
    session.add(conversao)
    session.commit()
    session.refresh(conversao)
    return LeadConversaoRead.model_validate(conversao, from_attributes=True)


@router.get("/{lead_id}/conversoes", response_model=list[LeadConversaoRead])
@router.get("/{lead_id}/conversoes/", response_model=list[LeadConversaoRead])
def listar_conversoes(
    lead_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    _get_lead_or_404(session=session, lead_id=lead_id)
    conversoes = session.exec(
        select(LeadConversao).where(LeadConversao.lead_id == lead_id).order_by(LeadConversao.created_at.desc())
    ).all()
    return [LeadConversaoRead.model_validate(item, from_attributes=True) for item in conversoes]
