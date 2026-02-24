"""Integrated tests for advanced DQ checks and consolidated renderer output."""

from __future__ import annotations

from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from etl.validate.checks_access_control import AccessControlReconciliationCheck
from etl.validate.checks_cross_source import (
    CrossSourceDatasetSpec,
    CrossSourceInconsistencyCheck,
)
from etl.validate.checks_percentages import (
    PercentBoundsCheck,
    PercentSumCheck,
    PercentSumRuleConfig,
    PercentageCheckConfig,
)
from etl.validate.framework import CheckContext, CheckResult, CheckStatus, Severity
from etl.validate.render_dq_report import render_dq_report, render_dq_report_json


def _make_engine():
    """Create in-memory SQLite engine for advanced DQ integrated tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_attendance_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic attendance table used by reconciliation tests."""

    metadata = sa.MetaData()
    table = sa.Table(
        "attendance_access_control",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.String(160), nullable=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=True),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("ingressos_validos", sa.Numeric(20, 6), nullable=True),
        sa.Column("presentes", sa.Numeric(20, 6), nullable=True),
        sa.Column("ausentes", sa.Numeric(20, 6), nullable=True),
        sa.Column("comparecimento_pct", sa.Numeric(20, 6), nullable=True),
    )
    metadata.create_all(engine)
    return table


def _create_percent_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic percentage-metrics table."""

    metadata = sa.MetaData()
    table = sa.Table(
        "stg_pct_metrics",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.String(80), nullable=True),
        sa.Column("metric_key", sa.String(120), nullable=True),
        sa.Column("metric_value", sa.Numeric(20, 6), nullable=True),
        sa.Column("unit", sa.String(40), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
    )
    metadata.create_all(engine)
    return table


def _create_cross_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic table for cross-source inconsistency checks."""

    metadata = sa.MetaData()
    table = sa.Table(
        "stg_cross_source_metrics",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=True),
        sa.Column("metric_key", sa.String(200), nullable=False),
        sa.Column("metric_value", sa.Numeric(20, 6), nullable=True),
        sa.Column("unit", sa.String(40), nullable=True),
        sa.Column("status", sa.String(16), nullable=True),
    )
    metadata.create_all(engine)
    return table


def _pct_config() -> PercentageCheckConfig:
    """Build baseline percentage check config for integrated advanced tests."""

    return PercentageCheckConfig(
        dataset_id="pct_metrics",
        table="stg_pct_metrics",
        severity=Severity.ERROR,
        ingestion_id_column="ingestion_id",
        source_id_column="source_id",
        lineage_ref_id_column="lineage_ref_id",
        value_column="metric_value",
        unit_column="unit",
        percent_units=("percent",),
        status_column="status",
        allowed_statuses=("ok",),
        require_lineage=True,
        lower_bound=Decimal("0"),
        upper_bound=Decimal("100"),
        sum_rules=(
            PercentSumRuleConfig(
                rule_id="by_group",
                group_by=("source_id", "ingestion_id", "group_id"),
                target_sum=Decimal("100"),
                tolerance=Decimal("1"),
                min_items=2,
            ),
        ),
    )


def test_advanced_checks_validate_severity_and_references() -> None:
    """Advanced checks should expose severity and key references in findings."""

    engine = _make_engine()
    attendance_table = _create_attendance_table(engine)
    percent_table = _create_percent_table(engine)
    cross_table = _create_cross_table(engine)

    with engine.begin() as conn:
        conn.execute(
            attendance_table.insert(),
            [
                {
                    "id": 1,
                    "session_id": 20251214,
                    "source_id": "SRC_ACCESS_14",
                    "ingestion_id": 940,
                    "lineage_ref_id": 9001,
                    "ingressos_validos": Decimal("100"),
                    "presentes": Decimal("120"),
                    "ausentes": Decimal("0"),
                    "comparecimento_pct": Decimal("120"),
                }
            ],
        )
        conn.execute(
            percent_table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 940,
                    "source_id": "SRC_DIMAC_1",
                    "lineage_ref_id": None,
                    "group_id": "Q1",
                    "metric_key": "faixa_a",
                    "metric_value": Decimal("130"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": 940,
                    "source_id": "SRC_DIMAC_1",
                    "lineage_ref_id": 9102,
                    "group_id": "Q1",
                    "metric_key": "faixa_b",
                    "metric_value": Decimal("20"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )
        conn.execute(
            cross_table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 940,
                    "source_id": "SRC_MTC_A",
                    "lineage_ref_id": 9201,
                    "metric_key": "share_bb_total",
                    "metric_value": Decimal("55"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": 940,
                    "source_id": "SRC_MTC_B",
                    "lineage_ref_id": 9202,
                    "metric_key": "share_bb_total",
                    "metric_value": Decimal("49"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )

    pct_config = _pct_config()
    cross_spec = CrossSourceDatasetSpec(
        dataset_id="mtc_metrics",
        table="stg_cross_source_metrics",
        status_column="status",
        allowed_statuses=("ok",),
    )

    with Session(engine) as session:
        context = CheckContext(ingestion_id=940, resources={"session": session})
        access_result = AccessControlReconciliationCheck().run(context)
        bounds_result = PercentBoundsCheck(pct_config).run(context)
        sum_result = PercentSumCheck(pct_config, pct_config.sum_rules[0]).run(context)
        cross_result = CrossSourceInconsistencyCheck(
            (cross_spec,),
            severity=Severity.WARNING,
            persist_inconsistencies=False,
        ).run(context)

    assert access_result.status == CheckStatus.FAIL
    assert access_result.severity == Severity.ERROR
    assert access_result.evidence["findings_sample"][0]["session_id"] == 20251214

    assert bounds_result.status == CheckStatus.FAIL
    assert bounds_result.severity == Severity.ERROR
    bounds_codes = {item["code"] for item in bounds_result.evidence["findings_sample"]}
    assert "PERCENT_OUT_OF_BOUNDS" in bounds_codes
    assert "PERCENT_MISSING_LINEAGE" in bounds_codes

    assert sum_result.status == CheckStatus.FAIL
    assert sum_result.severity == Severity.ERROR
    assert sum_result.evidence["findings_sample"][0]["code"] == "PERCENT_SUM_MISMATCH"

    assert cross_result.status == CheckStatus.FAIL
    assert cross_result.severity == Severity.WARNING
    assert cross_result.evidence["findings_sample"][0]["metric_key"] == "share_bb_total"
    assert "share_bb_total" in cross_result.evidence["metric_keys"]


def test_advanced_renderer_includes_evidence_and_standard_ordering() -> None:
    """Renderer should expose minimal evidence and deterministic ordering."""

    raw_results = [
        CheckResult(
            check_id="dq.schema.z_dataset",
            status=CheckStatus.FAIL,
            severity=Severity.ERROR,
            message="Tabela ausente",
            ingestion_id=941,
            evidence={"dataset_id": "z_dataset", "missing_table": True},
            lineage={"source_id": "SRC_Z", "location_value": "page:9", "evidence_text": "Tabela Z"},
        ),
        CheckResult(
            check_id="dq.cross_source.inconsistency",
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="Conflito de metrica",
            ingestion_id=941,
            evidence={
                "dataset_id": "a_dataset",
                "status": "INCONSISTENTE",
                "metric_key": "share_bb_total",
                "suggested_action": "Revisar fonte A vs B",
            },
            lineage={"source_id": "SRC_A", "location_value": "slide:3", "evidence_text": "Box Share"},
        ),
        CheckResult(
            check_id="dq.schema.a_dataset",
            status=CheckStatus.FAIL,
            severity=Severity.WARNING,
            message="Coluna obrigatoria ausente",
            ingestion_id=941,
            evidence={"dataset_id": "a_dataset", "missing_columns": ["metric_value"]},
            lineage={"source_id": "SRC_A", "location_value": "sheet:Dados", "evidence_text": "Cabecalho"},
        ),
    ]

    payload = render_dq_report_json(raw_results)
    markdown = render_dq_report(raw_results)

    assert payload["sections"]["errors"][0]["dataset_id"] == "z_dataset"
    warning_ids = [item["check_id"] for item in payload["sections"]["warnings"]]
    assert warning_ids == sorted(warning_ids)
    assert payload["sections"]["inconsistencies"][0]["metric_key"] == "share_bb_total"
    assert list(payload["sections"]["gaps_by_dataset"].keys()) == ["a_dataset", "z_dataset"]

    assert "Fonte: SRC_A | Local: slide:3 | Evidencia: Box Share" in markdown
    assert "## Inconsistencias" in markdown
    assert "## Gaps Por Dataset" in markdown

