"""Deterministic chart renderer for report figures.

This module renders `bar` and `line` charts from tabular rows using Pillow,
producing deterministic PNG output for identical input.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .chart_spec import ChartSeries, ChartSpec, ChartType


class ChartRenderError(ValueError):
    """Raised when chart rendering fails due to invalid data or contract."""


def _parse_color(color: str) -> tuple[int, int, int]:
    """Convert a color string to RGB tuple.

    Args:
        color: Color in a format accepted by Pillow (`#RRGGBB`, color name).

    Returns:
        RGB tuple.

    Raises:
        ChartRenderError: If color value is invalid.
    """

    try:
        return ImageColor.getrgb(color)
    except ValueError as exc:
        raise ChartRenderError(f"Cor invalida no chart: {color}") from exc


def _as_rows(data: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Validate and normalize chart input rows.

    Args:
        data: Sequence of row mappings.

    Returns:
        Normalized row list.

    Raises:
        ChartRenderError: If input type is invalid.
    """

    if not isinstance(data, Sequence) or isinstance(data, (str, bytes, bytearray)):
        raise ChartRenderError("data invalido: esperado list[dict].")

    rows: list[Mapping[str, Any]] = []
    for idx, row in enumerate(data):
        if not isinstance(row, Mapping):
            raise ChartRenderError(f"data[{idx}] invalido: esperado objeto/Mapping.")
        rows.append(row)

    if not rows:
        raise ChartRenderError("data invalido: lista vazia.")
    return rows


def _collect_categories(rows: Sequence[Mapping[str, Any]], x_field: str) -> list[str]:
    """Collect unique x categories preserving input order.

    Args:
        rows: Data rows.
        x_field: Category field name.

    Returns:
        Ordered category labels.

    Raises:
        ChartRenderError: If category field is missing in all rows.
    """

    categories: list[str] = []
    seen: set[str] = set()
    for row in rows:
        value = row.get(x_field)
        if value is None:
            continue
        label = str(value)
        if label not in seen:
            seen.add(label)
            categories.append(label)
    if not categories:
        raise ChartRenderError(f"Nenhuma categoria encontrada para campo x_field='{x_field}'.")
    return categories


def _build_series_values(
    rows: Sequence[Mapping[str, Any]],
    *,
    categories: Sequence[str],
    series: ChartSeries,
) -> list[float | None]:
    """Map one chart series to numeric y values aligned to categories.

    Args:
        rows: Data rows.
        categories: Ordered category labels.
        series: Series contract.

    Returns:
        Value list aligned with categories. Missing values become `None`.

    Raises:
        ChartRenderError: If y value cannot be parsed as float.
    """

    values_by_category: dict[str, float] = {}
    for row in rows:
        raw_x = row.get(series.x_field)
        if raw_x is None:
            continue
        category = str(raw_x)
        raw_y = row.get(series.y_field)
        if raw_y is None:
            continue
        try:
            values_by_category[category] = float(raw_y)
        except (TypeError, ValueError) as exc:
            raise ChartRenderError(
                f"Valor numerico invalido para serie '{series.name}' no campo '{series.y_field}': {raw_y}"
            ) from exc
    return [values_by_category.get(category) for category in categories]


def _build_palette(spec: ChartSpec) -> list[tuple[int, int, int]]:
    """Resolve deterministic RGB color list for series order.

    Args:
        spec: Chart spec contract.

    Returns:
        RGB color list aligned with spec series order.
    """

    palette = [_parse_color(color) for color in spec.chart_format.palette]
    colors: list[tuple[int, int, int]] = []
    for idx, series in enumerate(spec.series):
        if series.color:
            colors.append(_parse_color(series.color))
        else:
            colors.append(palette[idx % len(palette)])
    return colors


def _value_to_y(
    value: float,
    *,
    min_value: float,
    max_value: float,
    plot_top: int,
    plot_bottom: int,
) -> float:
    """Convert a numeric y value to canvas y coordinate.

    Args:
        value: Series y value.
        min_value: Y domain minimum.
        max_value: Y domain maximum.
        plot_top: Plot top pixel.
        plot_bottom: Plot bottom pixel.

    Returns:
        Canvas y coordinate.
    """

    if max_value == min_value:
        return (plot_top + plot_bottom) / 2
    ratio = (value - min_value) / (max_value - min_value)
    return plot_bottom - ratio * (plot_bottom - plot_top)


def _draw_axes_and_labels(
    draw: ImageDraw.ImageDraw,
    *,
    spec: ChartSpec,
    plot_left: int,
    plot_right: int,
    plot_top: int,
    plot_bottom: int,
    categories: Sequence[str],
    min_value: float,
    max_value: float,
) -> None:
    """Draw fixed axes, grid, ticks and labels.

    Args:
        draw: Pillow drawing context.
        spec: Chart spec contract.
        plot_left: Plot left coordinate.
        plot_right: Plot right coordinate.
        plot_top: Plot top coordinate.
        plot_bottom: Plot bottom coordinate.
        categories: X categories.
        min_value: Y domain minimum.
        max_value: Y domain maximum.
    """

    chart_format = spec.chart_format
    axis_color = _parse_color(chart_format.axis_color)
    grid_color = _parse_color(chart_format.grid_color)
    font = ImageFont.load_default()

    draw.line([(plot_left, plot_top), (plot_left, plot_bottom)], fill=axis_color, width=1)
    draw.line([(plot_left, plot_bottom), (plot_right, plot_bottom)], fill=axis_color, width=1)

    steps = 5
    for step in range(steps + 1):
        fraction = step / steps
        y = plot_bottom - fraction * (plot_bottom - plot_top)
        draw.line([(plot_left, int(y)), (plot_right, int(y))], fill=grid_color, width=1)
        tick_value = min_value + fraction * (max_value - min_value)
        draw.text((plot_left - 70, int(y) - 6), f"{tick_value:.1f}", fill=axis_color, font=font)

    if len(categories) == 1:
        x_positions = [(plot_left + plot_right) / 2]
    else:
        step = (plot_right - plot_left) / (len(categories) - 1)
        x_positions = [plot_left + index * step for index in range(len(categories))]

    for x, label in zip(x_positions, categories):
        draw.text((int(x) - 20, plot_bottom + 8), str(label), fill=axis_color, font=font)

    draw.text((plot_left, 20), spec.title, fill=axis_color, font=font)
    draw.text((plot_left, plot_bottom + 35), spec.x_label, fill=axis_color, font=font)
    draw.text((10, plot_top), spec.y_label, fill=axis_color, font=font)


def _draw_bar_chart(
    draw: ImageDraw.ImageDraw,
    *,
    spec: ChartSpec,
    categories: Sequence[str],
    series_values: Sequence[Sequence[float | None]],
    colors: Sequence[tuple[int, int, int]],
    plot_left: int,
    plot_right: int,
    plot_top: int,
    plot_bottom: int,
    min_value: float,
    max_value: float,
) -> None:
    """Render bar chart traces.

    Args:
        draw: Pillow drawing context.
        spec: Chart spec contract.
        categories: Ordered categories.
        series_values: Series values aligned to categories.
        colors: Series RGB colors.
        plot_left: Plot left coordinate.
        plot_right: Plot right coordinate.
        plot_top: Plot top coordinate.
        plot_bottom: Plot bottom coordinate.
        min_value: Y domain minimum.
        max_value: Y domain maximum.
    """

    category_count = len(categories)
    series_count = len(spec.series)
    slot_width = (plot_right - plot_left) / max(category_count, 1)
    group_width = slot_width * 0.8
    bar_width = group_width / max(series_count, 1)
    zero_y = _value_to_y(
        0.0,
        min_value=min_value,
        max_value=max_value,
        plot_top=plot_top,
        plot_bottom=plot_bottom,
    )

    for category_index in range(category_count):
        group_left = plot_left + category_index * slot_width + (slot_width - group_width) / 2
        for series_index, values in enumerate(series_values):
            value = values[category_index]
            if value is None:
                continue
            x0 = group_left + series_index * bar_width
            x1 = x0 + bar_width - 2
            y_value = _value_to_y(
                value,
                min_value=min_value,
                max_value=max_value,
                plot_top=plot_top,
                plot_bottom=plot_bottom,
            )
            y0 = min(zero_y, y_value)
            y1 = max(zero_y, y_value)
            draw.rectangle([(x0, y0), (x1, y1)], fill=colors[series_index], outline=colors[series_index])


def _draw_line_chart(
    draw: ImageDraw.ImageDraw,
    *,
    spec: ChartSpec,
    categories: Sequence[str],
    series_values: Sequence[Sequence[float | None]],
    colors: Sequence[tuple[int, int, int]],
    plot_left: int,
    plot_right: int,
    plot_top: int,
    plot_bottom: int,
    min_value: float,
    max_value: float,
) -> None:
    """Render line chart traces.

    Args:
        draw: Pillow drawing context.
        spec: Chart spec contract.
        categories: Ordered categories.
        series_values: Series values aligned to categories.
        colors: Series RGB colors.
        plot_left: Plot left coordinate.
        plot_right: Plot right coordinate.
        plot_top: Plot top coordinate.
        plot_bottom: Plot bottom coordinate.
        min_value: Y domain minimum.
        max_value: Y domain maximum.
    """

    if len(categories) == 1:
        x_positions = [(plot_left + plot_right) / 2]
    else:
        step = (plot_right - plot_left) / (len(categories) - 1)
        x_positions = [plot_left + index * step for index in range(len(categories))]

    for series_index, values in enumerate(series_values):
        points: list[tuple[float, float]] = []
        for x, value in zip(x_positions, values):
            if value is None:
                continue
            y = _value_to_y(
                value,
                min_value=min_value,
                max_value=max_value,
                plot_top=plot_top,
                plot_bottom=plot_bottom,
            )
            points.append((x, y))

        if len(points) >= 2:
            draw.line(points, fill=colors[series_index], width=spec.chart_format.line_width)
        for x, y in points:
            radius = spec.chart_format.marker_radius
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill=colors[series_index],
                outline=colors[series_index],
            )


def _to_png_bytes(image: Image.Image) -> bytes:
    """Encode a Pillow image into deterministic PNG bytes.

    Args:
        image: Pillow image to encode.

    Returns:
        PNG bytes.
    """

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def render_chart_png(
    spec: ChartSpec,
    data: Sequence[Mapping[str, Any]],
    output_path: Path | str | None = None,
) -> bytes | Path:
    """Render a deterministic PNG chart from tabular rows.

    Args:
        spec: Typed chart specification.
        data: Tabular row list from marts/views.
        output_path: Optional output path. If provided, PNG is written to disk.

    Returns:
        `bytes` when `output_path` is omitted, or `Path` when file is written.

    Raises:
        ChartRenderError: If chart contract or data payload is invalid.
        OSError: If writing output file fails.
    """

    rows = _as_rows(data)
    categories = _collect_categories(rows, spec.series[0].x_field)
    series_values = [
        _build_series_values(rows, categories=categories, series=series)
        for series in spec.series
    ]

    numeric_values = [value for values in series_values for value in values if value is not None]
    if not numeric_values:
        raise ChartRenderError("Nao ha valores numericos para renderizar o grafico.")

    min_value = min(0.0, min(numeric_values))
    max_value = max(0.0, max(numeric_values))
    if min_value == max_value:
        max_value = min_value + 1.0

    chart_format = spec.chart_format
    image = Image.new(
        "RGB",
        (chart_format.width_px, chart_format.height_px),
        _parse_color(chart_format.background_color),
    )
    draw = ImageDraw.Draw(image)
    colors = _build_palette(spec)

    plot_left = chart_format.margin_left
    plot_right = chart_format.width_px - chart_format.margin_right
    plot_top = chart_format.margin_top
    plot_bottom = chart_format.height_px - chart_format.margin_bottom

    _draw_axes_and_labels(
        draw,
        spec=spec,
        plot_left=plot_left,
        plot_right=plot_right,
        plot_top=plot_top,
        plot_bottom=plot_bottom,
        categories=categories,
        min_value=min_value,
        max_value=max_value,
    )

    if spec.chart_type == ChartType.BAR:
        _draw_bar_chart(
            draw,
            spec=spec,
            categories=categories,
            series_values=series_values,
            colors=colors,
            plot_left=plot_left,
            plot_right=plot_right,
            plot_top=plot_top,
            plot_bottom=plot_bottom,
            min_value=min_value,
            max_value=max_value,
        )
    elif spec.chart_type == ChartType.LINE:
        _draw_line_chart(
            draw,
            spec=spec,
            categories=categories,
            series_values=series_values,
            colors=colors,
            plot_left=plot_left,
            plot_right=plot_right,
            plot_top=plot_top,
            plot_bottom=plot_bottom,
            min_value=min_value,
            max_value=max_value,
        )
    else:
        raise ChartRenderError(f"chart_type nao suportado: {spec.chart_type}")

    png_bytes = _to_png_bytes(image)
    if output_path is None:
        return png_bytes

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(png_bytes)
    return destination
