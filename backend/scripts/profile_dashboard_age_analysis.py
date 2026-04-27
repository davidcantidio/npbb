"""Profiler e runner diagnostico da fase 1 do dashboard etario.

Executa `build_age_analysis` diretamente contra Postgres real, coleta:
- tempos por estagio Python
- tempos por query SQL
- volumes por origem e deduplicacao
- snapshots/deltas de pg_stat_statements
- EXPLAIN ANALYZE das familias de query
- ranking final de gargalos
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from contextvars import ContextVar
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import Session


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "auditoria" / "evidencias"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.models import Usuario, UsuarioTipo  # noqa: E402
from app.services import dashboard_service as ds  # noqa: E402
try:  # noqa: E402
    from scripts.capture_pg_stat_statements import (
        PgStatDeltaRow,
        build_engine as build_pg_engine,
        compute_pg_stat_delta,
        fetch_pg_stat_statements_rows,
        pg_stat_statements_installed,
        render_pg_stat_delta_markdown,
        render_pg_stat_markdown,
        serialize_deltas,
        serialize_rows,
    )
    from scripts.run_critical_explains import (
        DashboardAgeScenario,
        ExplainResult,
        build_dashboard_age_explain_specs,
        build_engine as build_explain_engine,
        render_dashboard_age_explains_markdown,
        resolve_dashboard_age_scenarios,
        run_explain_specs,
    )
except ModuleNotFoundError:  # noqa: E402
    from capture_pg_stat_statements import (
        PgStatDeltaRow,
        build_engine as build_pg_engine,
        compute_pg_stat_delta,
        fetch_pg_stat_statements_rows,
        pg_stat_statements_installed,
        render_pg_stat_delta_markdown,
        render_pg_stat_markdown,
        serialize_deltas,
        serialize_rows,
    )
    from run_critical_explains import (
        DashboardAgeScenario,
        ExplainResult,
        build_dashboard_age_explain_specs,
        build_engine as build_explain_engine,
        render_dashboard_age_explains_markdown,
        resolve_dashboard_age_scenarios,
        run_explain_specs,
    )


for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


SEVERE_EXPLAIN_FLAGS = frozenset({"seq_scan", "temp_blocks", "sort_spill", "heavy_buffer_read"})
LOAD_STAGES = frozenset(
    {
        "_load_lead_event_facts",
        "_load_lead_event_facts_via_batch",
        "_load_lead_event_facts_via_evento_nome",
    }
)
SQL_PUSH_STAGES = frozenset(
    {
        "_accumulate_link_metrics",
        "_finalize_event_analysis",
        "_build_consolidated_analysis",
    }
)
MULTI_PASS_STAGES = (
    "_build_qualidade_por_origem",
    "_build_qualidade_consolidado",
    "_build_confianca_consolidado",
    "_build_insights",
)


@dataclass(slots=True)
class StageAggregate:
    stage: str
    total_ms: float = 0.0
    sql_ms: float = 0.0
    calls: int = 0
    query_count: int = 0


@dataclass(slots=True)
class QueryAggregate:
    query_family: str
    total_ms: float = 0.0
    calls: int = 0
    max_ms: float = 0.0
    sample: str = ""


@dataclass(slots=True)
class RunMetrics:
    total_ms: float
    stage_stats: dict[str, StageAggregate]
    query_stats: dict[str, QueryAggregate]
    volumes: dict[str, Any]


@dataclass(slots=True)
class ScenarioSummary:
    slug: str
    description: str
    params: dict[str, Any]
    enabled: bool
    skip_reason: str | None
    warmups: int
    measured_runs: int
    total_ms: dict[str, float] = field(default_factory=dict)
    stage_breakdown: list[dict[str, Any]] = field(default_factory=list)
    query_breakdown: list[dict[str, Any]] = field(default_factory=list)
    volumes: dict[str, Any] = field(default_factory=dict)
    pg_stat_delta_top: list[dict[str, Any]] = field(default_factory=list)
    explain_flags: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class BottleneckRow:
    target: str
    impact: str
    pct_total: float
    cause: str
    next_action: str
    evidence: tuple[str, ...]


def _worker_url() -> str:
    value = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not value or value.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL Postgres para o diagnostico real.")
    return value


def _synthetic_npbb_user() -> Usuario:
    return Usuario(
        email="dashboard.age.profile@npbb.local",
        password_hash="diagnostic-only",
        tipo_usuario=UsuarioTipo.NPBB,
        ativo=True,
    )


def classify_dashboard_age_statement(statement: str) -> str:
    normalized = " ".join(statement.lower().split())
    if (
        "from lead_evento join lead on lead.id = lead_evento.lead_id join evento on evento.id = lead_evento.evento_id"
        in normalized
    ):
        return "_load_lead_event_facts.sql"
    if (
        "from lead join lead_batches on lead.batch_id = lead_batches.id join evento on evento.id = lead_batches.evento_id"
        in normalized
    ):
        return "_load_lead_event_facts_via_batch.sql"
    if (
        normalized.startswith("select evento.id, evento.nome, evento.cidade, evento.estado from evento")
        or "select evento.id, evento.nome, evento.cidade, evento.estado" in normalized
        and "from evento" in normalized
        and "lead_evento" not in normalized
    ):
        return "_load_visible_events_by_normalized_name.sql"
    if (
        "select lead.id, lead.evento_nome, lead.data_nascimento, lead.is_cliente_bb, lead.cpf, lead.nome, lead.sobrenome from lead"
        in normalized
    ):
        return "_load_lead_event_facts_via_evento_nome.sql"
    return "other.sql"


def classify_bottleneck_impact(
    pct_total: float,
    flags: set[str],
    *,
    multi_pass: bool = False,
) -> str:
    if pct_total > 40.0 or bool(flags & SEVERE_EXPLAIN_FLAGS):
        return "alto"
    if pct_total >= 15.0 or multi_pass:
        return "medio"
    return "baixo"


def _round_ms(value: float) -> float:
    return round(value, 3)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * weight


def _collapse_lineage_mix(volumes: dict[str, Any]) -> dict[str, int]:
    lineage = volumes.get("lineage_mix", {})
    return {str(key): int(value) for key, value in lineage.items()}


def _stage_extractors() -> dict[str, Callable[[Any], dict[str, Any]]]:
    def load_primary(result: Any) -> dict[str, Any]:
        return {"facts_primary": len(result)}

    def load_batch(result: Any) -> dict[str, Any]:
        return {"facts_batch": len(result)}

    def load_event_name(result: Any) -> dict[str, Any]:
        facts, stats = result
        return {
            "facts_event_name": len(facts),
            "event_name_candidate_volume": int(stats.candidate_volume),
            "event_name_ambiguous_volume": int(stats.ambiguous_volume),
            "event_name_missing_volume": int(stats.missing_volume),
        }

    def merge(result: Any) -> dict[str, Any]:
        facts, stats = result
        return {
            "facts_after_dedupe": len(facts),
            "dedupe_candidate_volume": int(stats.dedupe_candidate_volume),
            "dedupe_suppressed_volume": int(stats.dedupe_suppressed_volume),
        }

    return {
        "_load_lead_event_facts": load_primary,
        "_load_lead_event_facts_via_batch": load_batch,
        "_load_lead_event_facts_via_evento_nome": load_event_name,
        "_merge_and_dedupe_facts": merge,
    }


class DashboardAgeServiceProfiler:
    def __init__(self, bind: Any) -> None:
        self.bind = bind
        self._stage_var: ContextVar[str] = ContextVar("dashboard_age_stage", default="unattributed")
        self._stage_stats: dict[str, StageAggregate] = {}
        self._query_stats: dict[str, QueryAggregate] = {}
        self._volumes: dict[str, Any] = {}
        self._patched: list[tuple[str, Any]] = []

    def _before_cursor_execute(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        stack = conn.info.setdefault("dashboard_age_diag_stack", [])
        stack.append((time.perf_counter(), self._stage_var.get()))

    def _after_cursor_execute(
        self,
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        stack = conn.info.get("dashboard_age_diag_stack", [])
        if not stack:
            return
        started_at, stage_name = stack.pop()
        duration_ms = (time.perf_counter() - started_at) * 1000
        stage = self._stage_stats.setdefault(stage_name, StageAggregate(stage=stage_name))
        stage.sql_ms += duration_ms
        stage.query_count += 1
        family = classify_dashboard_age_statement(statement)
        query = self._query_stats.setdefault(family, QueryAggregate(query_family=family))
        query.total_ms += duration_ms
        query.calls += 1
        query.max_ms = max(query.max_ms, duration_ms)
        if not query.sample:
            query.sample = " ".join(str(statement).split())[:700]

    def _record_stage_duration(self, stage_name: str, duration_ms: float) -> None:
        stage = self._stage_stats.setdefault(stage_name, StageAggregate(stage=stage_name))
        stage.calls += 1
        stage.total_ms += duration_ms

    def _install_wrapper(
        self,
        name: str,
        extractor: Callable[[Any], dict[str, Any]] | None = None,
    ) -> None:
        original = getattr(ds, name)

        @wraps(original)
        def wrapped(*args, **kwargs):
            token = self._stage_var.set(name)
            started_at = time.perf_counter()
            try:
                result = original(*args, **kwargs)
                if extractor is not None:
                    self._volumes.update(extractor(result))
                return result
            finally:
                duration_ms = (time.perf_counter() - started_at) * 1000
                self._record_stage_duration(name, duration_ms)
                self._stage_var.reset(token)

        self._patched.append((name, original))
        setattr(ds, name, wrapped)

    def __enter__(self) -> "DashboardAgeServiceProfiler":
        event.listen(self.bind, "before_cursor_execute", self._before_cursor_execute)
        event.listen(self.bind, "after_cursor_execute", self._after_cursor_execute)
        for name, extractor in _stage_extractors().items():
            self._install_wrapper(name, extractor)
        for name in (
            "_accumulate_link_metrics",
            "_finalize_event_analysis",
            "_build_consolidated_analysis",
            "_build_qualidade_por_origem",
            "_build_qualidade_consolidado",
            "_build_confianca_consolidado",
            "_build_insights",
        ):
            self._install_wrapper(name)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        while self._patched:
            name, original = self._patched.pop()
            setattr(ds, name, original)
        event.remove(self.bind, "before_cursor_execute", self._before_cursor_execute)
        event.remove(self.bind, "after_cursor_execute", self._after_cursor_execute)

    def build_run_metrics(self, *, total_ms: float, response: Any) -> RunMetrics:
        stage_total = sum(stage.total_ms for stage in self._stage_stats.values())
        unattributed_ms = max(total_ms - stage_total, 0.0)
        if unattributed_ms > 0.001:
            stage = self._stage_stats.setdefault(
                "build_age_analysis_unattributed",
                StageAggregate(stage="build_age_analysis_unattributed"),
            )
            stage.calls += 1
            stage.total_ms += unattributed_ms

        volumes = dict(self._volumes)
        volumes.update(
            {
                "base_total": int(response.consolidado.base_total),
                "base_com_idade_volume": int(response.consolidado.base_com_idade_volume),
                "base_bb_coberta_volume": int(response.consolidado.base_bb_coberta_volume),
                "event_count": len(response.por_evento),
                "lineage_mix": {
                    row.source_kind: int(row.volume) for row in response.confianca_consolidado.lineage_mix
                },
            }
        )
        return RunMetrics(
            total_ms=total_ms,
            stage_stats={key: StageAggregate(**asdict(value)) for key, value in self._stage_stats.items()},
            query_stats={key: QueryAggregate(**asdict(value)) for key, value in self._query_stats.items()},
            volumes=volumes,
        )


def _profile_single_run(session: Session, scenario: DashboardAgeScenario) -> RunMetrics:
    bind = session.get_bind()
    profiler = DashboardAgeServiceProfiler(bind)
    current_user = _synthetic_npbb_user()
    with profiler:
        started_at = time.perf_counter()
        response = ds.build_age_analysis(session, scenario.params, current_user)
        total_ms = (time.perf_counter() - started_at) * 1000
    return profiler.build_run_metrics(total_ms=total_ms, response=response)


def _run_warmup(session: Session, scenario: DashboardAgeScenario) -> None:
    ds.build_age_analysis(session, scenario.params, _synthetic_npbb_user())


def _summarize_stage_breakdown(runs: list[RunMetrics]) -> list[dict[str, Any]]:
    stage_names = sorted({name for run in runs for name in run.stage_stats})
    total_mean_ms = mean(run.total_ms for run in runs) if runs else 0.0
    rows: list[dict[str, Any]] = []
    for stage_name in stage_names:
        total_values = [run.stage_stats.get(stage_name, StageAggregate(stage=stage_name)).total_ms for run in runs]
        sql_values = [run.stage_stats.get(stage_name, StageAggregate(stage=stage_name)).sql_ms for run in runs]
        call_values = [run.stage_stats.get(stage_name, StageAggregate(stage=stage_name)).calls for run in runs]
        query_values = [run.stage_stats.get(stage_name, StageAggregate(stage=stage_name)).query_count for run in runs]
        mean_ms = mean(total_values) if total_values else 0.0
        rows.append(
            {
                "stage": stage_name,
                "mean_ms": _round_ms(mean_ms),
                "pct_total": round((mean_ms / total_mean_ms) * 100, 2) if total_mean_ms > 0 else 0.0,
                "sql_mean_ms": _round_ms(mean(sql_values) if sql_values else 0.0),
                "calls_mean": round(mean(call_values), 2) if call_values else 0.0,
                "query_count_mean": round(mean(query_values), 2) if query_values else 0.0,
            }
        )
    rows.sort(key=lambda row: (-float(row["mean_ms"]), str(row["stage"])))
    return rows


def _summarize_query_breakdown(runs: list[RunMetrics]) -> list[dict[str, Any]]:
    family_names = sorted({name for run in runs for name in run.query_stats})
    rows: list[dict[str, Any]] = []
    for family_name in family_names:
        totals = [run.query_stats.get(family_name, QueryAggregate(query_family=family_name)).total_ms for run in runs]
        calls = [run.query_stats.get(family_name, QueryAggregate(query_family=family_name)).calls for run in runs]
        maxima = [run.query_stats.get(family_name, QueryAggregate(query_family=family_name)).max_ms for run in runs]
        sample = next(
            (
                run.query_stats[family_name].sample
                for run in runs
                if family_name in run.query_stats and run.query_stats[family_name].sample
            ),
            "",
        )
        rows.append(
            {
                "query_family": family_name,
                "mean_ms": _round_ms(mean(totals) if totals else 0.0),
                "calls_mean": round(mean(calls), 2) if calls else 0.0,
                "max_ms": _round_ms(max(maxima) if maxima else 0.0),
                "sample": sample,
            }
        )
    rows.sort(key=lambda row: (-float(row["mean_ms"]), str(row["query_family"])))
    return rows


def _summarize_totals(runs: list[RunMetrics]) -> dict[str, float]:
    totals = [run.total_ms for run in runs]
    if not totals:
        return {"min": 0.0, "p50": 0.0, "mean": 0.0, "p95": 0.0, "max": 0.0}
    return {
        "min": _round_ms(min(totals)),
        "p50": _round_ms(_percentile(totals, 0.50)),
        "mean": _round_ms(mean(totals)),
        "p95": _round_ms(_percentile(totals, 0.95)),
        "max": _round_ms(max(totals)),
    }


def _summarize_volumes(runs: list[RunMetrics]) -> dict[str, Any]:
    if not runs:
        return {}
    first = runs[0].volumes
    summary: dict[str, Any] = {
        "facts_primary": int(first.get("facts_primary", 0)),
        "facts_batch": int(first.get("facts_batch", 0)),
        "facts_event_name": int(first.get("facts_event_name", 0)),
        "facts_after_dedupe": int(first.get("facts_after_dedupe", 0)),
        "dedupe_candidate_volume": int(first.get("dedupe_candidate_volume", 0)),
        "dedupe_suppressed_volume": int(first.get("dedupe_suppressed_volume", 0)),
        "event_name_candidate_volume": int(first.get("event_name_candidate_volume", 0)),
        "event_name_ambiguous_volume": int(first.get("event_name_ambiguous_volume", 0)),
        "event_name_missing_volume": int(first.get("event_name_missing_volume", 0)),
        "base_total": int(first.get("base_total", 0)),
        "event_count": int(first.get("event_count", 0)),
        "lineage_mix": _collapse_lineage_mix(first),
    }
    summary["base_total_min"] = min(int(run.volumes.get("base_total", 0)) for run in runs)
    summary["base_total_max"] = max(int(run.volumes.get("base_total", 0)) for run in runs)
    return summary


def _summarize_scenario(
    scenario: DashboardAgeScenario,
    *,
    runs: list[RunMetrics],
    warmups: int,
    pg_stat_delta: list[PgStatDeltaRow],
    explains: list[ExplainResult],
) -> ScenarioSummary:
    explain_flags: dict[str, list[str]] = {}
    for explain in explains:
        explain_flags[explain.title] = list(explain.flags)
    return ScenarioSummary(
        slug=scenario.slug,
        description=scenario.description,
        params=scenario.params.model_dump(),
        enabled=scenario.enabled,
        skip_reason=scenario.skip_reason,
        warmups=warmups,
        measured_runs=len(runs),
        total_ms=_summarize_totals(runs),
        stage_breakdown=_summarize_stage_breakdown(runs),
        query_breakdown=_summarize_query_breakdown(runs),
        volumes=_summarize_volumes(runs),
        pg_stat_delta_top=serialize_deltas(pg_stat_delta[:10]),
        explain_flags=explain_flags,
    )


def _stage_pct_index(summaries: list[ScenarioSummary]) -> tuple[dict[str, float], float]:
    combined: dict[str, float] = defaultdict(float)
    combined_total = 0.0
    for summary in summaries:
        if not summary.enabled:
            continue
        summary_total = float(summary.total_ms.get("mean", 0.0))
        combined_total += summary_total
        for row in summary.stage_breakdown:
            combined[str(row["stage"])] += float(row["mean_ms"])
    return combined, combined_total


def _explain_flag_index(summaries: list[ScenarioSummary]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = defaultdict(set)
    for summary in summaries:
        for title, flags in summary.explain_flags.items():
            index[title].update(flags)
    return index


def _build_post_processing_row(stage_pct: dict[str, float], combined_total: float) -> BottleneckRow | None:
    total_ms = sum(stage_pct.get(stage, 0.0) for stage in MULTI_PASS_STAGES)
    if total_ms <= 0:
        return None
    pct_total = round((total_ms / combined_total) * 100, 2) if combined_total > 0 else 0.0
    impact = classify_bottleneck_impact(pct_total, set(), multi_pass=True)
    return BottleneckRow(
        target="post_processing_full_passes",
        impact=impact,
        pct_total=pct_total,
        cause="Mesma base `link_facts` reprocessada em passes separados de qualidade, confianca e insights.",
        next_action="remover recomputação Python" if impact != "baixo" else "não otimizar agora",
        evidence=(
            f"pct_total={pct_total:.2f}%",
            "functions="
            + ", ".join(MULTI_PASS_STAGES),
        ),
    )


def _infer_cause(stage: str, flags: set[str]) -> str:
    if flags & {"seq_scan", "heavy_buffer_read"}:
        return "Leitura ampla no Postgres para alimentar a etapa."
    if flags & {"temp_blocks", "sort_spill"}:
        return "Plano com uso de temporarios/spill durante a leitura."
    if stage == "_merge_and_dedupe_facts":
        return "Uniao de multiplas fontes seguida de deduplicacao em memoria."
    if stage in SQL_PUSH_STAGES:
        return "Agregacao principal mantida em Python sobre facts materializados."
    if stage in MULTI_PASS_STAGES:
        return "Reprocessamento completo da mesma base em uma etapa derivada."
    if stage in LOAD_STAGES:
        return "Carga de facts dominando o tempo total do endpoint."
    return "Custo observado sem sinal forte de I/O ou spill."


def _recommend_next_action(stage: str, impact: str, flags: set[str]) -> str:
    if impact == "baixo" and not flags:
        return "não otimizar agora"
    if stage == "_merge_and_dedupe_facts":
        return "fact table/materialização"
    if stage in MULTI_PASS_STAGES:
        return "remover recomputação Python"
    if stage in SQL_PUSH_STAGES:
        return "mover agregação para SQL"
    if stage == "_load_lead_event_facts_via_evento_nome":
        return "reduzir full scan" if impact != "baixo" else "não otimizar agora"
    if stage in LOAD_STAGES:
        return "novo índice" if flags & SEVERE_EXPLAIN_FLAGS else "reduzir full scan"
    return "não otimizar agora"


def _build_bottlenecks(summaries: list[ScenarioSummary]) -> list[BottleneckRow]:
    stage_pct, combined_total = _stage_pct_index(summaries)
    flag_index = _explain_flag_index(summaries)
    rows: list[BottleneckRow] = []
    for stage, total_ms in stage_pct.items():
        pct_total = round((total_ms / combined_total) * 100, 2) if combined_total > 0 else 0.0
        flags = set(flag_index.get(stage, set()))
        multi_pass = stage in MULTI_PASS_STAGES
        impact = classify_bottleneck_impact(pct_total, flags, multi_pass=multi_pass)
        rows.append(
            BottleneckRow(
                target=stage,
                impact=impact,
                pct_total=pct_total,
                cause=_infer_cause(stage, flags),
                next_action=_recommend_next_action(stage, impact, flags),
                evidence=(
                    f"pct_total={pct_total:.2f}%",
                    f"flags={','.join(sorted(flags)) or 'none'}",
                ),
            )
        )

    post_processing = _build_post_processing_row(stage_pct, combined_total)
    if post_processing is not None:
        rows.append(post_processing)

    rows.sort(
        key=lambda row: (
            {"alto": 0, "medio": 1, "baixo": 2}[row.impact],
            -row.pct_total,
            row.target,
        )
    )
    return rows


def _render_summary_markdown(
    *,
    label: str,
    summaries: list[ScenarioSummary],
    bottlenecks: list[BottleneckRow],
    pg_stat_available: bool,
    explain_blocked: bool,
) -> str:
    lines = [
        "# Diagnostico tecnico do dashboard etario",
        f"# label: {label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Status das evidencias",
        "",
        f"- pg_stat_statements: {'disponivel' if pg_stat_available else 'pendente/bloqueado'}",
        f"- EXPLAIN ANALYZE: {'disponivel' if not explain_blocked else 'pendente/bloqueado'}",
        "",
        "## Ranking de gargalos",
        "",
    ]
    if not bottlenecks:
        lines.append("- Nenhum gargalo material identificado nas medicoes executadas.")
        lines.append("")
    else:
        for row in bottlenecks:
            lines.append(
                f"- `{row.target}`: impacto `{row.impact}` ({row.pct_total:.2f}% do tempo medio agregado). "
                f"Causa: {row.cause} Proximo passo: `{row.next_action}`. Evidencia: {', '.join(row.evidence)}."
            )
        lines.append("")

    lines.append("## Cenarios")
    lines.append("")
    for summary in summaries:
        lines.append(f"### {summary.slug}")
        lines.append("")
        lines.append(f"- Descricao: {summary.description}")
        lines.append(f"- Parametros: `{summary.params}`")
        if not summary.enabled:
            lines.append(f"- Status: skipped ({summary.skip_reason})")
            lines.append("")
            continue
        lines.append(
            "- Total ms: "
            f"min={summary.total_ms['min']}, p50={summary.total_ms['p50']}, "
            f"mean={summary.total_ms['mean']}, p95={summary.total_ms['p95']}, max={summary.total_ms['max']}"
        )
        lines.append(f"- Volumes: `{summary.volumes}`")
        if summary.stage_breakdown:
            top_stages = summary.stage_breakdown[:5]
            stage_text = ", ".join(
                f"{row['stage']}={row['mean_ms']}ms ({row['pct_total']}%)" for row in top_stages
            )
            lines.append(f"- Top stages: {stage_text}")
        if summary.query_breakdown:
            top_queries = summary.query_breakdown[:4]
            query_text = ", ".join(
                f"{row['query_family']}={row['mean_ms']}ms" for row in top_queries
            )
            lines.append(f"- Top query families: {query_text}")
        if summary.explain_flags:
            explain_text = ", ".join(
                f"{key}=[{','.join(value) or 'none'}]" for key, value in sorted(summary.explain_flags.items())
            )
            lines.append(f"- Explain flags: {explain_text}")
        if summary.pg_stat_delta_top:
            lines.append(f"- pg_stat delta top1: `{summary.pg_stat_delta_top[0]}`")
        lines.append("")

    if not pg_stat_available:
        lines.append("## Bloqueios")
        lines.append("")
        lines.append(
            "- `pg_stat_statements` indisponivel no ambiente real; o ranking foi fechado com profiling do servico e EXPLAIN quando possivel."
        )
        lines.append("")
    if explain_blocked:
        lines.append("## Bloqueios")
        lines.append("")
        lines.append(
            "- Houve falha ou indisponibilidade para um ou mais `EXPLAIN ANALYZE`; os itens afetados foram marcados como pendentes e nao inferidos implicitamente."
        )
        lines.append("")
    return "\n".join(lines) + "\n"


def _run_scenario(
    engine: Any,
    scenario: DashboardAgeScenario,
    *,
    warmups: int,
    measured_runs: int,
    pg_stat_available: bool,
) -> tuple[list[RunMetrics], list[PgStatDeltaRow], list[Any], list[Any]]:
    pg_before: list[Any] = []
    pg_after: list[Any] = []
    if pg_stat_available:
        with engine.connect() as conn:
            pg_before = fetch_pg_stat_statements_rows(
                conn,
                profile="dashboard_age_analysis",
                limit=50,
            )

    for _ in range(warmups):
        with Session(engine) as session:
            _run_warmup(session, scenario)

    runs: list[RunMetrics] = []
    for _ in range(measured_runs):
        with Session(engine) as session:
            runs.append(_profile_single_run(session, scenario))

    if pg_stat_available:
        with engine.connect() as conn:
            pg_after = fetch_pg_stat_statements_rows(
                conn,
                profile="dashboard_age_analysis",
                limit=50,
            )

    delta = compute_pg_stat_delta(pg_before, pg_after) if pg_stat_available else []
    return runs, delta, pg_before, pg_after


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="current", help="Rotulo para os artefatos gerados.")
    parser.add_argument("--warmups", type=int, default=3, help="Numero de warmups por cenario.")
    parser.add_argument("--runs", type=int, default=10, help="Numero de execucoes medidas por cenario.")
    parser.add_argument(
        "--out-dir",
        default=os.getenv("LEADS_AUDIT_EVIDENCE_DIR", str(DEFAULT_OUT_DIR)),
        help="Diretorio versionado para salvar evidencias.",
    )
    parser.add_argument(
        "--skip-pg-stat",
        action="store_true",
        help="Pula snapshots/deltas de pg_stat_statements.",
    )
    parser.add_argument(
        "--skip-explains",
        action="store_true",
        help="Pula a captura de EXPLAIN ANALYZE.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).date().isoformat()
    label = args.label

    engine = build_pg_engine(_worker_url())
    explain_engine = build_explain_engine(_worker_url())

    with explain_engine.connect() as conn:
        scenarios = resolve_dashboard_age_scenarios(conn)

    pg_stat_available = False
    if not args.skip_pg_stat:
        with engine.connect() as conn:
            pg_stat_available = pg_stat_statements_installed(conn)

    all_summaries: list[ScenarioSummary] = []
    explain_results: list[ExplainResult] = []
    raw_payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "scenarios": [],
    }

    overall_pg_before: list[Any] = []
    overall_pg_after: list[Any] = []
    if pg_stat_available:
        with engine.connect() as conn:
            overall_pg_before = fetch_pg_stat_statements_rows(
                conn,
                profile="dashboard_age_analysis",
                limit=50,
            )

    for scenario in scenarios:
        if not scenario.enabled:
            all_summaries.append(
                _summarize_scenario(
                    scenario,
                    runs=[],
                    warmups=args.warmups,
                    pg_stat_delta=[],
                    explains=[],
                )
            )
            raw_payload["scenarios"].append(asdict(all_summaries[-1]))
            continue

        runs, delta, scenario_pg_before, scenario_pg_after = _run_scenario(
            engine,
            scenario,
            warmups=args.warmups,
            measured_runs=args.runs,
            pg_stat_available=pg_stat_available,
        )

        scenario_explains: list[ExplainResult] = []
        if not args.skip_explains:
            with explain_engine.connect() as conn:
                scenario_explains = run_explain_specs(
                    conn,
                    scenario_slug=scenario.slug,
                    specs=build_dashboard_age_explain_specs(scenario),
                )
                explain_results.extend(scenario_explains)

        summary = _summarize_scenario(
            scenario,
            runs=runs,
            warmups=args.warmups,
            pg_stat_delta=delta,
            explains=scenario_explains,
        )
        all_summaries.append(summary)
        raw_payload["scenarios"].append(
            {
                **asdict(summary),
                "pg_stat_snapshot_before": serialize_rows(scenario_pg_before),
                "pg_stat_snapshot_after": serialize_rows(scenario_pg_after),
                "runs": [
                    {
                        "total_ms": _round_ms(run.total_ms),
                        "stage_stats": {
                            key: asdict(value) for key, value in sorted(run.stage_stats.items())
                        },
                        "query_stats": {
                            key: asdict(value) for key, value in sorted(run.query_stats.items())
                        },
                        "volumes": run.volumes,
                    }
                    for run in runs
                ],
            }
        )

    if pg_stat_available:
        with engine.connect() as conn:
            overall_pg_after = fetch_pg_stat_statements_rows(
                conn,
                profile="dashboard_age_analysis",
                limit=50,
            )

    overall_pg_delta = compute_pg_stat_delta(overall_pg_before, overall_pg_after) if pg_stat_available else []
    bottlenecks = _build_bottlenecks(all_summaries)
    explain_blocked = any(result.error for result in explain_results)

    summary_path = out_dir / f"dashboard_age_analysis_diagnostic_{label}_{stamp}.md"
    raw_path = out_dir / f"dashboard_age_analysis_profile_{label}_{stamp}.json"
    pg_stat_path = out_dir / f"dashboard_age_analysis_pg_stat_{label}_{stamp}.md"
    explain_path = out_dir / f"dashboard_age_analysis_explain_{label}_{stamp}.md"

    summary_path.write_text(
        _render_summary_markdown(
            label=label,
            summaries=all_summaries,
            bottlenecks=bottlenecks,
            pg_stat_available=pg_stat_available,
            explain_blocked=explain_blocked,
        ),
        encoding="utf-8",
    )

    raw_payload["overall_pg_stat_before"] = serialize_rows(overall_pg_before)
    raw_payload["overall_pg_stat_after"] = serialize_rows(overall_pg_after)
    raw_payload["overall_pg_stat_delta"] = serialize_deltas(overall_pg_delta)
    raw_payload["bottlenecks"] = [asdict(item) for item in bottlenecks]
    raw_path.write_text(
        json.dumps(raw_payload, ensure_ascii=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    if pg_stat_available:
        pg_stat_sections = [
            render_pg_stat_markdown(
                rows=overall_pg_before,
                label=f"{label}-before",
                profile="dashboard_age_analysis",
            ),
            render_pg_stat_markdown(
                rows=overall_pg_after,
                label=f"{label}-after",
                profile="dashboard_age_analysis",
            ),
            render_pg_stat_delta_markdown(
                rows=overall_pg_delta,
                label=f"{label}-delta",
                profile="dashboard_age_analysis",
            ),
        ]
        pg_stat_path.write_text("\n".join(pg_stat_sections), encoding="utf-8")
    else:
        pg_stat_path.write_text(
            "# pg_stat_statements do dashboard etario\n\nERRO: pg_stat_statements indisponivel no banco alvo.\n",
            encoding="utf-8",
        )

    if args.skip_explains:
        explain_path.write_text(
            "# EXPLAIN do dashboard etario\n\nStatus: skipped via --skip-explains.\n",
            encoding="utf-8",
        )
    else:
        explain_path.write_text(
            render_dashboard_age_explains_markdown(
                scenarios=scenarios,
                results=explain_results,
                label=label,
            ),
            encoding="utf-8",
        )

    print(f"Escrito: {summary_path}")
    print(f"Escrito: {raw_path}")
    print(f"Escrito: {pg_stat_path}")
    print(f"Escrito: {explain_path}")


if __name__ == "__main__":
    main()
