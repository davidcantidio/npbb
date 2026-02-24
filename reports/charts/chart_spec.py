"""Chart specification contracts for report figure rendering.

This module defines typed chart contracts used by renderers to generate
deterministic PNG figures from tabular mart/view rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ChartType(str, Enum):
    """Supported chart types for report figures."""

    BAR = "bar"
    LINE = "line"


@dataclass(frozen=True)
class ChartSeries:
    """Series contract for one chart trace.

    Args:
        name: Display name used in legend.
        x_field: Source field used for x categories.
        y_field: Source field used for y numeric values.
        color: Optional hex color override (`#RRGGBB`).

    Raises:
        ValueError: If required fields are empty.
    """

    name: str
    x_field: str
    y_field: str
    color: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("ChartSeries.name deve ser texto nao vazio.")
        if not self.x_field.strip():
            raise ValueError("ChartSeries.x_field deve ser texto nao vazio.")
        if not self.y_field.strip():
            raise ValueError("ChartSeries.y_field deve ser texto nao vazio.")


@dataclass(frozen=True)
class ChartFormat:
    """Visual format contract for deterministic chart rendering.

    Minimal visual standard:
    - canvas: `1280x720`;
    - font: Pillow default bitmap font;
    - colors: fixed palette and neutral background;
    - margins: fixed paddings to stabilize axis/titles.

    Args:
        width_px: Canvas width in pixels.
        height_px: Canvas height in pixels.
        margin_left: Plot left margin.
        margin_right: Plot right margin.
        margin_top: Plot top margin.
        margin_bottom: Plot bottom margin.
        background_color: Canvas background color.
        axis_color: Axis color.
        grid_color: Grid line color.
        palette: Default color palette used when series color is omitted.
        line_width: Line chart stroke width.
        marker_radius: Line chart marker radius.

    Raises:
        ValueError: If any numeric field is invalid.
    """

    width_px: int = 1280
    height_px: int = 720
    margin_left: int = 100
    margin_right: int = 60
    margin_top: int = 90
    margin_bottom: int = 100
    background_color: str = "#FFFFFF"
    axis_color: str = "#1F2937"
    grid_color: str = "#D1D5DB"
    palette: tuple[str, ...] = (
        "#1F77B4",
        "#FF7F0E",
        "#2CA02C",
        "#D62728",
        "#9467BD",
    )
    line_width: int = 3
    marker_radius: int = 4

    def __post_init__(self) -> None:
        numeric_fields = {
            "width_px": self.width_px,
            "height_px": self.height_px,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "line_width": self.line_width,
            "marker_radius": self.marker_radius,
        }
        for field_name, value in numeric_fields.items():
            if int(value) <= 0:
                raise ValueError(f"ChartFormat.{field_name} deve ser inteiro positivo.")
        if not self.palette:
            raise ValueError("ChartFormat.palette deve conter ao menos uma cor.")


@dataclass(frozen=True)
class ChartSpec:
    """Chart rendering contract.

    Args:
        chart_type: Figure type (`bar` or `line`).
        title: Figure title text.
        x_label: X axis label.
        y_label: Y axis label.
        series: One or more chart series.
        chart_format: Visual output format.

    Raises:
        ValueError: If title is empty or series list is empty.
    """

    chart_type: ChartType
    title: str
    x_label: str
    y_label: str
    series: tuple[ChartSeries, ...]
    chart_format: ChartFormat = field(default_factory=ChartFormat)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("ChartSpec.title deve ser texto nao vazio.")
        if not self.series:
            raise ValueError("ChartSpec.series deve conter ao menos uma serie.")
