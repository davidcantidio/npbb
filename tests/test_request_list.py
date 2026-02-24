"""Unit tests for missing-artifacts request list generation."""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
import io
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.etl_registry import CoverageDataset  # noqa: E402
from app.models.models import EventSessionType  # noqa: E402
from etl.validate.framework import Severity  # noqa: E402
from etl.validate.request_list import (  # noqa: E402
    build_missing_artifacts_list,
    render_missing_artifacts_csv,
    render_missing_artifacts_markdown,
)
from etl.validate.show_coverage_evaluator import (  # noqa: E402
    CoverageMissingInput,
    CoverageReport,
)


def _build_report_fixture() -> CoverageReport:
    """Create one coverage report fixture with show/day mixed gaps."""

    missing_inputs = (
        CoverageMissingInput(
            session_id=10,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
            session_type=EventSessionType.NOTURNO_SHOW,
            dataset=CoverageDataset.ACCESS_CONTROL,
            status="gap",
            severity=Severity.ERROR,
            reason_code="missing_in_catalog",
            reason="Nenhuma fonte correspondente foi encontrada no catalogo.",
            expected_artifact="PDF de controle de acesso da sessao de show.",
            request_action="Solicitar: PDF de controle de acesso da sessao de show.",
            sources_considered=(),
            source_statuses=(),
            source_match_scopes=(),
            lineage_note="Motivo derivado de ausencia no catalogo.",
        ),
        CoverageMissingInput(
            session_id=10,
            session_key="TMJ2025_20251212_SHOW",
            session_date=date(2025, 12, 12),
            session_type=EventSessionType.NOTURNO_SHOW,
            dataset=CoverageDataset.OPTIN,
            status="partial",
            severity=Severity.WARNING,
            reason_code="ingestion_partial",
            reason="Fonte encontrada, mas a ultima ingestao terminou como partial.",
            expected_artifact="XLSX de opt-in/Eventim da sessao de show.",
            request_action="Reprocessar extractor de opt-in.",
            sources_considered=("SRC_OPTIN_NOTURNO_DOZE",),
            source_statuses=("partial",),
            source_match_scopes=("day_type",),
            lineage_note="Motivo derivado de divergencia entre coverage_matrix e catalogo.",
        ),
        CoverageMissingInput(
            session_id=99,
            session_key="TMJ2025_20251212_DIURNO",
            session_date=date(2025, 12, 12),
            session_type=EventSessionType.DIURNO_GRATUITO,
            dataset=CoverageDataset.LEADS,
            status="gap",
            severity=Severity.WARNING,
            reason_code="missing_in_catalog",
            reason="Nenhuma fonte correspondente foi encontrada no catalogo.",
            expected_artifact="XLSX de leads da programacao diurna.",
            request_action="Solicitar: XLSX de leads da programacao diurna.",
            sources_considered=(),
            source_statuses=(),
            source_match_scopes=(),
            lineage_note="Motivo derivado de ausencia no catalogo.",
        ),
    )
    return CoverageReport(
        generated_at=datetime.now(timezone.utc),
        event_id=2025,
        contract_version=1,
        status="gap",
        summary={
            "total_sessions": 2,
            "ok_sessions": 0,
            "partial_sessions": 1,
            "gap_sessions": 1,
            "total_missing_inputs": 3,
            "gap_missing_inputs": 2,
            "partial_missing_inputs": 1,
        },
        sessions=(),
        missing_inputs=missing_inputs,
    )


def test_build_missing_artifacts_list_filters_show_gaps_only_by_default() -> None:
    """Builder should keep only NOTURNO_SHOW items with status `gap` by default."""

    report = _build_report_fixture()
    items = build_missing_artifacts_list(report)

    assert len(items) == 1
    assert items[0].dia.isoformat() == "2025-12-12"
    assert items[0].sessao == "TMJ2025_20251212_SHOW"
    assert items[0].dataset == "access_control"
    assert "Acao sugerida:" in items[0].justificativa


def test_build_missing_artifacts_list_can_include_partial_show_findings() -> None:
    """Builder should include show partial rows when `include_partial=True`."""

    report = _build_report_fixture()
    items = build_missing_artifacts_list(report, include_partial=True)

    assert len(items) == 2
    datasets = [item.dataset for item in items]
    assert datasets == ["access_control", "optin"]


def test_render_missing_artifacts_outputs_have_required_columns() -> None:
    """Markdown and CSV renderers should expose fixed request-list columns."""

    report = _build_report_fixture()
    items = build_missing_artifacts_list(report, include_partial=True)

    markdown = render_missing_artifacts_markdown(items)
    assert "| dia | sessao | dataset | artefato_esperado | justificativa |" in markdown
    assert "TMJ2025_20251212_SHOW" in markdown
    assert "XLSX de opt-in/Eventim da sessao de show." in markdown

    csv_text = render_missing_artifacts_csv(items)
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    assert len(rows) == 2
    assert rows[0]["dia"] == "2025-12-12"
    assert rows[0]["sessao"] == "TMJ2025_20251212_SHOW"
    assert rows[0]["dataset"] in {"access_control", "optin"}
    assert rows[0]["artefato_esperado"]
    assert rows[0]["justificativa"]

