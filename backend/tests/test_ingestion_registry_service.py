from __future__ import annotations

from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models.models import IngestionStatus, SourceKind
from app.services.ingestion_registry import (
    build_file_snapshot,
    finish_ingestion,
    normalize_source_id,
    register_source,
    start_ingestion,
)
from app.services.metric_lineage import normalize_location, register_metric_lineage


def make_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_normalize_source_id() -> None:
    assert normalize_source_id("src_pdf_teste") == "SRC_PDF_TESTE"
    assert normalize_source_id(" SRC PDF  teste ") == "SRC_PDF_TESTE"


def test_register_start_finish_ingestion(tmp_path: Path) -> None:
    engine = make_engine()
    SQLModel.metadata.create_all(engine)

    test_file = tmp_path / "a.txt"
    test_file.write_bytes(b"abc")
    snap = build_file_snapshot(test_file)
    assert len(snap.sha256) == 64
    assert snap.size_bytes == 3

    with Session(engine) as session:
        src = register_source(
            session,
            source_id="SRC_TEST_FILE",
            kind=SourceKind.CSV,
            uri=str(test_file),
            snapshot=snap,
        )
        assert src.source_id == "SRC_TEST_FILE"
        assert src.file_sha256 == snap.sha256

        run = start_ingestion(session, source_id="SRC_TEST_FILE", pipeline="tmj", snapshot=snap)
        assert run.id is not None
        assert run.status == IngestionStatus.RUNNING
        assert run.file_sha256 == snap.sha256

        finished = finish_ingestion(
            session,
            ingestion_id=run.id,
            status=IngestionStatus.SUCCEEDED,
            log_text="ok",
        )
        assert finished.status == IngestionStatus.SUCCEEDED
        assert finished.finished_at is not None
        assert finished.log_text == "ok"

        lineage = register_metric_lineage(
            session,
            metric_key="attendance.presentes",
            source_id="SRC_TEST_FILE",
            ingestion_id=run.id,
            location_raw="pagina 2",
            evidence="Tabela: Controle de acesso (resumo por sessao)",
            docx_section="Publico do evento",
        )
        assert lineage.id is not None
        assert lineage.source_id == "SRC_TEST_FILE"
        assert lineage.metric_key == "attendance.presentes"
        assert lineage.location_norm == "page:2"


def test_normalize_location_examples() -> None:
    assert normalize_location("pagina 12") == "page:12"
    assert normalize_location("p. 3") == "page:3"
    assert normalize_location("slide 4") == "slide:4"
    assert normalize_location("aba Entidades") == "sheet:entidades"
    assert normalize_location("A1:D20") == "range:A1:D20"
