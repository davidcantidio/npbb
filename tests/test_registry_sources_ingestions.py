"""Consolidated unit tests for source fingerprint and ETL registry lifecycle.

This suite validates hashing/metadata helpers and the source/ingestion service
contract in isolated SQLite databases.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import cast

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from core.registry import SourceFileNotFoundError
from core.utils.file_fingerprint import collect_file_metadata, compute_file_sha256


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from app.services.etl_registry_service import (  # noqa: E402
    finish_ingestion_run,
    register_source_from_path,
    start_ingestion_run,
)


def make_engine():
    """Create isolated in-memory SQLite engine for registry tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_registry_tables(engine) -> None:  # noqa: ANN001
    """Create only `sources` and `ingestions` tables used in this test suite."""
    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__],
    )


def test_compute_file_sha256_and_metadata_are_stable(tmp_path: Path) -> None:
    """Fingerprint helpers return deterministic hash and minimum metadata fields."""
    source_file = tmp_path / "source.csv"
    source_file.write_text("id,nome\n1,alice\n", encoding="utf-8")

    digest_1 = compute_file_sha256(source_file)
    digest_2 = compute_file_sha256(source_file)
    metadata = collect_file_metadata(source_file)

    assert digest_1 == digest_2
    assert len(digest_1) == 64
    assert metadata.file_size_bytes == source_file.stat().st_size
    assert Path(metadata.path) == source_file.resolve()
    assert metadata.file_mtime_utc.tzinfo is not None


def test_compute_file_sha256_missing_file_raises(tmp_path: Path) -> None:
    """Fingerprint helper raises actionable not-found error for absent files."""
    missing = tmp_path / "nao_existe.pdf"
    with pytest.raises(SourceFileNotFoundError):
        compute_file_sha256(missing)


def test_collect_file_metadata_missing_file_raises(tmp_path: Path) -> None:
    """Metadata helper raises actionable not-found error for absent files."""
    missing = tmp_path / "nao_existe.xlsx"
    with pytest.raises(SourceFileNotFoundError):
        collect_file_metadata(missing)


def test_register_source_start_and_finish_ingestion_run(tmp_path: Path) -> None:
    """Service registers source, starts ingestion and finalizes run with status."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "acesso_13_12.pdf"
    source_file.write_bytes(b"fake-pdf-content")

    with Session(engine) as session:
        source = register_source_from_path(session, "src_acesso_13_12", source_file)
        assert source.source_id == "SRC_ACESSO_13_12"
        assert source.kind == SourceKind.PDF
        assert source.file_sha256 is not None

        run = start_ingestion_run(
            session,
            source_id=source.source_id,
            extractor_name="extract_pdf_access_control",
        )
        assert run.status == IngestionStatus.PARTIAL
        assert run.started_at is not None

        finish_ingestion_run(
            session,
            ingestion_id=run.id,
            status=IngestionStatus.SUCCESS,
            notes="ingestao concluida",
        )
        persisted = session.get(IngestionRun, run.id)
        assert persisted is not None
        assert persisted.status == IngestionStatus.SUCCESS
        assert persisted.finished_at is not None
        assert persisted.notes == "ingestao concluida"


def test_register_source_is_idempotent_for_same_source_id(tmp_path: Path) -> None:
    """Registering same source ID updates existing source instead of duplicating rows."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "optin.xlsx"
    source_file.write_bytes(b"v1")

    with Session(engine) as session:
        first = register_source_from_path(session, "SRC_OPTIN_12", source_file)
        first_hash = first.file_sha256

        source_file.write_bytes(b"v2")
        second = register_source_from_path(session, "src_optin_12", source_file)

        assert first.id == second.id
        assert second.file_sha256 != first_hash
        assert len(session.exec(select(Source)).all()) == 1


def test_source_id_unique_constraint_is_enforced() -> None:
    """Database constraint prevents duplicate `source_id` inserts."""
    engine = make_engine()
    create_registry_tables(engine)

    with Session(engine) as session:
        session.add(Source(source_id="SRC_DUPLICADO", kind=SourceKind.CSV, uri="file:///a.csv"))
        session.commit()

        session.add(Source(source_id="SRC_DUPLICADO", kind=SourceKind.CSV, uri="file:///b.csv"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_finish_ingestion_run_with_invalid_status_fails(tmp_path: Path) -> None:
    """Invalid status values fail on persistence, preventing illegal transitions."""
    engine = make_engine()
    create_registry_tables(engine)

    source_file = tmp_path / "show_14_12.csv"
    source_file.write_text("id,total\n1,10\n", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_SHOW_14_12", source_file)
        run = start_ingestion_run(session, source.source_id, "extract_show_summary")

        with pytest.raises((IntegrityError, StatementError)):
            finish_ingestion_run(
                session,
                ingestion_id=run.id,
                status=cast(IngestionStatus, "INVALID_STATUS"),
                notes="status invalido",
            )
        session.rollback()


def test_start_ingestion_run_requires_existing_source() -> None:
    """Service rejects ingestion start when source is not registered."""
    engine = make_engine()
    create_registry_tables(engine)

    with Session(engine) as session:
        with pytest.raises(ValueError, match="Fonte nao registrada"):
            start_ingestion_run(session, "SRC_NAO_EXISTE", "extract_xlsx")
