"""Unit tests for ETL registry service (`sources` + `ingestions`)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind
from app.services.etl_registry_service import (
    enforce_lineage_policy,
    finish_ingestion_run,
    register_source_from_path,
    start_ingestion_run,
)


def make_engine():
    """Create isolated in-memory SQLite engine for service unit tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_registry_tables(engine) -> None:  # noqa: ANN001
    """Create only ETL registry tables required by these tests."""
    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__],
    )


def test_register_source_from_path_is_idempotent(tmp_path: Path) -> None:
    """Registering same `source_id` twice updates source without duplicating rows."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "optin.csv"
    source_file.write_text("id,nome\n1,alice\n", encoding="utf-8")

    with Session(engine) as session:
        first = register_source_from_path(session, "src_optin_001", source_file)
        assert first.id is not None
        assert first.source_id == "SRC_OPTIN_001"
        assert first.file_size_bytes is not None
        assert first.file_sha256 is not None

        first_hash = first.file_sha256
        source_file.write_text("id,nome\n1,alice\n2,bob\n", encoding="utf-8")
        second = register_source_from_path(session, "SRC_OPTIN_001", source_file)

        assert second.id == first.id
        assert second.file_sha256 != first_hash

        total = session.exec(select(Source)).all()
        assert len(total) == 1


def test_start_and_finish_ingestion_run_persists_status_and_timestamps(tmp_path: Path) -> None:
    """Service creates and finalizes ingestion runs with timestamps and notes."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "acesso.pdf"
    source_file.write_bytes(b"fake-pdf-content")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_ACESSO_001", source_file)
        run = start_ingestion_run(session, source.source_id, "extract_pdf_access")

        assert run.id is not None
        assert run.source_pk == source.id
        assert run.extractor_name == "extract_pdf_access"
        assert run.status == IngestionStatus.PARTIAL
        assert run.started_at is not None
        assert run.finished_at is None

        finish_ingestion_run(
            session,
            ingestion_id=run.id,
            status=IngestionStatus.SUCCESS,
            notes="ingestao concluida sem inconsistencias",
        )

        persisted = session.get(IngestionRun, run.id)
        assert persisted is not None
        assert persisted.status == IngestionStatus.SUCCESS
        assert persisted.finished_at is not None
        assert persisted.notes == "ingestao concluida sem inconsistencias"


def test_register_source_from_path_fails_for_missing_file(tmp_path: Path) -> None:
    """Service raises FileNotFoundError when input path does not exist."""
    engine = make_engine()
    create_registry_tables(engine)

    missing = tmp_path / "nao_existe.xlsx"
    with Session(engine) as session:
        with pytest.raises(FileNotFoundError):
            register_source_from_path(session, "SRC_MISSING_FILE", missing)


def test_register_source_from_yaml_marks_config_kind(tmp_path: Path) -> None:
    """YAML sources should be registered as CONFIG for agenda/config audit."""

    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "agenda_master.yml"
    source_file.write_text("version: 1\nsessions: []\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_CONFIG_AGENDA_TEST", source_file)
        assert source.kind == SourceKind.CONFIG


def test_start_ingestion_run_requires_registered_source() -> None:
    """Service rejects ingestion start when `source_id` is not registered."""
    engine = make_engine()
    create_registry_tables(engine)

    with Session(engine) as session:
        with pytest.raises(ValueError, match="Fonte nao registrada"):
            start_ingestion_run(session, "SRC_UNKNOWN", "extract_xlsx_optin")


def test_enforce_lineage_policy_required_marks_partial_and_raises(tmp_path: Path) -> None:
    """Required policy marks run partial and blocks when lineage is missing."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "stg_show_12_12.csv"
    source_file.write_text("id,total\n1,10\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_STG_SHOW_12_12", source_file)
        run = start_ingestion_run(session, source.source_id, "load_stg_show")

        records = [
            {"metric_key": "show.publico", "lineage_ref_id": 101},
            {"metric_key": "show.publico", "lineage_ref_id": None},
        ]
        with pytest.raises(ValueError, match="exige linhagem"):
            enforce_lineage_policy(
                session,
                ingestion_id=run.id,
                dataset_name="stg_show_day_summary",
                records=records,
                policy="required",
                severity_on_missing="partial",
            )

        refreshed = session.get(IngestionRun, run.id)
        assert refreshed is not None
        assert refreshed.status == IngestionStatus.PARTIAL
        assert refreshed.finished_at is not None
        assert "stg_show_day_summary" in (refreshed.notes or "")
        assert "Como corrigir" in (refreshed.notes or "")


def test_enforce_lineage_policy_required_can_mark_failed(tmp_path: Path) -> None:
    """Required policy with failed severity marks run as FAILED on missing lineage."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "stg_show_14_12.csv"
    source_file.write_text("id,total\n1,12\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_STG_SHOW_14_12", source_file)
        run = start_ingestion_run(session, source.source_id, "load_stg_show")

        with pytest.raises(ValueError, match="exige linhagem"):
            enforce_lineage_policy(
                session,
                ingestion_id=run.id,
                dataset_name="stg_show_day_summary",
                records=[{"metric_key": "show.publico"}],
                policy="required",
                severity_on_missing="failed",
            )

        refreshed = session.get(IngestionRun, run.id)
        assert refreshed is not None
        assert refreshed.status == IngestionStatus.FAILED


def test_enforce_lineage_policy_optional_does_not_block(tmp_path: Path) -> None:
    """Optional policy allows records without lineage and does not update run."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "stg_optin_12_12.csv"
    source_file.write_text("id,total\n1,7\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_STG_OPTIN_12_12", source_file)
        run = start_ingestion_run(session, source.source_id, "load_stg_optin")
        enforce_lineage_policy(
            session,
            ingestion_id=run.id,
            dataset_name="stg_optin_events",
            records=[{"metric_key": "optin.total"}],
            policy="optional",
        )

        refreshed = session.get(IngestionRun, run.id)
        assert refreshed is not None
        assert refreshed.finished_at is None
        assert refreshed.notes is None


def test_enforce_lineage_policy_rejects_invalid_policy(tmp_path: Path) -> None:
    """Invalid policy configuration is rejected with actionable error."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "stg_invalid_policy.csv"
    source_file.write_text("id,total\n1,1\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_STG_INVALID_POLICY", source_file)
        run = start_ingestion_run(session, source.source_id, "load_stg_invalid")
        with pytest.raises(ValueError, match="policy invalida|policy em"):
            enforce_lineage_policy(
                session,
                ingestion_id=run.id,
                dataset_name="stg_invalid_policy",
                records=[],
                policy="must_have_lineage",
            )


def test_enforce_lineage_policy_rejects_invalid_severity(tmp_path: Path) -> None:
    """Invalid severity configuration is rejected with actionable error."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "stg_invalid_severity.csv"
    source_file.write_text("id,total\n1,1\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_STG_INVALID_SEVERITY", source_file)
        run = start_ingestion_run(session, source.source_id, "load_stg_invalid")
        with pytest.raises(ValueError, match="severity invalida|severity_on_missing"):
            enforce_lineage_policy(
                session,
                ingestion_id=run.id,
                dataset_name="stg_invalid_severity",
                records=[{"lineage_ref_id": None}],
                policy="required",
                severity_on_missing="warn",
            )
