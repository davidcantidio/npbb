"""Unit tests for schema and critical-not-null dataset checks."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from etl.validate.checks_not_null import NotNullCheck, build_not_null_checks
from etl.validate.checks_schema import (
    DatasetCheckConfig,
    SchemaCheck,
    build_schema_checks,
    load_dataset_check_configs,
)
from etl.validate.framework import CheckContext, CheckStatus, Severity


def _make_engine():
    """Create in-memory SQLite engine for isolated DQ check tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_schema_check_detects_missing_required_columns() -> None:
    """SchemaCheck should fail when expected columns do not exist in table."""

    engine = _make_engine()
    metadata = sa.MetaData()
    sa.Table(
        "stg_unit_schema",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
    )
    metadata.create_all(engine)

    config = DatasetCheckConfig(
        dataset_id="unit_schema",
        table="stg_unit_schema",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=("ingestion_id", "source_id", "lineage_ref_id"),
        critical_not_null_columns=("ingestion_id", "source_id"),
    )

    with Session(engine) as session:
        result = SchemaCheck(config).run(
            CheckContext(ingestion_id=7, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["dataset_id"] == "unit_schema"
    assert result.evidence["missing_columns"] == ["lineage_ref_id"]


def test_not_null_check_detects_critical_null_and_emits_lineage_hints() -> None:
    """NotNullCheck should fail on null keys and include source/lineage payload."""

    engine = _make_engine()
    metadata = sa.MetaData()
    table = sa.Table(
        "stg_unit_not_null",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("metric_value", sa.Integer(), nullable=True),
    )
    metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 77,
                    "source_id": "SRC_UNIT",
                    "lineage_ref_id": 101,
                    "metric_value": 25,
                },
                {
                    "id": 2,
                    "ingestion_id": 77,
                    "source_id": "SRC_UNIT",
                    "lineage_ref_id": 102,
                    "metric_value": None,
                },
            ],
        )

    config = DatasetCheckConfig(
        dataset_id="unit_not_null",
        table="stg_unit_not_null",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=(
            "ingestion_id",
            "source_id",
            "lineage_ref_id",
            "metric_value",
        ),
        critical_not_null_columns=("ingestion_id", "source_id", "lineage_ref_id", "metric_value"),
    )

    with Session(engine) as session:
        result = NotNullCheck(config).run(
            CheckContext(ingestion_id=77, resources={"session": session})
        )

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["null_critical_rows"] == 1
    assert result.lineage["source_id"] == "SRC_UNIT"
    assert result.lineage["lineage_ref_id"] == 102


def test_dataset_yaml_loader_supports_new_dataset_without_code_change(tmp_path: Path) -> None:
    """Loader should parse custom datasets and build checks dynamically."""

    yaml_path = tmp_path / "datasets.yml"
    yaml_path.write_text(
        dedent(
            """
            datasets:
              - dataset_id: custom_dataset
                table: custom_table
                domain: staging
                severity: warning
                required_columns:
                  - ingestion_id
                  - key_col
                critical_not_null_columns:
                  - ingestion_id
                  - key_col
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    configs = load_dataset_check_configs(yaml_path)
    schema_checks = build_schema_checks(configs)
    not_null_checks = build_not_null_checks(configs)

    assert len(configs) == 1
    assert configs[0].dataset_id == "custom_dataset"
    assert configs[0].severity == Severity.WARNING
    assert len(schema_checks) == 1
    assert schema_checks[0].check_id == "dq.schema.custom_dataset"
    assert len(not_null_checks) == 1
    assert not_null_checks[0].check_id == "dq.not_null.custom_dataset"


def test_not_null_check_skips_when_no_rows_in_scope() -> None:
    """NotNullCheck should skip when scoped ingestion has no table rows."""

    engine = _make_engine()
    metadata = sa.MetaData()
    sa.Table(
        "stg_unit_empty",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("metric_value", sa.Integer(), nullable=True),
    )
    metadata.create_all(engine)

    config = DatasetCheckConfig(
        dataset_id="unit_empty",
        table="stg_unit_empty",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=("ingestion_id", "source_id", "lineage_ref_id"),
        critical_not_null_columns=("ingestion_id", "source_id", "lineage_ref_id"),
    )

    with Session(engine) as session:
        result = NotNullCheck(config).run(
            CheckContext(ingestion_id=99, resources={"session": session})
        )

    assert result.status == CheckStatus.SKIP
    assert result.severity == Severity.INFO
    assert result.evidence["scoped_total_rows"] == 0
