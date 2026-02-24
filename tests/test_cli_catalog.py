"""Unit tests for ingestion operational catalog CLI."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine


BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind  # noqa: E402
from etl import cli_catalog  # noqa: E402


def make_engine():
    """Create isolated in-memory SQLite engine for CLI tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def create_registry_tables(engine) -> None:  # noqa: ANN001
    """Create only ETL registry tables required by catalog CLI."""
    SQLModel.metadata.create_all(
        engine,
        tables=[Source.__table__, IngestionRun.__table__],
    )


def test_catalog_report_cli_generates_markdown_and_json_with_filters(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI writes reports and applies status/kind filters without code edits."""
    engine = make_engine()
    create_registry_tables(engine)

    with Session(engine) as session:
        src_pdf_ok = Source(source_id="SRC_PDF_OK", kind=SourceKind.PDF, uri="file:///ok.pdf")
        src_pdf_fail = Source(source_id="SRC_PDF_FAIL", kind=SourceKind.PDF, uri="file:///fail.pdf")
        src_xlsx_ok = Source(source_id="SRC_XLSX_OK", kind=SourceKind.XLSX, uri="file:///ok.xlsx")
        session.add(src_pdf_ok)
        session.add(src_pdf_fail)
        session.add(src_xlsx_ok)
        session.commit()
        session.refresh(src_pdf_ok)
        session.refresh(src_pdf_fail)
        session.refresh(src_xlsx_ok)

        session.add(
            IngestionRun(
                source_pk=src_pdf_ok.id,
                status=IngestionStatus.SUCCESS,
                extractor_name="extract_pdf_ok",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_pdf_fail.id,
                status=IngestionStatus.FAILED,
                extractor_name="extract_pdf_fail",
            )
        )
        session.add(
            IngestionRun(
                source_pk=src_xlsx_ok.id,
                status=IngestionStatus.SUCCESS,
                extractor_name="extract_xlsx_ok",
            )
        )
        session.commit()

    monkeypatch.setattr(cli_catalog, "engine", engine)
    out_md = tmp_path / "catalog.md"
    out_json = tmp_path / "catalog.json"
    rc = cli_catalog.main(
        [
            "catalog:report",
            "--out-md",
            str(out_md),
            "--out-json",
            str(out_json),
            "--status",
            "success",
            "--kind",
            "pdf",
        ]
    )

    assert rc == 0
    assert out_md.exists()
    assert out_json.exists()

    markdown = out_md.read_text(encoding="utf-8")
    payload = json.loads(out_json.read_text(encoding="utf-8"))

    assert "filters.status: success" in markdown
    assert "filters.source_kind: pdf" in markdown
    assert "| SRC_PDF_OK | pdf |" in markdown

    assert payload["filters"]["status"] == ["success"]
    assert payload["filters"]["source_kind"] == ["pdf"]
    assert payload["summary"]["total_sources"] == 1
    assert payload["summary"]["latest_status_counts"] == {"success": 1}
    assert [item["source_id"] for item in payload["sources"]] == ["SRC_PDF_OK"]


def test_catalog_report_requires_at_least_one_output_path() -> None:
    """Catalog runner rejects execution when no output destination is informed."""
    with pytest.raises(ValueError, match="--out-md e/ou --out-json"):
        cli_catalog.run_catalog_report(out_md=None, out_json=None)
