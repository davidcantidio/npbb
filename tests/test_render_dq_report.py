"""Unit tests for DQ report renderers (markdown/json)."""

from __future__ import annotations

from datetime import datetime, timezone

from etl.validate.framework import CheckReport, CheckResult, CheckStatus, Severity
from etl.validate.render_dq_report import render_dq_report, render_dq_report_json


def _sample_report() -> CheckReport:
    """Build deterministic report fixture with error/warning/inconsistency/gap."""

    results = (
        CheckResult(
            check_id="dq.cross_source.inconsistency",
            status=CheckStatus.FAIL,
            severity=Severity.ERROR,
            message="Conflito de valores entre fontes",
            ingestion_id=501,
            evidence={
                "dataset_id": "dimac_metrics",
                "status": "INCONSISTENTE",
                "suggested_action": "Revisar fonte A vs B",
            },
            lineage={
                "source_id": "SRC_DIMAC_A",
                "location_value": "page:12",
                "evidence_text": "Tabela Dimac - Share BB",
                "lineage_ref_id": 77,
            },
        ),
        CheckResult(
            check_id="dq.schema.stg_dimac_metrics",
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="Tabela de dataset nao encontrada",
            ingestion_id=501,
            evidence={
                "dataset_id": "stg_dimac_metrics",
                "missing_table": True,
            },
            lineage={"source_id": "SRC_DIMAC_B"},
        ),
        CheckResult(
            check_id="dq.status.info",
            status=CheckStatus.PASS,
            severity=Severity.INFO,
            message="Execucao com status ok",
            ingestion_id=501,
            evidence={"dataset_id": "ops"},
            lineage={},
        ),
    )
    return CheckReport(
        ingestion_id=501,
        generated_at=datetime(2026, 2, 11, 12, 0, 0, tzinfo=timezone.utc),
        fail_on=Severity.ERROR,
        exit_code=1,
        summary={
            "total": 3,
            "pass": 1,
            "fail": 2,
            "skip": 0,
            "info": 1,
            "warning": 1,
            "error": 1,
        },
        results=results,
    )


def test_render_dq_report_json_groups_sections_and_preserves_base_contract() -> None:
    """JSON renderer should expose framework fields and grouped DQ sections."""

    payload = render_dq_report_json(_sample_report())
    assert payload["ingestion_id"] == 501
    assert payload["summary"]["fail"] == 2
    assert isinstance(payload["results"], list)
    assert len(payload["sections"]["errors"]) == 1
    assert len(payload["sections"]["warnings"]) == 1
    assert len(payload["sections"]["inconsistencies"]) == 1
    assert "stg_dimac_metrics" in payload["sections"]["gaps_by_dataset"]
    inconsistency_item = payload["sections"]["inconsistencies"][0]
    assert inconsistency_item["source_id"] == "SRC_DIMAC_A"
    assert inconsistency_item["location"] == "page:12"
    assert inconsistency_item["evidence_text"] == "Tabela Dimac - Share BB"


def test_render_dq_report_markdown_contains_sections_and_evidence_line() -> None:
    """Markdown renderer should include grouped sections and evidence rows."""

    markdown = render_dq_report(_sample_report())
    assert "# DQ Report" in markdown
    assert "## Errors" in markdown
    assert "## Warnings" in markdown
    assert "## Inconsistencias" in markdown
    assert "## Gaps Por Dataset" in markdown
    assert "Fonte: SRC_DIMAC_A | Local: page:12 | Evidencia: Tabela Dimac - Share BB" in markdown


def test_render_dq_report_json_accepts_plain_results_sequence() -> None:
    """Renderer should accept a plain list of CheckResult without CheckReport."""

    results = [
        CheckResult(
            check_id="dq.example.gap",
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="Gap de dados detectado",
            ingestion_id=77,
            evidence={"dataset_id": "example_dataset", "status": "GAP"},
            lineage={},
        )
    ]
    payload = render_dq_report_json(results)
    assert payload["ingestion_id"] == 77
    assert payload["summary"]["total"] == 1
    assert "example_dataset" in payload["sections"]["gaps_by_dataset"]

