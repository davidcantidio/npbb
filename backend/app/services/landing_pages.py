"""Servico de resolucao e montagem das landing pages publicas."""

from __future__ import annotations

import base64
import unicodedata
from html import escape

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import (
    Ativacao,
    AtivacaoLead,
    Evento,
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    Lead,
    SubtipoEvento,
    TipoEvento,
    now_utc,
)
from app.schemas.landing_public import (
    LandingAccessRead,
    LandingBrandRead,
    LandingEventRead,
    LandingFieldRead,
    LandingFormRead,
    LandingPageRead,
    LandingSubmitRequest,
    LandingSubmitResponse,
    LandingTemplateConfigRead,
)
from app.services.formulario_lead_catalog import (
    FORMULARIO_CAMPOS_DEFAULT,
    FORMULARIO_CAMPOS_ORDEM_BY_LOWER,
    get_form_field_definition,
)
from app.services.qr_code import build_qr_code_data_url
from app.utils.urls import build_ativacao_public_urls, build_evento_public_urls

PRIVACY_POLICY_URL = "https://www.bb.com.br/site/privacidade-e-lgpd/"
BRAND_TAGLINE = "Banco do Brasil. Pra tudo que voce imaginar."

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


def _match_keywords(value: str | None, mapping: dict[str, str]) -> str | None:
    token = _normalize_token(value)
    if not token:
        return None
    for keyword, category in mapping.items():
        if keyword in token:
            return category
    return None


def _build_hero_placeholder_data_url(*, title: str, subtitle: str, primary: str, secondary: str) -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">'
        f'<rect width="1600" height="900" fill="{primary}"/>'
        f'<circle cx="1320" cy="160" r="220" fill="{secondary}" opacity="0.9"/>'
        f'<circle cx="220" cy="760" r="260" fill="{secondary}" opacity="0.2"/>'
        '<rect x="96" y="96" width="420" height="96" rx="24" fill="#FFFFFF" opacity="0.14"/>'
        f'<text x="120" y="168" fill="#FFFFFF" font-size="44" font-family="Arial, sans-serif" font-weight="700">{escape(title)}</text>'
        f'<text x="120" y="248" fill="#FFFFFF" font-size="72" font-family="Arial, sans-serif" font-weight="800">{escape(subtitle)}</text>'
        '<text x="120" y="332" fill="#FFFFFF" font-size="28" font-family="Arial, sans-serif">Landing dinamica Banco do Brasil</text>'
        "</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


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


def get_event_form_config(
    session: Session, *, evento_id: int
) -> tuple[FormularioLeadConfig | None, list[FormularioLeadCampo], str | None]:
    config = session.exec(
        select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)
    ).first()
    if not config:
        return None, [], None

    campos = session.exec(
        select(FormularioLeadCampo)
        .where(FormularioLeadCampo.config_id == config.id)
        .order_by(FormularioLeadCampo.ordem, FormularioLeadCampo.id)
    ).all()
    template_name = None
    if config.template_id is not None:
        template = session.get(FormularioLandingTemplate, config.template_id)
        template_name = template.nome if template else None
    return config, campos, template_name


def resolve_template_category(
    session: Session, *, evento: Evento, template_name: str | None = None
) -> str:
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
    session: Session, *, evento: Evento, template_name: str | None = None
) -> LandingTemplateConfigRead:
    category = resolve_template_category(session, evento=evento, template_name=template_name)
    raw = dict(TEMPLATE_REGISTRY.get(category, TEMPLATE_REGISTRY["generico"]))
    raw["cta_text"] = (evento.cta_personalizado or "").strip() or raw["cta_text"]
    raw.pop("success_message", None)
    return LandingTemplateConfigRead(**raw)


def hydrate_ativacao_public_urls(
    ativacao: Ativacao, *, backend_base_url: str | None = None
) -> bool:
    urls = build_ativacao_public_urls(ativacao.id or 0, backend_base_url=backend_base_url)
    landing_url = urls["landing_url"]
    qr_code_url = build_qr_code_data_url(landing_url)

    changed = False
    if ativacao.landing_url != landing_url:
        ativacao.landing_url = landing_url
        changed = True
    if ativacao.url_promotor != urls["url_promotor"]:
        ativacao.url_promotor = urls["url_promotor"]
        changed = True
    if ativacao.qr_code_url != qr_code_url:
        ativacao.qr_code_url = qr_code_url
        changed = True
    return changed


def get_landing_fields(
    session: Session, *, evento: Evento
) -> tuple[list[LandingFieldRead], str | None]:
    _, campos_db, template_name = get_event_form_config(session, evento_id=evento.id or 0)
    if campos_db:
        fields = []
        for campo in campos_db:
            definition = get_form_field_definition(campo.nome_campo)
            fields.append(
                LandingFieldRead(
                    key=definition["key"],
                    label=definition["label"],
                    input_type=definition["input_type"],
                    required=bool(campo.obrigatorio),
                    autocomplete=definition.get("autocomplete"),
                    placeholder=definition.get("placeholder"),
                )
            )
        return fields, template_name

    default_fields = []
    for nome_campo, obrigatorio in FORMULARIO_CAMPOS_DEFAULT:
        definition = get_form_field_definition(nome_campo)
        default_fields.append(
            LandingFieldRead(
                key=definition["key"],
                label=definition["label"],
                input_type=definition["input_type"],
                required=obrigatorio,
                autocomplete=definition.get("autocomplete"),
                placeholder=definition.get("placeholder"),
            )
        )
    default_fields.sort(key=lambda item: FORMULARIO_CAMPOS_ORDEM_BY_LOWER.get(item.label.lower(), 999))
    return default_fields, None


def build_landing_payload(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None = None,
    backend_base_url: str | None = None,
) -> LandingPageRead:
    fields, template_name = get_landing_fields(session, evento=evento)
    template = get_template_config(session, evento=evento, template_name=template_name)
    template_data = TEMPLATE_REGISTRY[template.categoria]
    hero_url = (evento.hero_image_url or "").strip() or _build_hero_placeholder_data_url(
        title=evento.nome,
        subtitle=template.tema,
        primary=template.color_primary,
        secondary=template.color_secondary,
    )

    required_keys = [field.key for field in fields if field.required]
    optional_keys = [field.key for field in fields if not field.required]
    submit_url = (
        f"/landing/ativacoes/{ativacao.id}/submit"
        if ativacao and ativacao.id is not None
        else f"/landing/eventos/{evento.id}/submit"
    )

    if ativacao and hydrate_ativacao_public_urls(ativacao, backend_base_url=backend_base_url):
        ativacao.updated_at = now_utc()
        session.add(ativacao)
        session.commit()
        session.refresh(ativacao)

    event_urls = build_evento_public_urls(evento.id or 0, backend_base_url=backend_base_url)
    return LandingPageRead(
        ativacao_id=ativacao.id if ativacao else None,
        evento=LandingEventRead(
            id=evento.id or 0,
            nome=evento.nome,
            descricao=evento.descricao,
            descricao_curta=(evento.descricao_curta or "").strip() or evento.descricao,
            data_inicio=evento.data_inicio_realizada or evento.data_inicio_prevista,
            data_fim=evento.data_fim_realizada or evento.data_fim_prevista,
            cidade=evento.cidade,
            estado=evento.estado,
        ),
        template=template,
        formulario=LandingFormRead(
            event_id=evento.id or 0,
            ativacao_id=ativacao.id if ativacao else None,
            submit_url=submit_url,
            campos=fields,
            campos_obrigatorios=required_keys,
            campos_opcionais=optional_keys,
            mensagem_sucesso=template_data["success_message"],
            lgpd_texto=(
                "Ao enviar seus dados, voce concorda com o tratamento das informacoes para contato "
                "e relacionamento com o Banco do Brasil."
            ),
            privacy_policy_url=PRIVACY_POLICY_URL,
        ),
        marca=LandingBrandRead(
            tagline=BRAND_TAGLINE,
            versao_logo="negativo" if template.color_primary in {"#07111F", "#140F2E"} else "positivo",
            url_hero_image=hero_url,
            hero_alt=f"Imagem de destaque do evento {evento.nome}",
        ),
        acesso=LandingAccessRead(
            landing_url=ativacao.landing_url if ativacao else event_urls["url_landing"],
            qr_code_url=ativacao.qr_code_url if ativacao else None,
            url_promotor=ativacao.url_promotor if ativacao else event_urls["url_landing"],
        ),
    )


def submit_landing_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
    success_message: str,
) -> LandingSubmitResponse:
    email = str(payload.email).strip().lower() if payload.email else None
    existing_lead = None

    if ativacao and ativacao.id is not None and email:
        existing_lead = session.exec(
            select(Lead)
            .join(AtivacaoLead, AtivacaoLead.lead_id == Lead.id)
            .where(AtivacaoLead.ativacao_id == ativacao.id)
            .where(func.lower(Lead.email) == email)
        ).first()
    elif email:
        existing_lead = session.exec(
            select(Lead)
            .where(func.lower(Lead.email) == email)
            .where(Lead.evento_nome == evento.nome)
        ).first()

    if not existing_lead:
        existing_lead = Lead(
            nome=payload.nome,
            sobrenome=payload.sobrenome,
            email=email,
            telefone=payload.telefone,
            cpf=payload.cpf,
            data_nascimento=payload.data_nascimento,
            evento_nome=evento.nome,
            cidade=evento.cidade,
            estado=(payload.estado or evento.estado or "").strip() or None,
            endereco_rua=payload.endereco,
            genero=payload.genero,
            metodo_entrega=payload.area_de_atuacao,
            fonte_origem="landing_publica",
            opt_in="aceito",
            opt_in_flag=True,
        )
        session.add(existing_lead)
        session.flush()

    if ativacao and ativacao.id is not None and existing_lead.id is not None:
        existing_link = session.exec(
            select(AtivacaoLead)
            .where(AtivacaoLead.ativacao_id == ativacao.id)
            .where(AtivacaoLead.lead_id == existing_lead.id)
        ).first()
        if not existing_link:
            session.add(AtivacaoLead(ativacao_id=ativacao.id, lead_id=existing_lead.id))

    session.commit()
    session.refresh(existing_lead)
    return LandingSubmitResponse(
        lead_id=existing_lead.id or 0,
        event_id=evento.id or 0,
        ativacao_id=ativacao.id if ativacao else None,
        mensagem_sucesso=success_message,
    )
