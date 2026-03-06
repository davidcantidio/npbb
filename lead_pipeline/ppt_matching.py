from __future__ import annotations

from dataclasses import dataclass

from .ppt_openxml import ExtractedSlide


FAMILY_NUMERIC_SCOPE = {
    "rio_innovation": "direct_event",
    "recnplay": "direct_event",
    "ccxp": "direct_event",
    "corrida_rua": "family",
    "festival_tamo_junto": "family",
    "park_challenge": "family",
    "gilberto_gil": "lead_only",
    "afropunk": "lead_only",
    "sls_street": "coverage_only",
    "vert_battle": "coverage_only",
}

FAMILY_ALIASES = {
    "rio_innovation": ["rio innovation week", "rio innovation"],
    "recnplay": ["rec n play", "rec'n play", "recn play", "rec nplay"],
    "ccxp": ["ccxp"],
    "corrida_rua": [
        "circuito banco do brasil de corridas",
        "circuito bb de corrida",
        "circuito bb corrida de rua",
        "corrida de rua",
    ],
    "festival_tamo_junto": ["festival tamo junto", "tamo junto bb", "tamo junto"],
    "park_challenge": ["park challenge 2025", "park challenge", "skate park challenge"],
    "gilberto_gil": ["turne gilberto gil", "gilberto gil"],
    "afropunk": ["afropunk"],
    "sls_street": [
        "sls select series",
        "sls super crown 2025",
        "sls super crown",
        "street league",
        "sls",
    ],
    "vert_battle": ["vert battle", "skate vertical"],
}


@dataclass(frozen=True)
class SlideMatch:
    event_names: set[str]
    event_families: set[str]


def map_event_family(event_name: str) -> str | None:
    if event_name.startswith("GILBERTO GIL | TEMPO REI"):
        return "gilberto_gil"
    if event_name.startswith("SLS "):
        return "sls_street"
    if event_name in {"Circuito Banco do Brasil de Corridas", "Circuito BB de Corrida – JP"}:
        return "corrida_rua"
    if event_name in {"FESTIVAL TAMO JUNTO 2025", "TAMO JUNTO BB"}:
        return "festival_tamo_junto"
    if event_name == "Park Challenge 2025":
        return "park_challenge"
    if event_name == "VERT BATTLE :: CURITIBA":
        return "vert_battle"
    if event_name == "Rio Innovation Week":
        return "rio_innovation"
    if event_name == "Rec’n’Play":
        return "recnplay"
    if event_name == "CCXP – 2025":
        return "ccxp"
    if event_name == "Afropunk":
        return "afropunk"
    return None


def event_direct_aliases(event_name: str) -> list[str]:
    family = map_event_family(event_name)
    aliases = [event_name]

    if family == "rio_innovation":
        aliases.append("rio innovation")
    elif family == "recnplay":
        aliases.extend(["rec'n'play", "rec'n play", "rec n play", "rec´n play"])
    elif family == "ccxp":
        aliases.append("ccxp")

    normalized: list[str] = []
    seen: set[str] = set()
    for alias in aliases:
        normalized_alias = normalize_match_text(alias)
        if normalized_alias and normalized_alias not in seen:
            normalized.append(normalized_alias)
            seen.add(normalized_alias)
    return normalized


def normalize_match_text(value: str) -> str:
    from .ppt_openxml import normalize_ppt_text

    text = normalize_ppt_text(value)
    text = text.replace(" rec n play ", " recnplay ")
    text = text.replace(" rec nplay ", " recnplay ")
    return text


def match_slide(slide: ExtractedSlide, source_events: list[str]) -> SlideMatch:
    event_names: set[str] = set()
    event_families: set[str] = set()
    normalized_slide = slide.normalized_text

    for event_name in source_events:
        family = map_event_family(event_name)
        if family is None:
            continue

        direct_aliases = event_direct_aliases(event_name)
        if any(alias and alias in normalized_slide for alias in direct_aliases):
            event_names.add(event_name)
            event_families.add(family)
            continue

        family_alias_hits = [alias for alias in FAMILY_ALIASES[family] if normalize_match_text(alias) in normalized_slide]
        if family_alias_hits:
            event_families.add(family)

    return SlideMatch(event_names=event_names, event_families=event_families)


def eligible_coverage_basis(profile_name: str) -> str | None:
    if profile_name == "lead_summary_profile":
        return "lead_summary_profile"
    if profile_name == "coverage_section_profile":
        return "coverage_section_profile"
    if profile_name == "event_breakdown_profile":
        return "event_breakdown_profile"
    if profile_name == "event_topline_profile":
        return "event_topline_profile"
    return None
