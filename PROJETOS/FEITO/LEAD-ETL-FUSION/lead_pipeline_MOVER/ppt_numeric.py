from __future__ import annotations

from dataclasses import dataclass
import math
import re

from .ppt_openxml import ExtractedSlide, TextShape


FIELD_LABELS = {
    "total_leads": ["base total de leads", "leads"],
    "clientes_bb": ["clientes bb"],
    "nao_clientes": ["nao clientes"],
    "faixa_18_25": ["18 25 anos"],
    "faixa_26_40": ["26 40 anos"],
    "fora_18_40": ["fora de 18 40 anos"],
}

SUPPORTED_BREAKDOWN_FIELDS = [
    "clientes_bb",
    "nao_clientes",
    "faixa_18_25",
    "faixa_26_40",
    "fora_18_40",
    "total_leads",
]

NUMBER_RE = re.compile(
    r"(?P<prefix>\+)?\s*(?:R\$\s*)?(?P<number>\d{1,3}(?:[.\s]\d{3})+|\d+(?:,\d+)?)\s*(?P<unit>mil|MM|mm|bi)?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ObservedMetric:
    field: str
    display_text: str
    lower_bound: int
    upper_bound: int
    shape_name: str


def extract_lead_summary_metrics(slide: ExtractedSlide) -> dict[str, ObservedMetric]:
    results: dict[str, ObservedMetric] = {}
    for field in ("total_leads", "clientes_bb"):
        label_shape = _best_label_shape(slide, field)
        if label_shape is None:
            continue
        observed = _extract_metric_for_label(slide, field, label_shape, used_shapes=set())
        if observed is not None:
            results[field] = observed
    return results


def extract_breakdown_metrics(slide: ExtractedSlide) -> dict[str, ObservedMetric]:
    results: dict[str, ObservedMetric] = {}
    used_shapes: set[str] = set()
    for field in SUPPORTED_BREAKDOWN_FIELDS:
        label_shape = _best_label_shape(slide, field)
        if label_shape is None:
            continue
        observed = _extract_metric_for_label(slide, field, label_shape, used_shapes)
        if observed is None:
            continue
        results[field] = observed
        used_shapes.add(_shape_key(label_shape))
        used_shapes.add(observed.shape_name)
    return results


def extract_topline_leads(
    slide: ExtractedSlide,
    subject_aliases: dict[str, list[str]],
) -> dict[str, ObservedMetric]:
    title_shapes: list[tuple[str, TextShape]] = []
    for subject_id, aliases in subject_aliases.items():
        title_shape = _best_subject_title_shape(slide, aliases)
        if title_shape is not None:
            title_shapes.append((subject_id, title_shape))

    if not title_shapes:
        return {}

    title_shapes.sort(key=lambda item: item[1].center_x)
    blocks = _title_blocks(title_shapes)

    results: dict[str, ObservedMetric] = {}
    used_shapes: set[str] = set()
    for subject_id, title_shape, left_bound, right_bound in blocks:
        label_shape = _best_label_shape(
            slide,
            "total_leads",
            block=(left_bound, right_bound),
            prefer_near_x=title_shape.center_x,
        )
        if label_shape is None:
            continue
        observed = _extract_metric_for_label(
            slide,
            "total_leads",
            label_shape,
            used_shapes,
            block=(left_bound, right_bound),
        )
        if observed is None:
            continue
        results[subject_id] = observed
        used_shapes.add(_shape_key(label_shape))
        used_shapes.add(observed.shape_name)

    return results


def parse_number_bounds(value: str) -> tuple[str, int, int] | None:
    match = NUMBER_RE.search(str(value or ""))
    if match is None:
        return None

    number_text = match.group("number")
    prefix = match.group("prefix") or ""
    unit = (match.group("unit") or "").lower()
    display = f"{prefix}{number_text}{(' ' + unit) if unit else ''}".strip()

    clean_number = number_text.replace(" ", "")
    if "." in clean_number and "," not in clean_number:
        exact = int(clean_number.replace(".", ""))
        if prefix == "+" and exact >= 1_000:
            lower, upper = exact, exact + 999
        else:
            lower, upper = exact, exact
    elif "," in clean_number:
        whole, decimal = clean_number.split(",", 1)
        base = float(f"{whole}.{decimal}")
        if unit == "mil":
            scale = 1_000
        elif unit == "mm":
            scale = 1_000_000
        elif unit == "bi":
            scale = 1_000_000_000
        else:
            return None
        lower = int(base * scale)
        step = scale // (10 ** len(decimal))
        upper = lower + step - 1
    else:
        exact = int(clean_number)
        if unit == "mil":
            lower = exact * 1_000
            upper = lower + 999
        elif unit == "mm":
            lower = exact * 1_000_000
            upper = lower + 999_999
        elif unit == "bi":
            lower = exact * 1_000_000_000
            upper = lower + 999_999_999
        elif prefix == "+" and exact >= 1_000:
            lower = exact
            upper = exact + 999
        else:
            lower, upper = exact, exact

    return display, lower, upper


def compare_metric(observed: ObservedMetric, expected_value: int) -> bool:
    return observed.lower_bound <= expected_value <= observed.upper_bound


def _best_label_shape(
    slide: ExtractedSlide,
    field: str,
    *,
    block: tuple[float, float] | None = None,
    prefer_near_x: float | None = None,
) -> TextShape | None:
    aliases = FIELD_LABELS[field]
    candidates: list[tuple[int, TextShape]] = []
    for shape in slide.shapes:
        if block is not None and not _shape_in_block(shape, block):
            continue
        for alias_index, alias in enumerate(aliases):
            if alias in shape.normalized_text:
                candidates.append((alias_index, shape))
                break

    if not candidates:
        return None

    if prefer_near_x is not None:
        candidates.sort(
            key=lambda item: (
                item[0],
                abs(item[1].center_x - prefer_near_x),
                len(item[1].text),
                item[1].y,
            )
        )
    else:
        candidates.sort(key=lambda item: (item[0], len(item[1].text), item[1].y, item[1].x))
    return candidates[0][1]


def _extract_metric_for_label(
    slide: ExtractedSlide,
    field: str,
    label_shape: TextShape,
    used_shapes: set[str],
    *,
    block: tuple[float, float] | None = None,
) -> ObservedMetric | None:
    inline = parse_number_bounds(label_shape.text)
    if inline is not None and _supports_inline_value(field, label_shape):
        return ObservedMetric(
            field=field,
            display_text=inline[0],
            lower_bound=inline[1],
            upper_bound=inline[2],
            shape_name=_shape_key(label_shape),
        )

    best_candidate: tuple[float, TextShape, tuple[str, int, int]] | None = None
    for shape in slide.shapes:
        shape_key = _shape_key(shape)
        if shape_key in used_shapes or shape_key == _shape_key(label_shape):
            continue
        if block is not None and not _shape_in_block(shape, block):
            continue

        parsed = parse_number_bounds(shape.text)
        if parsed is None or not _is_numeric_shape(shape):
            continue

        x_distance = abs(shape.center_x - label_shape.center_x)
        y_distance = abs(shape.center_y - label_shape.center_y)
        if x_distance > 3_000_000 or y_distance > 1_800_000:
            continue

        score = x_distance + (1.5 * y_distance)
        if best_candidate is None or score < best_candidate[0]:
            best_candidate = (score, shape, parsed)

    if best_candidate is None:
        return None

    _, shape, parsed = best_candidate
    return ObservedMetric(
        field=field,
        display_text=parsed[0],
        lower_bound=parsed[1],
        upper_bound=parsed[2],
        shape_name=_shape_key(shape),
    )


def _best_subject_title_shape(slide: ExtractedSlide, aliases: list[str]) -> TextShape | None:
    candidates = [
        shape
        for shape in slide.shapes
        if any(alias in shape.normalized_text for alias in aliases)
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda shape: (shape.y, shape.x, len(shape.text)))
    return candidates[0]


def _title_blocks(
    title_shapes: list[tuple[str, TextShape]]
) -> list[tuple[str, TextShape, float, float]]:
    if len(title_shapes) == 1:
        subject_id, shape = title_shapes[0]
        return [(subject_id, shape, -math.inf, math.inf)]

    blocks: list[tuple[str, TextShape, float, float]] = []
    for index, (subject_id, shape) in enumerate(title_shapes):
        if index == 0:
            left_bound = -math.inf
        else:
            left_bound = (title_shapes[index - 1][1].center_x + shape.center_x) / 2
        if index == len(title_shapes) - 1:
            right_bound = math.inf
        else:
            right_bound = (shape.center_x + title_shapes[index + 1][1].center_x) / 2
        blocks.append((subject_id, shape, left_bound, right_bound))
    return blocks


def _shape_in_block(shape: TextShape, block: tuple[float, float]) -> bool:
    left_bound, right_bound = block
    return left_bound <= shape.center_x <= right_bound


def _is_numeric_shape(shape: TextShape) -> bool:
    parsed = parse_number_bounds(shape.text)
    if parsed is None:
        return False

    normalized = shape.normalized_text
    allowed_tokens = {"r", "s", "mil", "mm", "bi", "+", "$"}
    extra_tokens = [token for token in normalized.split() if token.isalpha() and token not in allowed_tokens]
    return not extra_tokens


def _shape_key(shape: TextShape) -> str:
    return f"{shape.shape_name}|{shape.x}|{shape.y}|{shape.width}|{shape.height}|{shape.text}"


def _supports_inline_value(field: str, label_shape: TextShape) -> bool:
    if field not in {"total_leads", "clientes_bb", "nao_clientes"}:
        return False
    text = label_shape.text.lower()
    return any(token in text for token in [".", ",", "+", "mil", "mm", "bi"])
