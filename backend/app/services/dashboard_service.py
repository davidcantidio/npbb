"""Servicos de analise etaria para endpoints de dashboard."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from statistics import median

from sqlalchemy import func as sa_func
from sqlmodel import Session, select

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Ativacao, AtivacaoLead, Evento, Lead, Usuario, UsuarioTipo, now_utc
from app.schemas.dashboard import (
    AgeAnalysisQuery,
    AgeAnalysisFilters,
    AgeAnalysisResponse,
    AgeBreakdown,
    ConsolidadoAgeAnalysis,
    EventoAgeAnalysis,
    FaixaEtariaMetrics,
    TopEventoAgeAnalysis,
)
from app.utils.http_errors import raise_http_error

DEFAULT_BB_COVERAGE_THRESHOLD_PCT = 80.0


@dataclass(slots=True)
class LeadEventFact:
    evento_id: int
    evento_nome: str
    cidade: str
    estado: str
    lead_id: int
    data_nascimento: date | None
    is_cliente_bb: bool | None


@dataclass(slots=True)
class EventAccumulator:
    evento_id: int
    evento_nome: str
    cidade: str
    estado: str
    base_leads: int = 0
    bb_covered_volume: int = 0
    bb_clients_volume: int = 0
    base_com_idade: int = 0
    faixa_18_25_volume: int = 0
    faixa_26_40_volume: int = 0
    fora_18_40_volume: int = 0
    sem_info_volume: int = 0


def _read_bb_coverage_threshold_pct() -> float:
    raw = os.getenv("DASHBOARD_BB_COVERAGE_THRESHOLD_PCT", "").strip()
    if not raw:
        return DEFAULT_BB_COVERAGE_THRESHOLD_PCT
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_BB_COVERAGE_THRESHOLD_PCT
    return min(max(value, 0.0), 100.0)


def calculate_age(data_nascimento: date, reference_date: date | None = None) -> int:
    current_date = reference_date or date.today()
    years = current_date.year - data_nascimento.year
    if (current_date.month, current_date.day) < (data_nascimento.month, data_nascimento.day):
        years -= 1
    return years


def classify_age_range(age: int) -> str:
    if 18 <= age <= 25:
        return "faixa_18_25"
    if 26 <= age <= 40:
        return "faixa_26_40"
    return "fora_18_40"


def _safe_pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


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


def _build_filters(params: AgeAnalysisQuery, current_user: Usuario) -> list:
    filters: list = []
    _apply_visibility(filters, current_user)

    if params.evento_id is not None:
        filters.append(Evento.id == params.evento_id)
    if params.data_inicio is not None:
        start_at, _ = _day_window_bounds(params.data_inicio)
        filters.append(Lead.data_criacao >= start_at)
    if params.data_fim is not None:
        _, end_exclusive = _day_window_bounds(params.data_fim)
        filters.append(Lead.data_criacao < end_exclusive)
    return filters


def _from_clause():
    return (
        Lead.__table__.join(AtivacaoLead, AtivacaoLead.lead_id == Lead.id)
        .join(Ativacao, Ativacao.id == AtivacaoLead.ativacao_id)
        .join(Evento, Evento.id == Ativacao.evento_id)
    )


def _from_clause_batch():
    """Lead via pipeline (LeadBatch) -> Evento. Usado para leads importados sem AtivacaoLead."""
    return (
        Lead.__table__.join(LeadBatch, Lead.batch_id == LeadBatch.id)
        .join(Evento, Evento.id == LeadBatch.evento_id)
    )


_GOLD_PIPELINE_STATUSES = {PipelineStatus.PASS, PipelineStatus.PASS_WITH_WARNINGS}


def _load_lead_event_facts(session: Session, filters: list) -> list[LeadEventFact]:
    rows = session.exec(
        select(
            Evento.id,
            Evento.nome,
            Evento.cidade,
            Evento.estado,
            Lead.id,
            Lead.data_nascimento,
            Lead.is_cliente_bb,
        )
        .select_from(_from_clause())
        .where(*filters)
        .distinct()
    ).all()

    facts: list[LeadEventFact] = []
    for row in rows:
        (
            evento_id,
            evento_nome,
            cidade,
            estado,
            lead_id,
            data_nascimento,
            is_cliente_bb,
        ) = row
        facts.append(
            LeadEventFact(
                evento_id=int(evento_id),
                evento_nome=_safe_text(evento_nome),
                cidade=_safe_text(cidade),
                estado=_safe_text(estado),
                lead_id=int(lead_id),
                data_nascimento=data_nascimento,
                is_cliente_bb=is_cliente_bb,
            )
        )
    return facts


def _load_lead_event_facts_via_batch(
    session: Session, filters: list
) -> list[LeadEventFact]:
    """Carrega leads vinculados a eventos via LeadBatch (importacao pipeline)."""
    batch_filters = list(filters)
    batch_filters.append(Lead.batch_id.is_not(None))
    batch_filters.append(LeadBatch.evento_id.is_not(None))
    batch_filters.append(LeadBatch.stage == BatchStage.GOLD)
    batch_filters.append(LeadBatch.pipeline_status.in_(_GOLD_PIPELINE_STATUSES))

    rows = session.exec(
        select(
            Evento.id,
            Evento.nome,
            Evento.cidade,
            Evento.estado,
            Lead.id,
            Lead.data_nascimento,
            Lead.is_cliente_bb,
        )
        .select_from(_from_clause_batch())
        .where(*batch_filters)
        .distinct()
    ).all()

    facts: list[LeadEventFact] = []
    for row in rows:
        (
            evento_id,
            evento_nome,
            cidade,
            estado,
            lead_id,
            data_nascimento,
            is_cliente_bb,
        ) = row
        facts.append(
            LeadEventFact(
                evento_id=int(evento_id),
                evento_nome=_safe_text(evento_nome),
                cidade=_safe_text(cidade),
                estado=_safe_text(estado),
                lead_id=int(lead_id),
                data_nascimento=data_nascimento,
                is_cliente_bb=is_cliente_bb,
            )
        )
    return facts


def _from_clause_evento_nome():
    """Lead via evento_nome match (ETL import). Usado quando Lead.evento_nome = Evento.nome."""
    return Lead.__table__.join(
        Evento,
        sa_func.lower(sa_func.trim(Lead.evento_nome)) == sa_func.lower(sa_func.trim(Evento.nome)),
    )


def _load_lead_event_facts_via_evento_nome(
    session: Session, filters: list
) -> list[LeadEventFact]:
    """Carrega leads vinculados a eventos via Lead.evento_nome = Evento.nome (import ETL)."""
    nome_filters = list(filters)
    nome_filters.append(Lead.evento_nome.is_not(None))
    nome_filters.append(sa_func.trim(Lead.evento_nome) != "")

    rows = session.exec(
        select(
            Evento.id,
            Evento.nome,
            Evento.cidade,
            Evento.estado,
            Lead.id,
            Lead.data_nascimento,
            Lead.is_cliente_bb,
        )
        .select_from(_from_clause_evento_nome())
        .where(*nome_filters)
        .distinct()
    ).all()

    facts: list[LeadEventFact] = []
    for row in rows:
        (
            evento_id,
            evento_nome,
            cidade,
            estado,
            lead_id,
            data_nascimento,
            is_cliente_bb,
        ) = row
        facts.append(
            LeadEventFact(
                evento_id=int(evento_id),
                evento_nome=_safe_text(evento_nome),
                cidade=_safe_text(cidade),
                estado=_safe_text(estado),
                lead_id=int(lead_id),
                data_nascimento=data_nascimento,
                is_cliente_bb=is_cliente_bb,
            )
        )
    return facts


def _merge_and_dedupe_facts(
    facts_ativacao: list[LeadEventFact],
    facts_batch: list[LeadEventFact],
    facts_evento_nome: list[LeadEventFact],
) -> list[LeadEventFact]:
    """Uniao de facts deduplicando por (lead_id, evento_id)."""
    seen: set[tuple[int, int]] = set()
    result: list[LeadEventFact] = []
    for fact in facts_ativacao + facts_batch + facts_evento_nome:
        key = (fact.lead_id, fact.evento_id)
        if key in seen:
            continue
        seen.add(key)
        result.append(fact)
    return result


def _day_window_bounds(value: date) -> tuple[datetime, datetime]:
    start = datetime.combine(value, time.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _accumulate_link_metrics(
    event_accumulator: EventAccumulator,
    consolidated_accumulator: EventAccumulator,
    fact: LeadEventFact,
    reference_date: date,
) -> None:
    # Regra de produto: consolidado conta por vinculo evento<->lead, sem deduplicar por lead_id.
    _consume_fact(event_accumulator, fact, reference_date=reference_date)
    _consume_fact(consolidated_accumulator, fact, reference_date=reference_date)


def _accumulator_from_fact(fact: LeadEventFact) -> EventAccumulator:
    return EventAccumulator(
        evento_id=fact.evento_id,
        evento_nome=fact.evento_nome,
        cidade=fact.cidade,
        estado=fact.estado,
    )


def _consume_fact(accumulator: EventAccumulator, fact: LeadEventFact, reference_date: date) -> None:
    accumulator.base_leads += 1

    if fact.is_cliente_bb is not None:
        accumulator.bb_covered_volume += 1
        if fact.is_cliente_bb:
            accumulator.bb_clients_volume += 1

    if fact.data_nascimento is None:
        accumulator.sem_info_volume += 1
        return

    age = calculate_age(fact.data_nascimento, reference_date=reference_date)
    faixa = classify_age_range(age)
    accumulator.base_com_idade += 1

    if faixa == "faixa_18_25":
        accumulator.faixa_18_25_volume += 1
        return
    if faixa == "faixa_26_40":
        accumulator.faixa_26_40_volume += 1
        return
    accumulator.fora_18_40_volume += 1


def _build_breakdown(accumulator: EventAccumulator) -> AgeBreakdown:
    return AgeBreakdown(
        faixa_18_25=FaixaEtariaMetrics(
            volume=accumulator.faixa_18_25_volume,
            pct=_safe_pct(accumulator.faixa_18_25_volume, accumulator.base_com_idade),
        ),
        faixa_26_40=FaixaEtariaMetrics(
            volume=accumulator.faixa_26_40_volume,
            pct=_safe_pct(accumulator.faixa_26_40_volume, accumulator.base_com_idade),
        ),
        fora_18_40=FaixaEtariaMetrics(
            volume=accumulator.fora_18_40_volume,
            pct=_safe_pct(accumulator.fora_18_40_volume, accumulator.base_com_idade),
        ),
        sem_info_volume=accumulator.sem_info_volume,
        sem_info_pct_da_base=_safe_pct(accumulator.sem_info_volume, accumulator.base_leads),
    )


def _resolve_dominant_range(accumulator: EventAccumulator) -> str:
    ranking = [
        ("faixa_18_25", accumulator.faixa_18_25_volume),
        ("faixa_26_40", accumulator.faixa_26_40_volume),
        ("fora_18_40", accumulator.fora_18_40_volume),
        ("sem_info", accumulator.sem_info_volume),
    ]
    return max(ranking, key=lambda item: item[1])[0]


def _resolve_bb_metrics(
    accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> tuple[float, int | None, float | None]:
    cobertura_bb_pct = _safe_pct(accumulator.bb_covered_volume, accumulator.base_leads)
    if cobertura_bb_pct < bb_coverage_threshold_pct:
        return cobertura_bb_pct, None, None

    # Contrato atual do endpoint: percentual BB sobre a base total do evento/consolidado.
    return (
        cobertura_bb_pct,
        accumulator.bb_clients_volume,
        _safe_pct(accumulator.bb_clients_volume, accumulator.base_leads),
    )


def _finalize_event_analysis(
    accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> EventoAgeAnalysis:
    cobertura_bb_pct, clientes_bb_volume, clientes_bb_pct = _resolve_bb_metrics(
        accumulator,
        bb_coverage_threshold_pct=bb_coverage_threshold_pct,
    )
    return EventoAgeAnalysis(
        evento_id=accumulator.evento_id,
        evento_nome=accumulator.evento_nome,
        cidade=accumulator.cidade,
        estado=accumulator.estado,
        base_leads=accumulator.base_leads,
        clientes_bb_volume=clientes_bb_volume,
        clientes_bb_pct=clientes_bb_pct,
        cobertura_bb_pct=cobertura_bb_pct,
        faixas=_build_breakdown(accumulator),
        faixa_dominante=_resolve_dominant_range(accumulator),
    )


def _build_consolidated_analysis(
    event_analyses: list[EventoAgeAnalysis],
    consolidated_accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> ConsolidadoAgeAnalysis:
    cobertura_bb_pct, clientes_bb_volume, clientes_bb_pct = _resolve_bb_metrics(
        consolidated_accumulator,
        bb_coverage_threshold_pct=bb_coverage_threshold_pct,
    )

    ordered_by_volume = sorted(
        event_analyses,
        key=lambda item: (-item.base_leads, item.evento_nome, item.evento_id),
    )
    top_eventos = [
        TopEventoAgeAnalysis(
            evento_id=item.evento_id,
            evento_nome=item.evento_nome,
            base_leads=item.base_leads,
            faixa_dominante=item.faixa_dominante,
        )
        for item in ordered_by_volume[:3]
    ]
    volumes = [item.base_leads for item in ordered_by_volume]

    return ConsolidadoAgeAnalysis(
        base_total=consolidated_accumulator.base_leads,
        clientes_bb_volume=clientes_bb_volume,
        clientes_bb_pct=clientes_bb_pct,
        cobertura_bb_pct=cobertura_bb_pct,
        faixas=_build_breakdown(consolidated_accumulator),
        top_eventos=top_eventos,
        media_por_evento=round(sum(volumes) / len(volumes), 2) if volumes else 0.0,
        mediana_por_evento=round(float(median(volumes)), 2) if volumes else 0.0,
        concentracao_top3_pct=_safe_pct(
            sum(item.base_leads for item in top_eventos),
            consolidated_accumulator.base_leads,
        ),
    )


def build_age_analysis(
    session: Session,
    params: AgeAnalysisQuery,
    current_user: Usuario,
) -> AgeAnalysisResponse:
    filters = _build_filters(params, current_user)
    facts_ativacao = _load_lead_event_facts(session, filters)
    facts_batch = _load_lead_event_facts_via_batch(session, filters)
    facts_evento_nome = _load_lead_event_facts_via_evento_nome(session, filters)
    link_facts = _merge_and_dedupe_facts(facts_ativacao, facts_batch, facts_evento_nome)
    reference_date = date.today()
    bb_coverage_threshold_pct = _read_bb_coverage_threshold_pct()

    accumulators: dict[int, EventAccumulator] = {}
    consolidated_accumulator = EventAccumulator(
        evento_id=0,
        evento_nome="consolidado",
        cidade="",
        estado="",
    )

    for fact in link_facts:
        event_accumulator = accumulators.setdefault(
            fact.evento_id,
            _accumulator_from_fact(fact),
        )
        _accumulate_link_metrics(
            event_accumulator,
            consolidated_accumulator,
            fact,
            reference_date=reference_date,
        )

    event_analyses = [
        _finalize_event_analysis(
            accumulator,
            bb_coverage_threshold_pct=bb_coverage_threshold_pct,
        )
        for accumulator in accumulators.values()
    ]
    event_analyses.sort(key=lambda item: (-item.base_leads, item.evento_nome, item.evento_id))

    return AgeAnalysisResponse(
        generated_at=now_utc(),
        filters=AgeAnalysisFilters(
            data_inicio=params.data_inicio,
            data_fim=params.data_fim,
            evento_id=params.evento_id,
        ),
        por_evento=event_analyses,
        consolidado=_build_consolidated_analysis(
            event_analyses,
            consolidated_accumulator=consolidated_accumulator,
            bb_coverage_threshold_pct=bb_coverage_threshold_pct,
        ),
    )
