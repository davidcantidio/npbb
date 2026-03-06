from __future__ import annotations

from dataclasses import dataclass

from .ppt_matching import SlideMatch, match_slide
from .ppt_openxml import ExtractedSlide


SUPPORTED_METRIC_LABELS = {
    "clientes_bb": ["clientes bb"],
    "nao_clientes": ["nao clientes"],
    "faixa_18_25": ["18 25 anos"],
    "faixa_26_40": ["26 40 anos"],
    "fora_18_40": ["fora de 18 40 anos"],
    "leads": ["leads"],
    "base_total": ["base total de leads"],
}


@dataclass(frozen=True)
class SlideProfile:
    slide_index: int
    profile_name: str
    match: SlideMatch


def classify_slides(slides: list[ExtractedSlide], source_events: list[str]) -> list[SlideProfile]:
    profiles: list[SlideProfile] = []
    for slide in slides:
        slide_match = match_slide(slide, source_events)
        profiles.append(
            SlideProfile(
                slide_index=slide.slide_index,
                profile_name=_classify_slide(slide, slide_match),
                match=slide_match,
            )
        )
    return profiles


def _classify_slide(slide: ExtractedSlide, slide_match: SlideMatch) -> str:
    text = slide.normalized_text
    metric_count = _metric_label_count(text)

    if "analise leads 2025" in text and "base total de leads" in text and "clientes bb" in text:
        return "lead_summary_profile"

    if "eventos considerados" in text:
        return "coverage_section_profile"

    if (slide_match.event_names or slide_match.event_families) and metric_count >= 3:
        return "event_breakdown_profile"

    if (slide_match.event_names or slide_match.event_families) and "leads" in text:
        return "event_topline_profile"

    return "unsupported_profile"


def _metric_label_count(text: str) -> int:
    count = 0
    for aliases in SUPPORTED_METRIC_LABELS.values():
        if any(alias in text for alias in aliases):
            count += 1
    return count
