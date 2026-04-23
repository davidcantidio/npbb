"""Servicos de analise etaria para endpoints de dashboard."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta, timezone
from statistics import median

from sqlalchemy import func as sa_func
from sqlmodel import Session, select

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus
from app.models.models import Evento, Lead, LeadEvento, Usuario, UsuarioTipo, now_utc
from app.models.lead_public_models import LeadEventoSourceKind, TipoLead
from app.schemas.dashboard import (
    AgeAnalysisQuery,
    AgeAnalysisFilters,
    AgeAnalysisInsights,
    AgeAnalysisResponse,
    AgeBreakdown,
    CompletenessMetrics,
    ConfiancaConsolidado,
    ConsolidadoAgeAnalysis,
    EventoAgeAnalysis,
    FaixaEtariaMetrics,
    LineageMixRow,
    OrigemQualidadeRow,
    TopEventoAgeAnalysis,
)
from app.services.lead_event_service import normalize_event_name
from app.utils.http_errors import raise_http_error

DEFAULT_BB_COVERAGE_THRESHOLD_PCT = 80.0
DEFAULT_EVENT_NAME_BACKFILL_ENABLED = True

_SOURCE_KIND_LABELS: dict[str, str] = {
    LeadEventoSourceKind.ACTIVATION.value: "Ativacao (captacao)",
    LeadEventoSourceKind.EVENT_DIRECT.value: "Vinculo direto ao evento",
    LeadEventoSourceKind.LEAD_BATCH.value: "Importacao (pipeline)",
    LeadEventoSourceKind.EVENT_NAME_BACKFILL.value: "Correspondencia por nome do evento",
    LeadEventoSourceKind.MANUAL_RECONCILED.value: "Reconciliacao manual",
}


@dataclass(slots=True)
class LeadEventFact:
    evento_id: int
    evento_nome: str
    cidade: str
    estado: str
    lead_id: int
    data_nascimento: date | None
    is_cliente_bb: bool | None
    source_kind: LeadEventoSourceKind
    tipo_lead: TipoLead | None
    cpf: str | None
    nome: str | None
    sobrenome: str | None


@dataclass(slots=True)
class EventAccumulator:
    evento_id: int
    evento_nome: str
    cidade: str
    estado: str
    base_leads: int = 0
    leads_proponente: int = 0
    leads_ativacao: int = 0
    leads_canal_desconhecido: int = 0
    bb_covered_volume: int = 0
    bb_clients_volume: int = 0
    bb_nao_cliente_volume: int = 0
    bb_indefinido_volume: int = 0
    base_com_idade: int = 0
    faixa_18_25_volume: int = 0
    faixa_26_40_volume: int = 0
    fora_18_40_volume: int = 0
    sem_info_volume: int = 0


@dataclass
class _QualityAccumulator:
    base: int = 0
    sem_cpf: int = 0
    sem_nasc: int = 0
    sem_nome: int = 0

    def consume(self, fact: LeadEventFact) -> None:
        self.base += 1
        if _is_cpf_missing(fact.cpf):
            self.sem_cpf += 1
        if fact.data_nascimento is None:
            self.sem_nasc += 1
        if _is_nome_completo_missing(fact.nome, fact.sobrenome):
            self.sem_nome += 1


@dataclass(slots=True)
class _EventoNomeResolutionStats:
    enabled: bool
    candidate_volume: int = 0
    ambiguous_volume: int = 0
    missing_volume: int = 0


@dataclass(slots=True)
class _MergeStats:
    dedupe_candidate_volume: int
    event_name_candidate_volume: int
    ambiguous_event_name_volume: int
    event_name_missing_volume: int
    event_name_backfill_enabled: bool
    dedupe_suppressed_volume: int = 0


def _read_bb_coverage_threshold_pct() -> float:
    raw = os.getenv("DASHBOARD_BB_COVERAGE_THRESHOLD_PCT", "").strip()
    if not raw:
        return DEFAULT_BB_COVERAGE_THRESHOLD_PCT
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_BB_COVERAGE_THRESHOLD_PCT
    return min(max(value, 0.0), 100.0)


def _read_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if raw == "":
        return default
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


def _read_event_name_backfill_enabled() -> bool:
    return _read_bool_env(
        "DASHBOARD_ENABLE_EVENTO_NOME_BACKFILL",
        DEFAULT_EVENT_NAME_BACKFILL_ENABLED,
    )


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


def _build_event_filters(params: AgeAnalysisQuery, current_user: Usuario) -> list:
    filters: list = []
    _apply_visibility(filters, current_user)

    if params.evento_id is not None:
        filters.append(Evento.id == params.evento_id)
    return filters


def _build_lead_filters(params: AgeAnalysisQuery) -> list:
    filters: list = []
    if params.data_inicio is not None:
        start_at, _ = _day_window_bounds(params.data_inicio)
        filters.append(Lead.data_criacao >= start_at)
    if params.data_fim is not None:
        _, end_exclusive = _day_window_bounds(params.data_fim)
        filters.append(Lead.data_criacao < end_exclusive)
    return filters


def _build_filters(params: AgeAnalysisQuery, current_user: Usuario) -> list:
    return [
        *_build_event_filters(params, current_user),
        *_build_lead_filters(params),
    ]


def _from_clause():
    return (
        LeadEvento.__table__.join(Lead, Lead.id == LeadEvento.lead_id)
        .join(Evento, Evento.id == LeadEvento.evento_id)
    )


def _from_clause_batch():
    return (
        Lead.__table__.join(LeadBatch, Lead.batch_id == LeadBatch.id)
        .join(Evento, Evento.id == LeadBatch.evento_id)
    )


_GOLD_PIPELINE_STATUSES = {PipelineStatus.PASS, PipelineStatus.PASS_WITH_WARNINGS}


def _row_to_fact(
    row: tuple,
    *,
    source_kind: LeadEventoSourceKind,
    tipo_lead: TipoLead | None,
) -> LeadEventFact:
    (
        evento_id,
        evento_nome,
        cidade,
        estado,
        lead_id,
        data_nascimento,
        is_cliente_bb,
        cpf,
        nome,
        sobrenome,
        *_,
    ) = row
    return LeadEventFact(
        evento_id=int(evento_id),
        evento_nome=_safe_text(evento_nome),
        cidade=_safe_text(cidade),
        estado=_safe_text(estado),
        lead_id=int(lead_id),
        data_nascimento=data_nascimento,
        is_cliente_bb=is_cliente_bb,
        source_kind=source_kind,
        tipo_lead=tipo_lead,
        cpf=cpf,
        nome=nome,
        sobrenome=sobrenome,
    )


def _resolve_batch_tipo_lead(
    origem_lote: str | None,
    tipo_lead_proponente: str | None,
) -> TipoLead:
    if _safe_text(origem_lote).lower() == TipoLead.ATIVACAO.value:
        return TipoLead.ATIVACAO
    if _safe_text(tipo_lead_proponente).lower() == TipoLead.BILHETERIA.value:
        return TipoLead.BILHETERIA
    return TipoLead.ENTRADA_EVENTO


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
            Lead.cpf,
            Lead.nome,
            Lead.sobrenome,
            LeadEvento.source_kind,
            LeadEvento.tipo_lead,
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
            cpf,
            nome,
            sobrenome,
            source_kind,
            tipo_lead,
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
                source_kind=source_kind,
                tipo_lead=tipo_lead,
                cpf=cpf,
                nome=nome,
                sobrenome=sobrenome,
            )
        )
    return facts


def _load_lead_event_facts_via_batch(session: Session, filters: list) -> list[LeadEventFact]:
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
            Lead.cpf,
            Lead.nome,
            Lead.sobrenome,
            LeadBatch.origem_lote,
            LeadBatch.tipo_lead_proponente,
        )
        .select_from(_from_clause_batch())
        .where(*batch_filters)
        .distinct()
    ).all()

    facts: list[LeadEventFact] = []
    for row in rows:
        origem_lote = row[10]
        tipo_lead_proponente = row[11]
        facts.append(
            _row_to_fact(
                row,
                source_kind=LeadEventoSourceKind.LEAD_BATCH,
                tipo_lead=_resolve_batch_tipo_lead(origem_lote, tipo_lead_proponente),
            )
        )
    return facts


def _load_visible_events_by_normalized_name(
    session: Session,
    event_filters: list,
) -> dict[str, list[tuple[int, str, str, str]]]:
    rows = session.exec(
        select(Evento.id, Evento.nome, Evento.cidade, Evento.estado).where(*event_filters)
    ).all()
    indexed: dict[str, list[tuple[int, str, str, str]]] = defaultdict(list)
    for evento_id, evento_nome, cidade, estado in rows:
        normalized = normalize_event_name(_safe_text(evento_nome))
        if normalized is None:
            continue
        indexed[normalized].append(
            (
                int(evento_id),
                _safe_text(evento_nome),
                _safe_text(cidade),
                _safe_text(estado),
            )
        )
    return indexed


def _load_lead_event_facts_via_evento_nome(
    session: Session,
    *,
    lead_filters: list,
    event_filters: list,
    enabled: bool,
    filtered_evento_id: int | None = None,
) -> tuple[list[LeadEventFact], _EventoNomeResolutionStats]:
    stats = _EventoNomeResolutionStats(enabled=enabled)
    if not enabled:
        return [], stats
    if filtered_evento_id is not None:
        return [], stats

    indexed_events = _load_visible_events_by_normalized_name(session, event_filters)
    nome_filters = list(lead_filters)
    nome_filters.append(Lead.evento_nome.is_not(None))
    nome_filters.append(sa_func.trim(Lead.evento_nome) != "")

    rows = session.exec(
        select(
            Lead.id,
            Lead.evento_nome,
            Lead.data_nascimento,
            Lead.is_cliente_bb,
            Lead.cpf,
            Lead.nome,
            Lead.sobrenome,
        ).where(*nome_filters)
    ).all()

    facts: list[LeadEventFact] = []
    for lead_id, evento_nome, data_nascimento, is_cliente_bb, cpf, nome, sobrenome in rows:
        stats.candidate_volume += 1
        normalized = normalize_event_name(_safe_text(evento_nome))
        if normalized is None:
            stats.missing_volume += 1
            continue

        matches = indexed_events.get(normalized, [])
        if not matches:
            stats.missing_volume += 1
            continue
        if len(matches) > 1:
            stats.ambiguous_volume += 1
            continue

        evento_id, evento_nome_match, cidade, estado = matches[0]
        facts.append(
            LeadEventFact(
                evento_id=evento_id,
                evento_nome=evento_nome_match,
                cidade=cidade,
                estado=estado,
                lead_id=int(lead_id),
                data_nascimento=data_nascimento,
                is_cliente_bb=is_cliente_bb,
                source_kind=LeadEventoSourceKind.EVENT_NAME_BACKFILL,
                tipo_lead=TipoLead.ENTRADA_EVENTO,
                cpf=cpf,
                nome=nome,
                sobrenome=sobrenome,
            )
        )
    return facts, stats


def _merge_and_dedupe_facts(
    facts_primary: list[LeadEventFact],
    facts_batch: list[LeadEventFact],
    facts_evento_nome: list[LeadEventFact],
    evento_nome_stats: _EventoNomeResolutionStats,
) -> tuple[list[LeadEventFact], _MergeStats]:
    """Uniao de facts deduplicando por (lead_id, evento_id). Ordem: lead_evento, batch, nome."""
    seen: set[tuple[int, int]] = set()
    result: list[LeadEventFact] = []
    merge_stats = _MergeStats(
        dedupe_candidate_volume=len(facts_primary) + len(facts_batch) + len(facts_evento_nome),
        event_name_candidate_volume=evento_nome_stats.candidate_volume,
        ambiguous_event_name_volume=evento_nome_stats.ambiguous_volume,
        event_name_missing_volume=evento_nome_stats.missing_volume,
        event_name_backfill_enabled=evento_nome_stats.enabled,
    )
    for fact in facts_primary + facts_batch + facts_evento_nome:
        key = (fact.lead_id, fact.evento_id)
        if key in seen:
            merge_stats.dedupe_suppressed_volume += 1
            continue
        seen.add(key)
        result.append(fact)
    return result, merge_stats


def _day_window_bounds(value: date) -> tuple[datetime, datetime]:
    start = datetime.combine(value, dt_time.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _is_cpf_missing(cpf: str | None) -> bool:
    if cpf is None:
        return True
    return _safe_text(cpf) == ""


def _is_nome_completo_missing(nome: str | None, sobrenome: str | None) -> bool:
    return _safe_text(nome) == "" or _safe_text(sobrenome) == ""


def _consume_canal(accumulator: EventAccumulator, fact: LeadEventFact) -> None:
    if fact.tipo_lead == TipoLead.ATIVACAO:
        accumulator.leads_ativacao += 1
    elif fact.tipo_lead in (TipoLead.BILHETERIA, TipoLead.ENTRADA_EVENTO):
        accumulator.leads_proponente += 1
    else:
        accumulator.leads_canal_desconhecido += 1


def _accumulate_link_metrics(
    event_accumulator: EventAccumulator,
    consolidated_accumulator: EventAccumulator,
    fact: LeadEventFact,
    reference_date: date,
) -> None:
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
    _consume_canal(accumulator, fact)

    if fact.is_cliente_bb is None:
        accumulator.bb_indefinido_volume += 1
    else:
        accumulator.bb_covered_volume += 1
        if fact.is_cliente_bb:
            accumulator.bb_clients_volume += 1
        else:
            accumulator.bb_nao_cliente_volume += 1

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
    v18 = accumulator.faixa_18_25_volume
    v26 = accumulator.faixa_26_40_volume
    base_idade = accumulator.base_com_idade
    return AgeBreakdown(
        faixa_18_25=FaixaEtariaMetrics(
            volume=v18,
            pct=_safe_pct(v18, base_idade),
        ),
        faixa_26_40=FaixaEtariaMetrics(
            volume=v26,
            pct=_safe_pct(v26, base_idade),
        ),
        faixa_18_40=FaixaEtariaMetrics(
            volume=v18 + v26,
            pct=_safe_pct(v18 + v26, base_idade),
        ),
        fora_18_40=FaixaEtariaMetrics(
            volume=accumulator.fora_18_40_volume,
            pct=_safe_pct(accumulator.fora_18_40_volume, base_idade),
        ),
        sem_info_volume=accumulator.sem_info_volume,
        sem_info_pct_da_base=_safe_pct(accumulator.sem_info_volume, accumulator.base_leads),
    )


def _resolve_dominant_range(accumulator: EventAccumulator) -> tuple[str, str]:
    ranking = [
        ("faixa_18_25", accumulator.faixa_18_25_volume),
        ("faixa_26_40", accumulator.faixa_26_40_volume),
        ("fora_18_40", accumulator.fora_18_40_volume),
        ("sem_info", accumulator.sem_info_volume),
    ]
    highest = max(value for _, value in ranking)
    if highest <= 0:
        return "sem_info", "empty"
    leaders = [key for key, value in ranking if value == highest]
    return leaders[0], ("resolved" if len(leaders) == 1 else "tied")


def _cobertura_bb_pct(accumulator: EventAccumulator) -> float:
    return _safe_pct(accumulator.bb_covered_volume, accumulator.base_leads)


def _resolve_cliente_bb_public_metrics(
    accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> tuple[
    float,
    int | None,
    float | None,
    int | None,
    float | None,
]:
    """Retorna cobertura, (clientes vol, pct), (nao clientes vol, pct) — ultimos Nulos se abaixo do limiar."""
    cobertura_bb_pct = _cobertura_bb_pct(accumulator)
    if cobertura_bb_pct < bb_coverage_threshold_pct:
        return cobertura_bb_pct, None, None, None, None

    return (
        cobertura_bb_pct,
        accumulator.bb_clients_volume,
        _safe_pct(accumulator.bb_clients_volume, accumulator.base_leads),
        accumulator.bb_nao_cliente_volume,
        _safe_pct(accumulator.bb_nao_cliente_volume, accumulator.base_leads),
    )


def _finalize_event_analysis(
    accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> EventoAgeAnalysis:
    faixa_dominante, faixa_dominante_status = _resolve_dominant_range(accumulator)
    cobertura_bb_pct, clientes_bb_volume, clientes_bb_pct, nao_vol, nao_pct = (
        _resolve_cliente_bb_public_metrics(
            accumulator,
            bb_coverage_threshold_pct=bb_coverage_threshold_pct,
        )
    )
    return EventoAgeAnalysis(
        evento_id=accumulator.evento_id,
        evento_nome=accumulator.evento_nome,
        cidade=accumulator.cidade,
        estado=accumulator.estado,
        base_leads=accumulator.base_leads,
        base_com_idade_volume=accumulator.base_com_idade,
        base_bb_coberta_volume=accumulator.bb_covered_volume,
        leads_proponente=accumulator.leads_proponente,
        leads_ativacao=accumulator.leads_ativacao,
        leads_canal_desconhecido=accumulator.leads_canal_desconhecido,
        clientes_bb_volume=clientes_bb_volume,
        clientes_bb_pct=clientes_bb_pct,
        nao_clientes_bb_volume=nao_vol,
        nao_clientes_bb_pct=nao_pct,
        bb_indefinido_volume=accumulator.bb_indefinido_volume,
        cobertura_bb_pct=cobertura_bb_pct,
        faixas=_build_breakdown(accumulator),
        faixa_dominante=faixa_dominante,
        faixa_dominante_status=faixa_dominante_status,
    )


def _build_consolidated_analysis(
    event_analyses: list[EventoAgeAnalysis],
    consolidated_accumulator: EventAccumulator,
    bb_coverage_threshold_pct: float,
) -> ConsolidadoAgeAnalysis:
    _, faixa_dominante_status = _resolve_dominant_range(consolidated_accumulator)
    cobertura_bb_pct, clientes_bb_volume, clientes_bb_pct, nao_vol, nao_pct = (
        _resolve_cliente_bb_public_metrics(
            consolidated_accumulator,
            bb_coverage_threshold_pct=bb_coverage_threshold_pct,
        )
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
        base_com_idade_volume=consolidated_accumulator.base_com_idade,
        base_bb_coberta_volume=consolidated_accumulator.bb_covered_volume,
        leads_proponente=consolidated_accumulator.leads_proponente,
        leads_ativacao=consolidated_accumulator.leads_ativacao,
        leads_canal_desconhecido=consolidated_accumulator.leads_canal_desconhecido,
        clientes_bb_volume=clientes_bb_volume,
        clientes_bb_pct=clientes_bb_pct,
        nao_clientes_bb_volume=nao_vol,
        nao_clientes_bb_pct=nao_pct,
        bb_indefinido_volume=consolidated_accumulator.bb_indefinido_volume,
        cobertura_bb_pct=cobertura_bb_pct,
        faixas=_build_breakdown(consolidated_accumulator),
        top_eventos=top_eventos,
        media_por_evento=round(sum(volumes) / len(volumes), 2) if volumes else 0.0,
        mediana_por_evento=round(float(median(volumes)), 2) if volumes else 0.0,
        concentracao_top3_pct=_safe_pct(
            sum(item.base_leads for item in top_eventos),
            consolidated_accumulator.base_leads,
        ),
        faixa_dominante_status=faixa_dominante_status,
    )


def _quality_row_from_acc(kind: str, acc: _QualityAccumulator) -> OrigemQualidadeRow:
    b = acc.base
    return OrigemQualidadeRow(
        source_kind=kind,
        label=_SOURCE_KIND_LABELS.get(kind, kind),
        base_vinculos=b,
        sem_cpf_volume=acc.sem_cpf,
        sem_cpf_pct=_safe_pct(acc.sem_cpf, b),
        sem_data_nascimento_volume=acc.sem_nasc,
        sem_data_nascimento_pct=_safe_pct(acc.sem_nasc, b),
        sem_nome_completo_volume=acc.sem_nome,
        sem_nome_completo_pct=_safe_pct(acc.sem_nome, b),
    )


def _build_qualidade_por_origem(facts: list[LeadEventFact]) -> list[OrigemQualidadeRow]:
    by_kind: dict[str, _QualityAccumulator] = defaultdict(_QualityAccumulator)
    for fact in facts:
        key = fact.source_kind.value
        by_kind[key].consume(fact)

    rows = [_quality_row_from_acc(k, v) for k, v in by_kind.items() if v.base > 0]
    rows.sort(key=lambda r: (-r.base_vinculos, r.source_kind))
    return rows


def _build_qualidade_consolidado(facts: list[LeadEventFact]) -> CompletenessMetrics:
    acc = _QualityAccumulator()
    for fact in facts:
        acc.consume(fact)
    b = acc.base
    if b <= 0:
        return CompletenessMetrics(
            base_vinculos=0,
            sem_cpf_volume=0,
            sem_cpf_pct=0.0,
            sem_data_nascimento_volume=0,
            sem_data_nascimento_pct=0.0,
            sem_nome_completo_volume=0,
            sem_nome_completo_pct=0.0,
        )
    return CompletenessMetrics(
        base_vinculos=b,
        sem_cpf_volume=acc.sem_cpf,
        sem_cpf_pct=_safe_pct(acc.sem_cpf, b),
        sem_data_nascimento_volume=acc.sem_nasc,
        sem_data_nascimento_pct=_safe_pct(acc.sem_nasc, b),
        sem_nome_completo_volume=acc.sem_nome,
        sem_nome_completo_pct=_safe_pct(acc.sem_nome, b),
    )


def _build_lineage_mix(facts: list[LeadEventFact]) -> list[LineageMixRow]:
    total = len(facts)
    by_kind: dict[str, int] = defaultdict(int)
    for fact in facts:
        by_kind[fact.source_kind.value] += 1

    rows = [
        LineageMixRow(
            source_kind=kind,
            label=_SOURCE_KIND_LABELS.get(kind, kind),
            volume=volume,
            pct=_safe_pct(volume, total),
        )
        for kind, volume in by_kind.items()
    ]
    rows.sort(key=lambda row: (-row.volume, row.source_kind))
    return rows


def _build_confianca_consolidado(
    facts: list[LeadEventFact],
    consolidado: ConsolidadoAgeAnalysis,
    merge_stats: _MergeStats,
) -> ConfiancaConsolidado:
    return ConfiancaConsolidado(
        base_vinculos=len(facts),
        base_com_idade_volume=consolidado.base_com_idade_volume,
        base_bb_coberta_volume=consolidado.base_bb_coberta_volume,
        dedupe_candidate_volume=merge_stats.dedupe_candidate_volume,
        dedupe_suppressed_volume=merge_stats.dedupe_suppressed_volume,
        dedupe_suppressed_pct=_safe_pct(
            merge_stats.dedupe_suppressed_volume,
            merge_stats.dedupe_candidate_volume,
        ),
        event_name_candidate_volume=merge_stats.event_name_candidate_volume,
        ambiguous_event_name_volume=merge_stats.ambiguous_event_name_volume,
        ambiguous_event_name_pct=_safe_pct(
            merge_stats.ambiguous_event_name_volume,
            merge_stats.event_name_candidate_volume,
        ),
        event_name_missing_volume=merge_stats.event_name_missing_volume,
        event_name_missing_pct=_safe_pct(
            merge_stats.event_name_missing_volume,
            merge_stats.event_name_candidate_volume,
        ),
        evento_nome_backfill_habilitado=merge_stats.event_name_backfill_enabled,
        lineage_mix=_build_lineage_mix(facts),
    )


def _build_insights(
    consolidado: ConsolidadoAgeAnalysis,
    qualidade_rows: list[OrigemQualidadeRow],
    confianca: ConfiancaConsolidado,
    event_count: int,
    bb_threshold: float,
) -> AgeAnalysisInsights:
    resumo: list[str] = []
    alertas: list[str] = []
    flags: list[str] = []

    total = consolidado.base_total
    if total == 0:
        if not confianca.evento_nome_backfill_habilitado:
            flags.append("event_name_backfill_disabled")
            alertas.append(
                "Sem vinculos no filtro e fallback por nome do evento desabilitado."
            )
        elif confianca.ambiguous_event_name_volume > 0:
            flags.append("event_name_backfill_ambiguous")
            alertas.append(
                f"{confianca.ambiguous_event_name_volume} lead(s) com nome de evento ambiguo foram descartados antes da consolidacao."
            )
        elif confianca.event_name_missing_volume > 0:
            flags.append("event_name_backfill_missing")
            alertas.append(
                f"{confianca.event_name_missing_volume} lead(s) tinham nome de evento sem correspondencia valida."
            )
        return AgeAnalysisInsights(
            resumo=["Nenhum vinculo lead-evento encontrado para os filtros aplicados."],
            alertas=alertas,
            flags=flags,
        )

    resumo.append(
        f"Base consolidada de {total} vinculo(s) lead-evento em {event_count} evento(s)."
    )

    prop = consolidado.leads_proponente
    ativ = consolidado.leads_ativacao
    des = consolidado.leads_canal_desconhecido
    resumo.append(
        f"Distribuicao por canal: {ativ} ativacao, {prop} proponente"
        + (f", {des} sem classificacao de canal." if des else ".")
    )

    fx = consolidado.faixas
    resumo.append(
        f"Faixa 18-40 (com data de nascimento): {fx.faixa_18_40.volume} registros "
        f"({format(fx.faixa_18_40.pct, '.2f')}% da base com idade). "
        f"Fora de 18-40: {fx.fora_18_40.volume} ({format(fx.fora_18_40.pct, '.2f')}% da base com idade). "
        f"Sem data de nascimento: {fx.sem_info_volume} ({format(fx.sem_info_pct_da_base, '.2f')}% da base total)."
    )

    resumo.append(
        f"Denominadores: {consolidado.base_com_idade_volume} vinculo(s) com idade e "
        f"{consolidado.base_bb_coberta_volume} com cobertura BB."
    )

    if consolidado.cobertura_bb_pct < bb_threshold:
        flags.append("bb_coverage_low")
        alertas.append(
            f"Cobertura BB ({format(consolidado.cobertura_bb_pct, '.2f')}%) abaixo do limiar de "
            f"{format(bb_threshold, '.0f')}%; percentuais de cliente e nao cliente BB ficam ocultos."
        )
    elif consolidado.clientes_bb_volume is not None:
        resumo.append(
            f"Clientes BB: {consolidado.clientes_bb_volume} ({format(consolidado.clientes_bb_pct or 0, '.2f')}%). "
            f"Nao clientes BB: {consolidado.nao_clientes_bb_volume} "
            f"({format(consolidado.nao_clientes_bb_pct or 0, '.2f')}%). "
            f"Cruzamento pendente (BB indefinido): {consolidado.bb_indefinido_volume}."
        )

    if consolidado.faixa_dominante_status == "tied":
        flags.append("dominant_range_tied")
        alertas.append(
            "A faixa dominante consolidada esta empatada; trate esse resumo como indicio, nao como maioria clara."
        )

    if fx.sem_info_pct_da_base >= 20:
        flags.append("birthdate_coverage_low")
        alertas.append(
            f"Sem data de nascimento em {format(fx.sem_info_pct_da_base, '.2f')}% da base; a leitura etaria perde confiabilidade."
        )

    if consolidado.concentracao_top3_pct >= 70 and len(consolidado.top_eventos) >= 1:
        resumo.append(
            f"Concentracao: os tres maiores eventos concentram {format(consolidado.concentracao_top3_pct, '.2f')}% "
            "da base no filtro."
        )

    if confianca.dedupe_suppressed_volume > 0:
        flags.append("dedupe_suppressed")
        alertas.append(
            f"{confianca.dedupe_suppressed_volume} candidato(s) foram suprimidos por deduplicacao "
            f"({format(confianca.dedupe_suppressed_pct, '.2f')}% dos candidatos ao merge)."
        )

    if not confianca.evento_nome_backfill_habilitado:
        flags.append("event_name_backfill_disabled")
        alertas.append(
            "Fallback por nome do evento desabilitado; a base consolidada pode ficar menor, mas evita associacoes arriscadas."
        )
    elif confianca.ambiguous_event_name_volume > 0:
        flags.append("event_name_backfill_ambiguous")
        alertas.append(
            f"{confianca.ambiguous_event_name_volume} lead(s) com nome de evento ambiguo foram descartados "
            f"({format(confianca.ambiguous_event_name_pct, '.2f')}% dos candidatos por nome)."
        )

    if confianca.event_name_missing_volume > 0:
        flags.append("event_name_backfill_missing")

    for row in qualidade_rows:
        gaps: list[tuple[str, float]] = [
            ("CPF", row.sem_cpf_pct),
            ("data de nascimento", row.sem_data_nascimento_pct),
            ("nome completo", row.sem_nome_completo_pct),
        ]
        gaps.sort(key=lambda x: -x[1])
        worst = [g[0] for g in gaps if g[1] > 0][:2]
        if worst:
            resumo.append(
                f"Fonte '{row.label}' ({row.base_vinculos} vinculos): maiores lacunas em "
                f"{', '.join(worst)} (ver tabela de qualidade para percentuais)."
            )

    return AgeAnalysisInsights(resumo=resumo, alertas=alertas, flags=flags)


def build_age_analysis(
    session: Session,
    params: AgeAnalysisQuery,
    current_user: Usuario,
) -> AgeAnalysisResponse:
    event_filters = _build_event_filters(params, current_user)
    lead_filters = _build_lead_filters(params)
    filters = [*event_filters, *lead_filters]
    facts_le = _load_lead_event_facts(session, filters)
    facts_batch = _load_lead_event_facts_via_batch(session, filters)
    facts_nome, evento_nome_stats = _load_lead_event_facts_via_evento_nome(
        session,
        lead_filters=lead_filters,
        event_filters=event_filters,
        enabled=_read_event_name_backfill_enabled(),
        filtered_evento_id=params.evento_id,
    )
    link_facts, merge_stats = _merge_and_dedupe_facts(
        facts_le,
        facts_batch,
        facts_nome,
        evento_nome_stats,
    )

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

    consolidado = _build_consolidated_analysis(
        event_analyses,
        consolidated_accumulator=consolidated_accumulator,
        bb_coverage_threshold_pct=bb_coverage_threshold_pct,
    )

    qualidade_por_origem = _build_qualidade_por_origem(link_facts)
    qualidade_consolidado = _build_qualidade_consolidado(link_facts)
    confianca_consolidado = _build_confianca_consolidado(
        link_facts,
        consolidado,
        merge_stats,
    )
    insights = _build_insights(
        consolidado,
        qualidade_por_origem,
        confianca_consolidado,
        event_count=len(event_analyses),
        bb_threshold=bb_coverage_threshold_pct,
    )

    return AgeAnalysisResponse(
        generated_at=now_utc(),
        age_reference_date=reference_date,
        filters=AgeAnalysisFilters(
            data_inicio=params.data_inicio,
            data_fim=params.data_fim,
            evento_id=params.evento_id,
        ),
        por_evento=event_analyses,
        consolidado=consolidado,
        qualidade_consolidado=qualidade_consolidado,
        confianca_consolidado=confianca_consolidado,
        qualidade_por_origem=qualidade_por_origem,
        insights=insights,
    )
