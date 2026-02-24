"""Unit tests for deterministic report chart rendering."""

from __future__ import annotations

from pathlib import Path

import pytest

from reports.charts import (
    ChartRenderError,
    ChartSeries,
    ChartSpec,
    ChartType,
    render_chart_png,
)


def _sample_rows() -> list[dict[str, object]]:
    """Return deterministic sample rows used by chart tests."""

    return [
        {"dia": "2025-12-12", "presentes": 120, "comparecimento": 0.80},
        {"dia": "2025-12-13", "presentes": 180, "comparecimento": 0.90},
        {"dia": "2025-12-14", "presentes": 150, "comparecimento": 0.75},
    ]


def test_render_chart_png_bar_is_deterministic() -> None:
    """Bar renderer should produce equal PNG bytes for identical input."""

    spec = ChartSpec(
        chart_type=ChartType.BAR,
        title="Presencas por dia",
        x_label="Dia",
        y_label="Presentes",
        series=(
            ChartSeries(name="Entradas validadas", x_field="dia", y_field="presentes"),
        ),
    )

    png_a = render_chart_png(spec, _sample_rows())
    png_b = render_chart_png(spec, _sample_rows())

    assert isinstance(png_a, bytes)
    assert png_a[:8] == b"\x89PNG\r\n\x1a\n"
    assert png_a == png_b


def test_render_chart_png_line_is_deterministic() -> None:
    """Line renderer should produce equal PNG bytes for identical input."""

    spec = ChartSpec(
        chart_type=ChartType.LINE,
        title="Comparecimento por dia",
        x_label="Dia",
        y_label="Percentual",
        series=(
            ChartSeries(name="Comparecimento", x_field="dia", y_field="comparecimento"),
        ),
    )

    png_a = render_chart_png(spec, _sample_rows())
    png_b = render_chart_png(spec, _sample_rows())

    assert isinstance(png_a, bytes)
    assert png_a[:8] == b"\x89PNG\r\n\x1a\n"
    assert png_a == png_b


def test_render_chart_png_writes_file_when_output_path_is_provided(tmp_path: Path) -> None:
    """Renderer should write deterministic PNG file when output path is set."""

    spec = ChartSpec(
        chart_type=ChartType.BAR,
        title="Presencas por dia",
        x_label="Dia",
        y_label="Presentes",
        series=(
            ChartSeries(name="Entradas validadas", x_field="dia", y_field="presentes"),
        ),
    )
    output_path = tmp_path / "charts" / "attendance.png"

    result = render_chart_png(spec, _sample_rows(), output_path=output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_chart_png_raises_for_non_numeric_y_values() -> None:
    """Renderer should fail with actionable error for invalid numeric values."""

    spec = ChartSpec(
        chart_type=ChartType.LINE,
        title="Comparecimento por dia",
        x_label="Dia",
        y_label="Percentual",
        series=(
            ChartSeries(name="Comparecimento", x_field="dia", y_field="comparecimento"),
        ),
    )

    rows = [{"dia": "2025-12-12", "comparecimento": "n/a"}]
    with pytest.raises(ChartRenderError, match="Valor numerico invalido"):
        render_chart_png(spec, rows)
