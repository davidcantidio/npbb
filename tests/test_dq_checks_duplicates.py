"""Unit tests for duplicate-key checks driven by dataset configuration."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from etl.validate.checks_duplicates import (
    DuplicateCheck,
    DuplicateCheckSpec,
    build_duplicate_checks,
)
from etl.validate.checks_schema import DatasetCheckConfig, load_dataset_check_configs
from etl.validate.framework import CheckContext, CheckStatus, Severity


def _make_engine():
    """Create in-memory SQLite engine for isolated duplicate check tests."""

    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_duplicate_check_detects_duplicates_and_limits_sample_size() -> None:
    """DuplicateCheck should detect duplicate groups and limit evidence sample."""

    engine = _make_engine()
    metadata = sa.MetaData()
    table = sa.Table(
        "stg_dup_optin",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("cpf_hash", sa.String(64), nullable=True),
        sa.Column("evento", sa.String(200), nullable=True),
        sa.Column("sessao", sa.String(200), nullable=True),
    )
    metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_A",
                    "lineage_ref_id": 901,
                    "cpf_hash": "CPF_DUP_A",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 13/12",
                },
                {
                    "id": 2,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_A",
                    "lineage_ref_id": 902,
                    "cpf_hash": "CPF_DUP_A",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 13/12",
                },
                {
                    "id": 3,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_A",
                    "lineage_ref_id": 903,
                    "cpf_hash": "CPF_DUP_A",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 13/12",
                },
                {
                    "id": 4,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_B",
                    "lineage_ref_id": 904,
                    "cpf_hash": "CPF_DUP_B",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 14/12",
                },
                {
                    "id": 5,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_B",
                    "lineage_ref_id": 905,
                    "cpf_hash": "CPF_DUP_B",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 14/12",
                },
                {
                    "id": 6,
                    "ingestion_id": 700,
                    "source_id": "SRC_OPTIN_C",
                    "lineage_ref_id": 906,
                    "cpf_hash": "CPF_OK",
                    "evento": "TMJ 2025",
                    "sessao": "SHOW 12/12",
                },
            ],
        )

    config = DatasetCheckConfig(
        dataset_id="dup_optin",
        table="stg_dup_optin",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=("ingestion_id", "source_id", "lineage_ref_id"),
        critical_not_null_columns=("ingestion_id",),
        duplicate_key_sets=(("cpf_hash", "evento", "sessao"),),
    )
    check = DuplicateCheck(
        DuplicateCheckSpec(
            dataset_config=config,
            key_columns=("cpf_hash", "evento", "sessao"),
        ),
        sample_limit=1,
    )

    with Session(engine) as session:
        result = check.run(CheckContext(ingestion_id=700, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert result.evidence["duplicate_group_count"] == 2
    assert result.evidence["duplicate_total_rows"] == 5
    assert result.evidence["duplicate_excess_rows"] == 3
    assert len(result.evidence["sample_duplicates"]) == 1
    assert result.lineage["source_id"] == "SRC_OPTIN_A"
    assert result.lineage["lineage_ref_id"] == 901


def test_duplicate_check_passes_when_no_duplicates() -> None:
    """DuplicateCheck should pass when no duplicate group is found."""

    engine = _make_engine()
    metadata = sa.MetaData()
    table = sa.Table(
        "stg_dup_leads",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("email_hash", sa.String(64), nullable=True),
        sa.Column("evento", sa.String(200), nullable=True),
    )
    metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(
            table.insert(),
            [
                {
                    "id": 1,
                    "ingestion_id": 900,
                    "source_id": "SRC_LEADS_A",
                    "lineage_ref_id": 1001,
                    "email_hash": "A",
                    "evento": "TMJ 2025",
                },
                {
                    "id": 2,
                    "ingestion_id": 900,
                    "source_id": "SRC_LEADS_A",
                    "lineage_ref_id": 1002,
                    "email_hash": "B",
                    "evento": "TMJ 2025",
                },
            ],
        )

    config = DatasetCheckConfig(
        dataset_id="dup_leads",
        table="stg_dup_leads",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=("ingestion_id", "source_id", "lineage_ref_id"),
        critical_not_null_columns=("ingestion_id",),
        duplicate_key_sets=(("email_hash", "evento"),),
    )
    check = DuplicateCheck(
        DuplicateCheckSpec(dataset_config=config, key_columns=("email_hash", "evento"))
    )

    with Session(engine) as session:
        result = check.run(CheckContext(ingestion_id=900, resources={"session": session}))

    assert result.status == CheckStatus.PASS
    assert result.severity == Severity.INFO
    assert result.evidence["duplicate_group_count"] == 0
    assert result.evidence["sample_duplicates"] == []


def test_duplicate_check_fails_when_config_references_missing_columns() -> None:
    """DuplicateCheck should fail with actionable message for bad key config."""

    engine = _make_engine()
    metadata = sa.MetaData()
    sa.Table(
        "stg_dup_bad_config",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingestion_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.String(160), nullable=False),
        sa.Column("lineage_ref_id", sa.Integer(), nullable=False),
        sa.Column("cpf_hash", sa.String(64), nullable=True),
    )
    metadata.create_all(engine)

    config = DatasetCheckConfig(
        dataset_id="dup_bad_config",
        table="stg_dup_bad_config",
        domain="staging",
        severity=Severity.ERROR,
        required_columns=("ingestion_id", "source_id"),
        critical_not_null_columns=("ingestion_id",),
        duplicate_key_sets=(("cpf_hash", "evento"),),
    )
    check = DuplicateCheck(
        DuplicateCheckSpec(dataset_config=config, key_columns=("cpf_hash", "evento"))
    )

    with Session(engine) as session:
        result = check.run(CheckContext(ingestion_id=321, resources={"session": session}))

    assert result.status == CheckStatus.FAIL
    assert result.severity == Severity.ERROR
    assert "evento" in result.evidence["missing_columns"]


def test_build_duplicate_checks_from_yaml(tmp_path: Path) -> None:
    """Builder should create one check per duplicate key set in YAML."""

    yaml_path = tmp_path / "datasets.yml"
    yaml_path.write_text(
        dedent(
            """
            datasets:
              - dataset_id: stg_optin_custom
                table: stg_optin_transactions
                domain: staging
                severity: error
                required_columns:
                  - ingestion_id
                  - source_id
                critical_not_null_columns:
                  - ingestion_id
                duplicate_key_sets:
                  - [cpf_hash, evento, sessao]
                  - [email_hash, evento, sessao]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    configs = load_dataset_check_configs(yaml_path)
    checks = build_duplicate_checks(configs, sample_limit=3)
    check_ids = {check.check_id for check in checks}
    assert len(checks) == 2
    assert "dq.duplicates.stg_optin_custom.cpf_hash_evento_sessao" in check_ids
    assert "dq.duplicates.stg_optin_custom.email_hash_evento_sessao" in check_ids
