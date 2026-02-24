"""Unit tests for percentage bounds/sum data-quality checks."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from etl.validate.checks_percentages import (
    PercentBoundsCheck,
    PercentSumCheck,
    PercentSumRuleConfig,
    PercentageCheckConfig,
    build_percentage_checks,
    load_percentage_check_configs,
)
from etl.validate.framework import CheckContext, CheckStatus, Severity


def _make_engine():
    """Create in-memory SQLite engine for isolated percentage check tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_percentage_table(engine) -> sa.Table:  # noqa: ANN001
    """Create synthetic table used by percentage checks.

    Args:
        engine: SQLAlchemy engine for test schema.

    Returns:
        SQLAlchemy table object.
    """

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


def _base_config() -> PercentageCheckConfig:
    """Return a baseline percentage check config used by tests."""

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


def test_percent_bounds_check_detects_bounds_and_missing_lineage() -> None:
    """Bounds check should fail for out-of-range values and missing lineage."""

    engine = _make_engine()
    table = _create_percentage_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 700,
                    "source_id": "SRC_SOCIAL",
                    "lineage_ref_id": 101,
                    "group_id": "G1",
                    "metric_key": "a",
                    "metric_value": Decimal("120"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": 700,
                    "source_id": "SRC_SOCIAL",
                    "lineage_ref_id": None,
                    "group_id": "G1",
                    "metric_key": "b",
                    "metric_value": Decimal("30"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )

    with Session(engine) as session:
        result = PercentBoundsCheck(_base_config()).run(
            CheckContext(ingestion_id=700, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    codes = {finding["code"] for finding in result.evidence["findings_sample"]}
    assert "PERCENT_OUT_OF_BOUNDS" in codes
    assert "PERCENT_MISSING_LINEAGE" in codes


def test_percent_sum_check_detects_inconsistent_group_sum() -> None:
    """Sum check should fail when grouped percentages do not reconcile to target."""

    engine = _make_engine()
    table = _create_percentage_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 701,
                    "source_id": "SRC_DIMAC",
                    "lineage_ref_id": 201,
                    "group_id": "Q1",
                    "metric_key": "opt_a",
                    "metric_value": Decimal("40"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": 701,
                    "source_id": "SRC_DIMAC",
                    "lineage_ref_id": 202,
                    "group_id": "Q1",
                    "metric_key": "opt_b",
                    "metric_value": Decimal("30"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 3,
                    "ingestion_id": 701,
                    "source_id": "SRC_DIMAC",
                    "lineage_ref_id": 203,
                    "group_id": "Q2",
                    "metric_key": "opt_a",
                    "metric_value": Decimal("60"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 4,
                    "ingestion_id": 701,
                    "source_id": "SRC_DIMAC",
                    "lineage_ref_id": 204,
                    "group_id": "Q2",
                    "metric_key": "opt_b",
                    "metric_value": Decimal("40"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )

    config = _base_config()
    with Session(engine) as session:
        result = PercentSumCheck(config, config.sum_rules[0]).run(
            CheckContext(ingestion_id=701, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    sample = result.evidence["findings_sample"][0]
    assert sample["code"] == "PERCENT_SUM_MISMATCH"
    assert sample["group_key"]["group_id"] == "Q1"


def test_percentage_checks_skip_when_no_percent_rows() -> None:
    """Checks should skip when dataset has no percentage rows in scope."""

    engine = _make_engine()
    table = _create_percentage_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 702,
                    "source_id": "SRC_MTC",
                    "lineage_ref_id": 301,
                    "group_id": "Q1",
                    "metric_key": "mentions",
                    "metric_value": Decimal("500"),
                    "unit": "count",
                    "status": "ok",
                }
            ],
        )

    config = _base_config()
    with Session(engine) as session:
        bounds_result = PercentBoundsCheck(config).run(
            CheckContext(ingestion_id=702, resources={"session": session})
        )
        sum_result = PercentSumCheck(config, config.sum_rules[0]).run(
            CheckContext(ingestion_id=702, resources={"session": session})
        )

    assert bounds_result.status == CheckStatus.SKIP
    assert sum_result.status == CheckStatus.SKIP


def test_percentage_checks_pass_for_consistent_values() -> None:
    """Checks should pass when percent values are in bounds and grouped sums reconcile."""

    engine = _make_engine()
    table = _create_percentage_table(engine)
    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 703,
                    "source_id": "SRC_SOCIAL_OK",
                    "lineage_ref_id": 401,
                    "group_id": "Q_OK",
                    "metric_key": "a",
                    "metric_value": Decimal("55"),
                    "unit": "percent",
                    "status": "ok",
                },
                {
                    "id": 2,
                    "ingestion_id": 703,
                    "source_id": "SRC_SOCIAL_OK",
                    "lineage_ref_id": 402,
                    "group_id": "Q_OK",
                    "metric_key": "b",
                    "metric_value": Decimal("45"),
                    "unit": "percent",
                    "status": "ok",
                },
            ],
        )

    config = _base_config()
    with Session(engine) as session:
        bounds_result = PercentBoundsCheck(config).run(
            CheckContext(ingestion_id=703, resources={"session": session})
        )
        sum_result = PercentSumCheck(config, config.sum_rules[0]).run(
            CheckContext(ingestion_id=703, resources={"session": session})
        )

    assert bounds_result.status == CheckStatus.PASS
    assert sum_result.status == CheckStatus.PASS


def test_percentage_loader_and_builder_read_yaml_contract(tmp_path: Path) -> None:
    """Loader and builder should parse YAML config and materialize checks."""

    yaml_path = tmp_path / "datasets.yml"
    yaml_path.write_text(
        dedent(
            """
            datasets: []
            percentage_checks:
              - dataset_id: pct_social
                table: stg_social_metrics
                severity: warning
                ingestion_id_column: ingestion_id
                source_id_column: source_id
                lineage_ref_id_column: lineage_ref_id
                value_column: metric_value
                unit_column: unit
                percent_units: [percent]
                status_column: status
                allowed_statuses: [ok]
                require_lineage: true
                lower_bound: 0
                upper_bound: 100
                sum_rules:
                  - rule_id: by_slide
                    group_by: [source_id, ingestion_id, slide_number]
                    target_sum: 100
                    tolerance: 1
                    min_items: 2
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    configs = load_percentage_check_configs(yaml_path)
    checks = build_percentage_checks(configs)

    assert len(configs) == 1
    assert configs[0].dataset_id == "pct_social"
    assert configs[0].severity == Severity.WARNING
    assert len(checks) == 2
    check_ids = {check.check_id for check in checks}
    assert "dq.percent.bounds.pct_social" in check_ids
    assert "dq.percent.sum.pct_social.by_slide" in check_ids
