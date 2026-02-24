"""Tests for PPTX social metrics extractor and staging loader."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select
import yaml

from etl.extract.pptx_mapping import load_pptx_mapping
from etl.extract import pptx_social_metrics


pptx = pytest.importorskip("pptx")

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_lineage import LineageRef  # noqa: E402
from app.models.etl_registry import IngestionRun, IngestionStatus, Source  # noqa: E402
from app.models.models import EventSession  # noqa: E402
from app.models.stg_social_metrics import StgSocialMetric  # noqa: E402


def _make_engine():
    """Create isolated in-memory SQLite engine for staging tests."""
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _create_required_tables(engine) -> None:  # noqa: ANN001
    """Create minimal registry + lineage + social staging tables."""
    SQLModel.metadata.create_all(
        engine,
        tables=[
            Source.__table__,
            IngestionRun.__table__,
            LineageRef.__table__,
            EventSession.__table__,
            StgSocialMetric.__table__,
        ],
    )


def _write_sample_social_pptx(path: Path) -> None:
    """Create PPTX fixture with social metrics labels in slide text blocks."""
    presentation = pptx.Presentation()

    slide1 = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide1.shapes.title.text = "Midias e Alcance"
    body1 = slide1.placeholders[1].text_frame
    body1.clear()
    body1.paragraphs[0].text = "Alcance total: 1.234"
    body1.add_paragraph().text = "Taxa de engajamento: 12,5%"

    slide2 = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide2.shapes.title.text = "Social Listening"
    body2 = slide2.placeholders[1].text_frame
    body2.clear()
    body2.paragraphs[0].text = "Sentimento positivo: 78%"

    presentation.save(path)


def _write_mapping(path: Path, rules: list[dict[str, object]]) -> None:
    """Write temporary mapping YAML for social metrics extraction tests."""
    payload = {
        "schema_version": "1.0",
        "rules": rules,
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_extract_social_metrics_returns_metric_rows_with_slide_lineage(tmp_path: Path) -> None:
    """Extractor should parse mapped metrics and include slide lineage fields."""
    pptx_path = tmp_path / "social_metrics.pptx"
    mapping_path = tmp_path / "mapping.yml"
    _write_sample_social_pptx(pptx_path)
    _write_mapping(
        mapping_path,
        rules=[
            {
                "metric_name": "media_reach_total",
                "platform": "instagram",
                "unit": "count",
                "slide_number": 1,
                "extraction_rule": "label:Alcance total | parse:first_integer",
            },
            {
                "metric_name": "social_engagement_rate",
                "platform": "instagram",
                "unit": "percent",
                "slide_number": 1,
                "extraction_rule": "label:Taxa de engajamento | parse:first_percent",
            },
        ],
    )
    rules = load_pptx_mapping(mapping_path).rules

    rows = list(pptx_social_metrics.extract_social_metrics(pptx_path, rules))

    assert len(rows) == 2
    by_metric = {row["metric_name"]: row for row in rows}
    assert by_metric["media_reach_total"]["metric_value"] == Decimal("1234")
    assert by_metric["media_reach_total"]["slide_number"] == 1
    assert by_metric["media_reach_total"]["lineage_location"] == "slide:1"
    assert by_metric["social_engagement_rate"]["metric_value"] == Decimal("12.5")
    assert by_metric["social_engagement_rate"]["unit"] == "percent"


def test_load_social_metrics_to_staging_persists_rows_and_lineage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should persist social metrics with ingestion and lineage refs."""
    pptx_path = tmp_path / "social_metrics_load.pptx"
    mapping_path = tmp_path / "mapping.yml"
    _write_sample_social_pptx(pptx_path)
    _write_mapping(
        mapping_path,
        rules=[
            {
                "metric_name": "media_reach_total",
                "platform": "instagram",
                "unit": "count",
                "slide_number": 1,
                "extraction_rule": "label:Alcance total | parse:first_integer",
            },
            {
                "metric_name": "social_engagement_rate",
                "platform": "instagram",
                "unit": "percent",
                "slide_number": 1,
                "extraction_rule": "label:Taxa de engajamento | parse:first_percent",
            },
            {
                "metric_name": "social_positive_sentiment",
                "platform": "social_listening",
                "unit": "percent",
                "slide_number": 2,
                "extraction_rule": "label:Sentimento positivo | parse:first_percent",
            },
        ],
    )
    rules = load_pptx_mapping(mapping_path).rules

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pptx_social_metrics, "engine", engine)

    summary = pptx_social_metrics.load_social_metrics_to_staging(
        source_id="src_social_metrics_ok_doze",
        pptx_path=pptx_path,
        mapping_rules=rules,
        lineage_policy="required",
        severity_on_missing="failed",
        drift_severity="partial",
    )

    assert summary["source_id"] == "SRC_SOCIAL_METRICS_OK_DOZE"
    assert summary["metrics_loaded"] == 3
    assert summary["drift_count"] == 0
    assert summary["status"] == IngestionStatus.SUCCESS.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.SUCCESS

        rows = session.exec(select(StgSocialMetric).order_by(StgSocialMetric.id)).all()
        assert len(rows) == 3
        assert all(row.lineage_ref_id > 0 for row in rows)
        assert all(row.session_id is not None for row in rows)
        assert all(row.location_value.startswith("slide:") for row in rows)


def test_load_social_metrics_marks_partial_when_label_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should mark ingestion as partial when drift severity is partial."""
    pptx_path = tmp_path / "social_metrics_partial.pptx"
    mapping_path = tmp_path / "mapping.yml"
    _write_sample_social_pptx(pptx_path)
    _write_mapping(
        mapping_path,
        rules=[
            {
                "metric_name": "media_reach_total",
                "platform": "instagram",
                "unit": "count",
                "slide_number": 1,
                "extraction_rule": "label:Alcance total | parse:first_integer",
            },
            {
                "metric_name": "missing_metric",
                "platform": "instagram",
                "unit": "count",
                "slide_number": 1,
                "extraction_rule": "label:Label inexistente | parse:first_integer",
            },
        ],
    )
    rules = load_pptx_mapping(mapping_path).rules

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pptx_social_metrics, "engine", engine)

    summary = pptx_social_metrics.load_social_metrics_to_staging(
        source_id="src_social_metrics_partial_doze",
        pptx_path=pptx_path,
        mapping_rules=rules,
        drift_severity="partial",
    )

    assert summary["source_id"] == "SRC_SOCIAL_METRICS_PARTIAL_DOZE"
    assert summary["metrics_loaded"] == 1
    assert summary["drift_count"] == 1
    assert summary["status"] == IngestionStatus.PARTIAL.value

    with Session(engine) as session:
        run = session.get(IngestionRun, summary["ingestion_id"])
        assert run is not None
        assert run.status == IngestionStatus.PARTIAL
        assert run.notes and "Drift de layout" in run.notes


def test_load_social_metrics_fails_when_label_is_missing_and_drift_is_failed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader should fail ingestion when drift severity is configured as failed."""
    pptx_path = tmp_path / "social_metrics_failed.pptx"
    mapping_path = tmp_path / "mapping.yml"
    _write_sample_social_pptx(pptx_path)
    _write_mapping(
        mapping_path,
        rules=[
            {
                "metric_name": "missing_metric",
                "platform": "instagram",
                "unit": "count",
                "slide_number": 1,
                "extraction_rule": "label:Label inexistente | parse:first_integer",
            }
        ],
    )
    rules = load_pptx_mapping(mapping_path).rules

    engine = _make_engine()
    _create_required_tables(engine)
    monkeypatch.setattr(pptx_social_metrics, "engine", engine)

    with pytest.raises(ValueError, match="Drift de layout detectado"):
        pptx_social_metrics.load_social_metrics_to_staging(
            source_id="src_social_metrics_failed_doze",
            pptx_path=pptx_path,
            mapping_rules=rules,
            drift_severity="failed",
        )

    with Session(engine) as session:
        runs = session.exec(select(IngestionRun).order_by(IngestionRun.id.desc())).all()
        assert runs
        assert runs[0].status == IngestionStatus.FAILED
