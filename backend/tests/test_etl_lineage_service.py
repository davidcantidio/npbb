"""Unit tests for ETL lineage service helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.models.etl_lineage import LineageLocationType, LineageRef
from app.models.etl_registry import IngestionRun, Source
from app.services.etl_lineage_service import attach_lineage, create_lineage_ref
from app.services.etl_registry_service import register_source_from_path, start_ingestion_run


def make_engine():
    """Create isolated in-memory SQLite engine for lineage service tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_required_tables(engine) -> None:  # noqa: ANN001
    """Create only ETL registry + lineage tables required by this suite."""
    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__, LineageRef.__table__],
    )


def test_create_lineage_ref_persists_reference_for_aggregated_metric(tmp_path: Path) -> None:
    """Helper persists lineage with source, ingestion, canonical location and evidence."""
    engine = make_engine()
    create_required_tables(engine)

    source_file = tmp_path / "acesso_13_12.pdf"
    source_file.write_bytes(b"fake-pdf-content")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_ACESSO_13_12", source_file)
        run = start_ingestion_run(session, source.source_id, "extract_pdf_access")
        lineage = create_lineage_ref(
            session,
            source_id=source.source_id,
            ingestion_id=run.id,
            location_type="page",
            location_value="page:12",
            evidence_text="Tabela: Controle de acesso por sessao",
            is_aggregated_metric=True,
        )

        assert lineage.id is not None
        assert lineage.source_id == source.source_id
        assert lineage.ingestion_id == run.id
        assert lineage.location_type == LineageLocationType.PAGE
        assert lineage.location_value == "page:12"
        assert lineage.evidence_text == "Tabela: Controle de acesso por sessao"


def test_create_lineage_ref_requires_evidence_for_aggregated_metric(tmp_path: Path) -> None:
    """Aggregated metric lineage must provide evidence text."""
    engine = make_engine()
    create_required_tables(engine)

    source_file = tmp_path / "shows_14_12.xlsx"
    source_file.write_text("x", encoding="utf-8")

    with Session(engine) as session:
        source = register_source_from_path(session, "SRC_SHOWS_14_12", source_file)
        with pytest.raises(ValueError, match="evidence_text obrigatorio"):
            create_lineage_ref(
                session,
                source_id=source.source_id,
                location_type="sheet",
                location_value="sheet:resumo",
                evidence_text="",
                is_aggregated_metric=True,
            )


def test_create_lineage_ref_rejects_invalid_location_and_source_mismatch(tmp_path: Path) -> None:
    """Helper rejects invalid location format and source/ingestion mismatch."""
    engine = make_engine()
    create_required_tables(engine)

    file_a = tmp_path / "a.csv"
    file_b = tmp_path / "b.csv"
    file_a.write_text("a", encoding="utf-8")
    file_b.write_text("b", encoding="utf-8")

    with Session(engine) as session:
        source_a = register_source_from_path(session, "SRC_A", file_a)
        source_b = register_source_from_path(session, "SRC_B", file_b)
        run_a = start_ingestion_run(session, source_a.source_id, "extract_a")

        with pytest.raises(ValueError, match="location_value invalido para page"):
            create_lineage_ref(
                session,
                source_id=source_a.source_id,
                location_type="page",
                location_value="page:0",
                evidence_text="Tabela X",
            )

        with pytest.raises(ValueError, match="nao pertence ao source"):
            create_lineage_ref(
                session,
                source_id=source_b.source_id,
                ingestion_id=run_a.id,
                location_type="range",
                location_value="range:A1:D20",
                evidence_text="Tabela Y",
            )


def test_attach_lineage_adds_standard_field_to_dict() -> None:
    """Helper attaches `lineage_ref_id` on mutable dictionaries."""
    record = {"metric_key": "attendance.presentes"}
    updated = attach_lineage(record, 17)
    assert updated is record
    assert record["lineage_ref_id"] == 17


@dataclass
class _CanonicalRecord:
    metric_key: str
    lineage_ref_id: int | None = None


def test_attach_lineage_adds_standard_field_to_object() -> None:
    """Helper attaches `lineage_ref_id` on object-style records."""
    record = _CanonicalRecord(metric_key="attendance.presentes")
    updated = attach_lineage(record, 99)
    assert updated is record
    assert record.lineage_ref_id == 99


def test_attach_lineage_rejects_invalid_lineage_id() -> None:
    """Helper rejects non-positive lineage reference IDs."""
    with pytest.raises(ValueError, match="lineage_ref_id invalido"):
        attach_lineage({"metric_key": "m1"}, 0)


def test_attach_lineage_handles_pydantic_like_record_dump() -> None:
    """Helper supports pydantic-like records by returning dict with lineage ID."""

    class _PydanticLike:
        def model_dump(self):  # noqa: ANN201
            return {"metric_key": "ticket_sales.total"}

    output = attach_lineage(_PydanticLike(), 5)
    assert isinstance(output, dict)
    assert output["lineage_ref_id"] == 5
