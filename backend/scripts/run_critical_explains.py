"""Gera EXPLAIN ANALYZE para consultas criticas.

Perfis suportados:
  - leads_critical: baseline legado do fluxo de leads
  - dashboard_age: familias de query do dashboard etario

Uso:
  python scripts/run_critical_explains.py --label before
  python scripts/run_critical_explains.py --profile dashboard_age --label current
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.dialects import postgresql
from sqlmodel import select


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parent
DEFAULT_OUT_DIR = REPO_ROOT / "auditoria" / "evidencias"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.models.lead_batch import BatchStage, LeadBatch, PipelineStatus  # noqa: E402
from app.models.models import Evento, Lead, LeadEvento, Usuario, UsuarioTipo  # noqa: E402
from app.schemas.dashboard import AgeAnalysisQuery  # noqa: E402
from app.services import dashboard_service as ds  # noqa: E402


for env_path in (BASE_DIR / ".env", REPO_ROOT / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()


@dataclass(frozen=True, slots=True)
class ExplainQuerySpec:
    title: str
    statement: Any


@dataclass(frozen=True, slots=True)
class ExplainResult:
    scenario_slug: str
    title: str
    sql: str
    plan_lines: tuple[str, ...]
    flags: tuple[str, ...]
    error: str | None = None


@dataclass(frozen=True, slots=True)
class DashboardAgeScenario:
    slug: str
    description: str
    params: AgeAnalysisQuery
    enabled: bool = True
    skip_reason: str | None = None

    @property
    def uses_event_name_fallback(self) -> bool:
        return self.enabled and self.params.evento_id is None


def _url() -> str:
    u = (os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not u or u.startswith("sqlite"):
        raise SystemExit("Defina DIRECT_URL ou DATABASE_URL (Postgres) para rodar EXPLAIN.")
    return u


def build_engine(url: str):
    connect_args: dict[str, Any] = {"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))}
    if (
        "sslmode=" not in url
        and "ssl=require" not in url
        and "127.0.0.1" not in url
        and "localhost" not in url
    ):
        connect_args["sslmode"] = "require"
    return sa.create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def _synthetic_npbb_user() -> Usuario:
    return Usuario(
        email="dashboard.age.diagnostic@npbb.local",
        password_hash="diagnostic-only",
        tipo_usuario=UsuarioTipo.NPBB,
        ativo=True,
    )


def _anchor_date(conn: sa.Connection) -> date | None:
    value = conn.execute(sa.text("select max(data_criacao)::date from lead")).scalar()
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _resolve_reference_event_id(conn: sa.Connection, anchor: date | None) -> int | None:
    if anchor is not None:
        recent_cutoff = anchor - timedelta(days=89)
        recent_row = conn.execute(
            sa.text(
                """
                select le.evento_id, count(*) as total
                from lead_evento le
                join lead l on l.id = le.lead_id
                where l.data_criacao::date >= :recent_cutoff
                group by le.evento_id
                order by total desc, le.evento_id
                limit 1
                """
            ),
            {"recent_cutoff": recent_cutoff},
        ).first()
        if recent_row is not None:
            return int(recent_row.evento_id)

    total_row = conn.execute(
        sa.text(
            """
            select le.evento_id, count(*) as total
            from lead_evento le
            group by le.evento_id
            order by total desc, le.evento_id
            limit 1
            """
        )
    ).first()
    if total_row is not None:
        return int(total_row.evento_id)

    if anchor is not None:
        recent_batch_row = conn.execute(
            sa.text(
                """
                select lb.evento_id, count(*) as total
                from lead l
                join lead_batches lb on lb.id = l.batch_id
                where l.data_criacao::date >= :recent_cutoff
                  and lb.evento_id is not null
                  and lb.stage = :stage_gold
                  and lb.pipeline_status in :statuses
                group by lb.evento_id
                order by total desc, lb.evento_id
                limit 1
                """
            ).bindparams(sa.bindparam("statuses", expanding=True)),
            {
                "recent_cutoff": anchor - timedelta(days=89),
                "stage_gold": BatchStage.GOLD.value,
                "statuses": [PipelineStatus.PASS.value, PipelineStatus.PASS_WITH_WARNINGS.value],
            },
        ).first()
        if recent_batch_row is not None:
            return int(recent_batch_row.evento_id)

    batch_row = conn.execute(
        sa.text(
            """
            select lb.evento_id, count(*) as total
            from lead l
            join lead_batches lb on lb.id = l.batch_id
            where lb.evento_id is not null
              and lb.stage = :stage_gold
              and lb.pipeline_status in :statuses
            group by lb.evento_id
            order by total desc, lb.evento_id
            limit 1
            """
        ).bindparams(sa.bindparam("statuses", expanding=True)),
        {
            "stage_gold": BatchStage.GOLD.value,
            "statuses": [PipelineStatus.PASS.value, PipelineStatus.PASS_WITH_WARNINGS.value],
        },
    ).first()
    if batch_row is not None:
        return int(batch_row.evento_id)
    return None


def resolve_dashboard_age_scenarios(conn: sa.Connection) -> list[DashboardAgeScenario]:
    anchor = _anchor_date(conn)
    reference_event_id = _resolve_reference_event_id(conn, anchor)
    rolling_end = anchor
    rolling_start = anchor - timedelta(days=29) if anchor is not None else None

    no_filters = DashboardAgeScenario(
        slug="no_filters",
        description="Sem filtros",
        params=AgeAnalysisQuery(),
    )
    if reference_event_id is None:
        event_only = DashboardAgeScenario(
            slug="reference_event",
            description="Evento de maior volume recente ou total",
            params=AgeAnalysisQuery(),
            enabled=False,
            skip_reason="Nenhum evento de referencia encontrado em lead_evento ou batches GOLD.",
        )
        event_and_window = DashboardAgeScenario(
            slug="reference_event_30d",
            description="Evento de referencia com janela movel de 30 dias",
            params=AgeAnalysisQuery(),
            enabled=False,
            skip_reason="Nenhum evento de referencia encontrado em lead_evento ou batches GOLD.",
        )
    else:
        event_only = DashboardAgeScenario(
            slug="reference_event",
            description="Evento de maior volume recente ou total",
            params=AgeAnalysisQuery(evento_id=reference_event_id),
        )
        event_and_window = DashboardAgeScenario(
            slug="reference_event_30d",
            description="Evento de referencia com janela movel de 30 dias",
            params=AgeAnalysisQuery(
                evento_id=reference_event_id,
                data_inicio=rolling_start,
                data_fim=rolling_end,
            ),
        )

    if rolling_start is None or rolling_end is None:
        rolling_window = DashboardAgeScenario(
            slug="rolling_30d",
            description="Janela movel de 30 dias ancorada na maior lead.data_criacao",
            params=AgeAnalysisQuery(),
            enabled=False,
            skip_reason="Tabela lead sem data_criacao para definir ancora temporal.",
        )
        if event_and_window.enabled:
            event_and_window = DashboardAgeScenario(
                slug=event_and_window.slug,
                description=event_and_window.description,
                params=AgeAnalysisQuery(evento_id=reference_event_id),
                enabled=False,
                skip_reason="Tabela lead sem data_criacao para definir ancora temporal.",
            )
    else:
        rolling_window = DashboardAgeScenario(
            slug="rolling_30d",
            description="Janela movel de 30 dias ancorada na maior lead.data_criacao",
            params=AgeAnalysisQuery(data_inicio=rolling_start, data_fim=rolling_end),
        )

    return [no_filters, event_only, rolling_window, event_and_window]


def detect_explain_flags(plan_lines: list[str]) -> tuple[str, ...]:
    flags: set[str] = set()
    lowered = [line.lower() for line in plan_lines]
    if any("seq scan" in line for line in lowered):
        flags.add("seq_scan")
    if any("temp blocks" in line or "temp read=" in line or "temp written=" in line for line in lowered):
        flags.add("temp_blocks")
    if any("sort method: external merge" in line or "disk:" in line for line in lowered):
        flags.add("sort_spill")

    shared_reads = 0
    for line in lowered:
        if "buffers:" not in line or "read=" not in line:
            continue
        try:
            read_chunk = line.split("read=", 1)[1].split()[0]
            shared_reads += int(read_chunk.rstrip(","))
        except (IndexError, ValueError):
            continue
    if shared_reads >= 1000:
        flags.add("heavy_buffer_read")
    return tuple(sorted(flags))


def _compile_literal_sql(statement: Any) -> str:
    compiled = statement.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True},
    )
    return str(compiled)


def _primary_stmt(params: AgeAnalysisQuery, current_user: Usuario):
    filters = ds._build_filters(params, current_user)
    return (
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
        .select_from(ds._from_clause())
        .where(*filters)
        .distinct()
    )


def _batch_stmt(params: AgeAnalysisQuery, current_user: Usuario):
    batch_filters = list(ds._build_filters(params, current_user))
    batch_filters.append(Lead.batch_id.is_not(None))
    batch_filters.append(LeadBatch.evento_id.is_not(None))
    batch_filters.append(LeadBatch.stage == BatchStage.GOLD)
    batch_filters.append(
        LeadBatch.pipeline_status.in_(
            tuple(sorted(ds._GOLD_PIPELINE_STATUSES, key=lambda item: item.value))
        )
    )
    return (
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
        .select_from(ds._from_clause_batch())
        .where(*batch_filters)
        .distinct()
    )


def _visible_events_stmt(params: AgeAnalysisQuery, current_user: Usuario):
    event_filters = ds._build_event_filters(params, current_user)
    return select(Evento.id, Evento.nome, Evento.cidade, Evento.estado).where(*event_filters)


def _event_name_stmt(params: AgeAnalysisQuery):
    lead_filters = ds._build_lead_filters(params)
    nome_filters = list(lead_filters)
    nome_filters.append(Lead.evento_nome.is_not(None))
    nome_filters.append(sa.func.trim(Lead.evento_nome) != "")
    return select(
        Lead.id,
        Lead.evento_nome,
        Lead.data_nascimento,
        Lead.is_cliente_bb,
        Lead.cpf,
        Lead.nome,
        Lead.sobrenome,
    ).where(*nome_filters)


def build_dashboard_age_explain_specs(scenario: DashboardAgeScenario) -> list[ExplainQuerySpec]:
    if not scenario.enabled:
        return []
    current_user = _synthetic_npbb_user()
    specs = [
        ExplainQuerySpec(title="_load_lead_event_facts", statement=_primary_stmt(scenario.params, current_user)),
        ExplainQuerySpec(
            title="_load_lead_event_facts_via_batch",
            statement=_batch_stmt(scenario.params, current_user),
        ),
    ]
    if scenario.uses_event_name_fallback:
        specs.extend(
            [
                ExplainQuerySpec(
                    title="_load_visible_events_by_normalized_name",
                    statement=_visible_events_stmt(scenario.params, current_user),
                ),
                ExplainQuerySpec(
                    title="_load_lead_event_facts_via_evento_nome",
                    statement=_event_name_stmt(scenario.params),
                ),
            ]
        )
    return specs


def run_explain_specs(
    conn: sa.Connection,
    *,
    scenario_slug: str,
    specs: list[ExplainQuerySpec],
) -> list[ExplainResult]:
    results: list[ExplainResult] = []
    for spec in specs:
        sql = _compile_literal_sql(spec.statement)
        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {sql}"
        try:
            rows = conn.execute(sa.text(explain_sql)).fetchall()
            plan_lines = [str(row[0]) for row in rows]
            results.append(
                ExplainResult(
                    scenario_slug=scenario_slug,
                    title=spec.title,
                    sql=sql,
                    plan_lines=tuple(plan_lines),
                    flags=detect_explain_flags(plan_lines),
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                ExplainResult(
                    scenario_slug=scenario_slug,
                    title=spec.title,
                    sql=sql,
                    plan_lines=(),
                    flags=(),
                    error=str(exc),
                )
            )
    return results


def render_dashboard_age_explains_markdown(
    *,
    scenarios: list[DashboardAgeScenario],
    results: list[ExplainResult],
    label: str,
) -> str:
    lines = [
        "# EXPLAIN do dashboard etario",
        f"# label: {label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    results_by_scenario: dict[str, list[ExplainResult]] = {}
    for result in results:
        results_by_scenario.setdefault(result.scenario_slug, []).append(result)

    for scenario in scenarios:
        lines.append(f"## {scenario.slug}")
        lines.append("")
        lines.append(f"Descricao: {scenario.description}")
        lines.append(f"Parametros: {scenario.params.model_dump()}")
        if not scenario.enabled:
            lines.append(f"Status: skipped ({scenario.skip_reason})")
            lines.append("")
            continue

        scenario_results = results_by_scenario.get(scenario.slug, [])
        if not scenario_results:
            lines.append("Status: sem resultados de EXPLAIN.")
            lines.append("")
            continue

        for result in scenario_results:
            lines.append(f"### {result.title}")
            lines.append("")
            if result.error:
                lines.append(f"ERRO: {result.error}")
                lines.append("")
                continue
            lines.append(f"Flags: {', '.join(result.flags) if result.flags else 'nenhuma'}")
            lines.append("")
            lines.append("```sql")
            lines.append(result.sql)
            lines.append("```")
            lines.append("")
            lines.append("```text")
            lines.extend(result.plan_lines)
            lines.append("```")
            lines.append("")
    return "\n".join(lines) + "\n"


def _run_legacy_leads_critical(conn: sa.Connection) -> list[str]:
    lines: list[str] = []
    batch_id = conn.execute(sa.text("SELECT id FROM lead_batches ORDER BY id DESC LIMIT 1")).scalar()
    evento_id = conn.execute(sa.text("SELECT id FROM evento ORDER BY id DESC LIMIT 1")).scalar()
    if not batch_id:
        lines.append("# Sem lead_batches - pulando explains que dependem de batch_id.")
    if not evento_id:
        lines.append("# Sem evento - pulando explains que dependem de evento_id.")

    def run(title: str, sql: str, params: dict[str, Any] | None = None) -> None:
        lines.append(f"## {title}")
        lines.append("")
        explain = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {sql}"
        try:
            res = conn.execute(sa.text(explain), params or {})
            for row in res:
                lines.append(str(row[0]))
        except Exception as exc:  # noqa: BLE001
            lines.append(f"ERRO: {exc}")
        lines.append("")

    if batch_id:
        run(
            "lead_batches metadados (sem TOAST de arquivo_bronze)",
            """
            SELECT id, enviado_por, evento_id, nome_arquivo_original, arquivo_sha256, stage,
                   bronze_storage_bucket, bronze_storage_key, bronze_size_bytes
            FROM lead_batches WHERE id = :bid
            """,
            {"bid": batch_id},
        )
        run(
            "leads_silver ordenado por row_index (batch)",
            """
            SELECT id, batch_id, row_index FROM leads_silver
            WHERE batch_id = :bid ORDER BY row_index LIMIT 200
            """,
            {"bid": batch_id},
        )

    if evento_id:
        start = datetime.now(timezone.utc) - timedelta(days=30)
        end = datetime.now(timezone.utc) + timedelta(days=1)
        run(
            "dashboard-style: contagem por evento com filtro de data em lead.data_criacao (faixa)",
            """
            SELECT count(*) AS n
            FROM lead_evento le
            INNER JOIN evento e ON e.id = le.evento_id
            INNER JOIN lead l ON l.id = le.lead_id
            WHERE le.evento_id = :eid
              AND l.data_criacao >= :start_at
              AND l.data_criacao < :end_at
            """,
            {"eid": evento_id, "start_at": start, "end_at": end},
        )

    run(
        "indice parcial data_compra (amostra: ultimos leads com data_compra)",
        """
        SELECT id, data_compra FROM lead
        WHERE data_compra IS NOT NULL
        ORDER BY data_compra DESC NULLS LAST
        LIMIT 50
        """,
    )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="current", help="Sufixo do arquivo: before, after ou current")
    parser.add_argument(
        "--profile",
        default="leads_critical",
        choices=("leads_critical", "dashboard_age"),
        help="Perfil de EXPLAIN a executar.",
    )
    parser.add_argument(
        "--out-dir",
        default=os.getenv("LEADS_AUDIT_EVIDENCE_DIR", str(DEFAULT_OUT_DIR)),
        help="Diretorio versionado para salvar evidencia.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = build_engine(_url())

    if args.profile == "dashboard_age":
        with engine.connect() as conn:
            scenarios = resolve_dashboard_age_scenarios(conn)
            results: list[ExplainResult] = []
            for scenario in scenarios:
                results.extend(
                    run_explain_specs(
                        conn,
                        scenario_slug=scenario.slug,
                        specs=build_dashboard_age_explain_specs(scenario),
                    )
                )
        out_file = out_dir / f"explain_dashboard_age_{args.label}.md"
        out_file.write_text(
            render_dashboard_age_explains_markdown(
                scenarios=scenarios,
                results=results,
                label=args.label,
            ),
            encoding="utf-8",
        )
        print(f"Escrito: {out_file}")
        return

    lines = [
        f"# label: {args.label}",
        f"# gerado em {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    with engine.connect() as conn:
        lines.extend(_run_legacy_leads_critical(conn))

    out_file = out_dir / f"explain_leads_critical_{args.label}.txt"
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {out_file}")


if __name__ == "__main__":
    main()
