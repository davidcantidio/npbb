# ruff: noqa: E402

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.capture_pg_stat_statements import (
    PgStatStatementRow,
    compute_pg_stat_delta,
)
from scripts.profile_dashboard_age_analysis import (
    classify_bottleneck_impact,
    classify_dashboard_age_statement,
)
from scripts.run_critical_explains import detect_explain_flags


def test_compute_pg_stat_delta_uses_queryid_and_ignores_non_positive_growth() -> None:
    before = [
        PgStatStatementRow(
            queryid="q1",
            calls=10,
            total_exec_ms=100.0,
            mean_exec_ms=10.0,
            rows=50,
            shared_blks_hit=200,
            shared_blks_read=30,
            temp_blks_read=0,
            temp_blks_written=0,
            query_sample="select 1",
        )
    ]
    after = [
        PgStatStatementRow(
            queryid="q1",
            calls=15,
            total_exec_ms=145.5,
            mean_exec_ms=9.7,
            rows=80,
            shared_blks_hit=280,
            shared_blks_read=45,
            temp_blks_read=2,
            temp_blks_written=1,
            query_sample="select 1",
        ),
        PgStatStatementRow(
            queryid="q2",
            calls=0,
            total_exec_ms=0.0,
            mean_exec_ms=0.0,
            rows=0,
            shared_blks_hit=0,
            shared_blks_read=0,
            temp_blks_read=0,
            temp_blks_written=0,
            query_sample="select 2",
        ),
    ]

    delta = compute_pg_stat_delta(before, after)

    assert len(delta) == 1
    assert delta[0].queryid == "q1"
    assert delta[0].calls_delta == 5
    assert delta[0].total_exec_ms_delta == 45.5
    assert delta[0].shared_blks_read_delta == 15


def test_classify_dashboard_age_statement_matches_known_query_families() -> None:
    primary = """
    SELECT evento.id, evento.nome, evento.cidade, evento.estado, lead.id
    FROM lead_evento JOIN lead ON lead.id = lead_evento.lead_id
    JOIN evento ON evento.id = lead_evento.evento_id
    """
    event_name = """
    SELECT lead.id, lead.evento_nome, lead.data_nascimento, lead.is_cliente_bb,
           lead.cpf, lead.nome, lead.sobrenome
    FROM lead
    WHERE lead.evento_nome IS NOT NULL
    """

    assert classify_dashboard_age_statement(primary) == "_load_lead_event_facts.sql"
    assert (
        classify_dashboard_age_statement(event_name)
        == "_load_lead_event_facts_via_evento_nome.sql"
    )


def test_detect_explain_flags_finds_seq_scan_temp_blocks_and_sort_spill() -> None:
    plan = [
        "Seq Scan on lead",
        "Buffers: shared hit=10 read=1500 temp read=12 written=3",
        "Sort Method: external merge  Disk: 1024kB",
    ]

    flags = detect_explain_flags(plan)

    assert flags == ("heavy_buffer_read", "seq_scan", "sort_spill", "temp_blocks")


def test_classify_bottleneck_impact_prioritizes_severe_explain_flags() -> None:
    assert classify_bottleneck_impact(12.0, {"seq_scan"}) == "alto"
    assert classify_bottleneck_impact(20.0, set()) == "medio"
    assert classify_bottleneck_impact(4.0, set(), multi_pass=True) == "medio"
    assert classify_bottleneck_impact(4.0, set()) == "baixo"
