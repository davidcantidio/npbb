"""Template registry and category resolution for public landing pages."""

from __future__ import annotations

import unicodedata

from sqlmodel import Session

from app.models.models import Evento, SubtipoEvento, TipoEvento
from app.schemas.landing_public import LandingExperimentVariantRead, LandingTemplateConfigRead

TEMPLATE_REGISTRY: dict[str, dict[str, str]] = {
    "generico": {
        "categoria": "generico",
        "tema": "Default",
        "mood": "Neutro, confiavel e com identidade BB.",
        "cta_text": "Quero me cadastrar",
        "color_primary": "#3333BD",
        "color_secondary": "#FCFC30",
        "color_background": "#F7F8FF",
        "color_text": "#111827",
        "hero_layout": "split",
        "cta_variant": "filled",
        "graphics_style": "geometric",
        "tone_of_voice": "warmth",
        "success_message": "Cadastro realizado com sucesso. Obrigado por participar com o BB.",
    },
    "corporativo": {
        "categoria": "corporativo",
        "tema": "Corp",
        "mood": "Profissional, confiavel e estrategico.",
        "cta_text": "Confirmar presenca",
        "color_primary": "#1E3A8A",
        "color_secondary": "#FCFC30",
        "color_background": "#F5F7FB",
        "color_text": "#111827",
        "hero_layout": "split",
        "cta_variant": "outlined",
        "graphics_style": "grid",
        "tone_of_voice": "attention",
        "success_message": "Inscricao confirmada. Nos vemos no encontro do Banco do Brasil.",
    },
    "esporte_convencional": {
        "categoria": "esporte_convencional",
        "tema": "Sport",
        "mood": "Orgulho, conquista e energia alta.",
        "cta_text": "Garanta sua vaga",
        "color_primary": "#3333BD",
        "color_secondary": "#FCFC30",
        "color_background": "#F3F7FF",
        "color_text": "#111827",
        "hero_layout": "split",
        "cta_variant": "filled",
        "graphics_style": "geometric",
        "tone_of_voice": "enthusiasm",
        "success_message": "Voce esta dentro. O BB vai torcer com voce.",
    },
    "esporte_radical": {
        "categoria": "esporte_radical",
        "tema": "Radical",
        "mood": "Alta energia, autenticidade e movimento.",
        "cta_text": "Quero fazer parte",
        "color_primary": "#FF6E91",
        "color_secondary": "#FCFC30",
        "color_background": "#FFF7FB",
        "color_text": "#1F2937",
        "hero_layout": "full-bleed",
        "cta_variant": "gradient",
        "graphics_style": "dynamic",
        "tone_of_voice": "enthusiasm",
        "success_message": "Voce esta dentro. A gente se ve na pista.",
    },
    "show_musical": {
        "categoria": "show_musical",
        "tema": "Show",
        "mood": "Vibrante, noturno e memoravel.",
        "cta_text": "Quero ir",
        "color_primary": "#735CC6",
        "color_secondary": "#FF6E91",
        "color_background": "#140F2E",
        "color_text": "#F8FAFC",
        "hero_layout": "dark-overlay",
        "cta_variant": "gradient",
        "graphics_style": "dynamic",
        "tone_of_voice": "enthusiasm",
        "success_message": "Cadastro confirmado. Prepare-se para uma experiencia inesquecivel.",
    },
    "evento_cultural": {
        "categoria": "evento_cultural",
        "tema": "Cultural",
        "mood": "Sofisticado, acessivel e inspirador.",
        "cta_text": "Quero conhecer",
        "color_primary": "#00EBD0",
        "color_secondary": "#BDB6FF",
        "color_background": "#F7FBFB",
        "color_text": "#111827",
        "hero_layout": "editorial",
        "cta_variant": "outlined",
        "graphics_style": "organic",
        "tone_of_voice": "attention",
        "success_message": "Inscricao realizada. Obrigado por valorizar a cultura com o BB.",
    },
    "tecnologia": {
        "categoria": "tecnologia",
        "tema": "Tech",
        "mood": "Futuro, comunidade e inovacao.",
        "cta_text": "Quero participar",
        "color_primary": "#54DCFC",
        "color_secondary": "#83FFEA",
        "color_background": "#07111F",
        "color_text": "#F8FAFC",
        "hero_layout": "dark-overlay",
        "cta_variant": "gradient",
        "graphics_style": "grid",
        "tone_of_voice": "enthusiasm",
        "success_message": "Cadastro feito. O proximo passo em inovacao comeca aqui.",
    },
}

CATEGORY_ALIASES = {
    "default": "generico",
    "padrao": "generico",
    "genérico": "generico",
    "genérico bb": "generico",
    "generic": "generico",
    "corp": "corporativo",
    "institucional": "corporativo",
    "corporativo": "corporativo",
}

CTA_VARIANT_REGISTRY: dict[str, list[dict[str, str]]] = {
    "generico": [
        {"id": "generic_a", "label": "Padrao A", "text": "Quero participar"},
        {"id": "generic_b", "label": "Padrao B", "text": "Faca sua inscricao"},
    ],
    "corporativo": [
        {"id": "corp_a", "label": "Corporativo A", "text": "Confirmar presenca"},
        {"id": "corp_b", "label": "Corporativo B", "text": "Fazer inscricao"},
    ],
    "esporte_convencional": [
        {"id": "sport_a", "label": "Esporte A", "text": "Cadastre-se na acao"},
        {"id": "sport_b", "label": "Esporte B", "text": "Quero receber novidades"},
    ],
    "esporte_radical": [
        {"id": "radical_a", "label": "Radical A", "text": "Quero fazer parte"},
        {"id": "radical_b", "label": "Radical B", "text": "Inscreva-se agora"},
    ],
    "show_musical": [
        {"id": "show_a", "label": "Show A", "text": "Cadastre-se na experiencia"},
        {"id": "show_b", "label": "Show B", "text": "Quero receber novidades"},
    ],
    "evento_cultural": [
        {"id": "cultural_a", "label": "Cultural A", "text": "Cadastre-se para saber mais"},
        {"id": "cultural_b", "label": "Cultural B", "text": "Quero receber novidades"},
    ],
    "tecnologia": [
        {"id": "tech_a", "label": "Tech A", "text": "Cadastre-se para acompanhar"},
        {"id": "tech_b", "label": "Tech B", "text": "Quero receber novidades"},
    ],
}

SUBTIPO_KEYWORDS = {
    "skate": "esporte_radical",
    "surfe": "esporte_radical",
    "surf": "esporte_radical",
    "bmx": "esporte_radical",
    "futebol": "esporte_convencional",
    "atletismo": "esporte_convencional",
    "natacao": "esporte_convencional",
    "volei": "esporte_convencional",
    "show": "show_musical",
    "festival": "show_musical",
    "concerto": "show_musical",
    "musica": "show_musical",
    "exposicao": "evento_cultural",
    "teatro": "evento_cultural",
    "cinema": "evento_cultural",
    "ccbb": "evento_cultural",
    "congresso": "corporativo",
    "summit": "corporativo",
    "treinamento": "corporativo",
    "reuniao": "corporativo",
    "hackathon": "tecnologia",
    "startup": "tecnologia",
    "tech": "tecnologia",
    "inovacao": "tecnologia",
}

TIPO_KEYWORDS = {
    "esporte": "esporte_convencional",
    "cultura": "evento_cultural",
    "corporativo": "corporativo",
    "institucional": "corporativo",
    "tecnologia": "tecnologia",
    "inovacao": "tecnologia",
    "show": "show_musical",
}


def _normalize_token(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_only.strip().lower().split())


def _resolve_category_alias(value: str | None) -> str | None:
    token = _normalize_token(value)
    if not token:
        return None
    if token in TEMPLATE_REGISTRY:
        return token
    if token in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[token]
    return None


def normalize_template_override_input(value: str | None) -> str | None:
    token = _normalize_token(value)
    if not token:
        return None
    return _resolve_category_alias(token)


def get_allowed_template_overrides() -> list[str]:
    return sorted(TEMPLATE_REGISTRY.keys())


def _match_keywords(value: str | None, mapping: dict[str, str]) -> str | None:
    token = _normalize_token(value)
    if not token:
        return None
    for keyword, category in mapping.items():
        if keyword in token:
            return category
    return None


def _build_cta_variants(*, category: str, has_custom_cta: bool) -> tuple[bool, list[LandingExperimentVariantRead]]:
    if has_custom_cta:
        return False, []
    items = CTA_VARIANT_REGISTRY.get(category, [])
    return (
        len(items) > 1,
        [LandingExperimentVariantRead(id=item["id"], label=item["label"], text=item["text"]) for item in items],
    )


def _get_tipo_nome(session: Session, evento: Evento) -> str | None:
    if evento.tipo_id is None:
        return None
    tipo = session.get(TipoEvento, evento.tipo_id)
    return tipo.nome if tipo else None


def _get_subtipo_nome(session: Session, evento: Evento) -> str | None:
    if evento.subtipo_id is None:
        return None
    subtipo = session.get(SubtipoEvento, evento.subtipo_id)
    return subtipo.nome if subtipo else None


def resolve_template_category(
    session: Session,
    *,
    evento: Evento,
    template_name: str | None = None,
    template_override: str | None = None,
) -> str:
    transient = _resolve_category_alias(template_override)
    if transient:
        return transient

    explicit = _resolve_category_alias(evento.template_override)
    if explicit:
        return explicit

    explicit_template = _resolve_category_alias(template_name)
    if explicit_template:
        return explicit_template

    subtipo_match = _match_keywords(_get_subtipo_nome(session, evento), SUBTIPO_KEYWORDS)
    if subtipo_match:
        return subtipo_match

    tipo_match = _match_keywords(_get_tipo_nome(session, evento), TIPO_KEYWORDS)
    if tipo_match:
        return tipo_match

    keyword_match = _match_keywords(evento.nome, {**SUBTIPO_KEYWORDS, **TIPO_KEYWORDS})
    if keyword_match:
        return keyword_match

    return "generico"


def get_template_config(
    session: Session,
    *,
    evento: Evento,
    template_name: str | None = None,
    template_override: str | None = None,
) -> LandingTemplateConfigRead:
    category = resolve_template_category(
        session,
        evento=evento,
        template_name=template_name,
        template_override=template_override,
    )
    raw = dict(TEMPLATE_REGISTRY.get(category, TEMPLATE_REGISTRY["generico"]))
    custom_cta = (evento.cta_personalizado or "").strip()
    raw["cta_text"] = custom_cta or raw["cta_text"]
    cta_experiment_enabled, cta_variants = _build_cta_variants(
        category=category,
        has_custom_cta=bool(custom_cta),
    )
    raw["cta_experiment_enabled"] = cta_experiment_enabled
    raw["cta_variants"] = cta_variants
    raw.pop("success_message", None)
    return LandingTemplateConfigRead(**raw)
