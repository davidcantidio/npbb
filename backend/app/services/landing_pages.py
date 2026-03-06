"""Servico de resolucao e montagem das landing pages publicas."""

from __future__ import annotations

import unicodedata

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.models import (
    Ativacao,
    AtivacaoLead,
    Evento,
    EventoLandingCustomizationAudit,
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    Gamificacao,
    LandingAnalyticsEvent,
    Lead,
    SubtipoEvento,
    TipoEvento,
    now_utc,
)
from app.schemas.landing_public import (
    GamificacaoPublicSchema,
    LandingAccessRead,
    LandingAnalyticsSummaryRead,
    LandingAnalyticsTrackRequest,
    LandingAnalyticsVariantSummaryRead,
    LandingAtivacaoRead,
    LandingBrandRead,
    LandingExperimentVariantRead,
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

ANALYTICS_EVENT_PAGE_VIEW = "page_view"
ANALYTICS_EVENT_FORM_START = "form_start"
ANALYTICS_EVENT_SUBMIT_ATTEMPT = "submit_attempt"
ANALYTICS_EVENT_SUBMIT_SUCCESS = "submit_success"
ANALYTICS_EVENT_CTA_EXPOSURE = "cta_exposure"

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


def _build_submit_url(*, evento_id: int, ativacao: Ativacao | None) -> str:
    if ativacao and ativacao.id is not None:
        return f"/landing/ativacoes/{ativacao.id}/submit"
    return f"/landing/eventos/{evento_id}/submit"


def _persist_ativacao_public_urls_if_changed(
    session: Session,
    *,
    ativacao: Ativacao | None,
    backend_base_url: str | None,
) -> None:
    if ativacao is None:
        return
    if not hydrate_ativacao_public_urls(ativacao, backend_base_url=backend_base_url):
        return
    ativacao.updated_at = now_utc()
    session.add(ativacao)
    session.commit()
    session.refresh(ativacao)


def _build_ativacao_info(ativacao: Ativacao | None) -> LandingAtivacaoRead | None:
    if ativacao is None:
        return None
    return LandingAtivacaoRead(
        id=ativacao.id or 0,
        nome=ativacao.nome,
        descricao=(ativacao.descricao or "").strip() or None,
        mensagem_qrcode=(ativacao.mensagem_qrcode or "").strip() or None,
    )


def _build_gamificacoes_for_ativacao(
    session: Session, *, ativacao: Ativacao | None
) -> list[GamificacaoPublicSchema]:
    if ativacao is None or not ativacao.gamificacao_id:
        return []

    gamificacao = session.get(Gamificacao, ativacao.gamificacao_id)
    if gamificacao is None:
        return []

    return [
        GamificacaoPublicSchema(
            id=gamificacao.id or 0,
            nome=gamificacao.nome,
            descricao=gamificacao.descricao,
            premio=gamificacao.premio,
            titulo_feedback=gamificacao.titulo_feedback,
            texto_feedback=gamificacao.texto_feedback,
        )
    ]


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
    hero_url = (evento.hero_image_url or "").strip() or None

    required_keys = [field.key for field in fields if field.required]
    optional_keys = [field.key for field in fields if not field.required]
    submit_url = _build_submit_url(evento_id=evento.id or 0, ativacao=ativacao)

    _persist_ativacao_public_urls_if_changed(
        session,
        ativacao=ativacao,
        backend_base_url=backend_base_url,
    )

    event_urls = build_evento_public_urls(evento.id or 0, backend_base_url=backend_base_url)
    ativacao_info = _build_ativacao_info(ativacao)
    gamificacoes = _build_gamificacoes_for_ativacao(session, ativacao=ativacao)

    return LandingPageRead(
        ativacao_id=ativacao.id if ativacao else None,
        ativacao=ativacao_info,
        gamificacoes=gamificacoes,
        evento=LandingEventRead(
            id=evento.id or 0,
            nome=evento.nome,
            cta_personalizado=(evento.cta_personalizado or "").strip() or None,
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


def _find_existing_landing_lead(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    email: str | None,
) -> Lead | None:
    if not email:
        return None

    if ativacao and ativacao.id is not None:
        return session.exec(
            select(Lead)
            .join(AtivacaoLead, AtivacaoLead.lead_id == Lead.id)
            .where(AtivacaoLead.ativacao_id == ativacao.id)
            .where(func.lower(Lead.email) == email)
        ).first()

    return session.exec(
        select(Lead)
        .where(func.lower(Lead.email) == email)
        .where(Lead.evento_nome == evento.nome)
    ).first()


def _create_landing_lead(
    session: Session,
    *,
    evento: Evento,
    payload: LandingSubmitRequest,
    email: str | None,
) -> Lead:
    lead = Lead(
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
    session.add(lead)
    session.flush()
    return lead


def _ensure_ativacao_lead_link(
    session: Session,
    *,
    ativacao: Ativacao | None,
    lead: Lead,
) -> AtivacaoLead | None:
    if ativacao is None or ativacao.id is None or lead.id is None:
        return None

    ativacao_lead = session.exec(
        select(AtivacaoLead)
        .where(AtivacaoLead.ativacao_id == ativacao.id)
        .where(AtivacaoLead.lead_id == lead.id)
    ).first()
    if ativacao_lead is None:
        ativacao_lead = AtivacaoLead(ativacao_id=ativacao.id, lead_id=lead.id)
        try:
            with session.begin_nested():
                session.add(ativacao_lead)
                session.flush()
        except IntegrityError:
            ativacao_lead = session.exec(
                select(AtivacaoLead)
                .where(AtivacaoLead.ativacao_id == ativacao.id)
                .where(AtivacaoLead.lead_id == lead.id)
            ).first()
            if ativacao_lead is None:
                raise
    return ativacao_lead


def _track_submit_success_analytics_if_needed(
    session: Session,
    *,
    evento: Evento,
    ativacao: Ativacao | None,
    payload: LandingSubmitRequest,
) -> None:
    if not (payload.cta_variant_id or payload.landing_session_id):
        return

    template_config = get_template_config(session, evento=evento)
    session.add(
        LandingAnalyticsEvent(
            event_id=evento.id or 0,
            ativacao_id=ativacao.id if ativacao else None,
            categoria=template_config.categoria,
            tema=template_config.tema,
            event_name=ANALYTICS_EVENT_SUBMIT_SUCCESS,
            cta_variant_id=payload.cta_variant_id,
            landing_session_id=payload.landing_session_id,
        )
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
    existing_lead = _find_existing_landing_lead(
        session,
        evento=evento,
        ativacao=ativacao,
        email=email,
    )

    if not existing_lead:
        existing_lead = _create_landing_lead(
            session,
            evento=evento,
            payload=payload,
            email=email,
        )

    ativacao_lead = _ensure_ativacao_lead_link(
        session,
        ativacao=ativacao,
        lead=existing_lead,
    )
    _track_submit_success_analytics_if_needed(
        session,
        evento=evento,
        ativacao=ativacao,
        payload=payload,
    )

    session.commit()
    session.refresh(existing_lead)
    if ativacao_lead:
        session.refresh(ativacao_lead)
    return LandingSubmitResponse(
        lead_id=existing_lead.id or 0,
        event_id=evento.id or 0,
        ativacao_id=ativacao.id if ativacao else None,
        ativacao_lead_id=ativacao_lead.id if ativacao_lead else None,
        mensagem_sucesso=success_message,
    )


def track_landing_analytics(session: Session, *, payload: LandingAnalyticsTrackRequest) -> None:
    session.add(
        LandingAnalyticsEvent(
            event_id=payload.event_id,
            ativacao_id=payload.ativacao_id,
            categoria=payload.categoria,
            tema=payload.tema,
            event_name=payload.event_name,
            cta_variant_id=payload.cta_variant_id,
            landing_session_id=payload.landing_session_id,
        )
    )
    session.commit()


def list_landing_customization_audits(
    session: Session, *, event_id: int, limit: int = 50
) -> list[EventoLandingCustomizationAudit]:
    return session.exec(
        select(EventoLandingCustomizationAudit)
        .where(EventoLandingCustomizationAudit.event_id == event_id)
        .order_by(EventoLandingCustomizationAudit.created_at.desc(), EventoLandingCustomizationAudit.id.desc())
        .limit(limit)
    ).all()


def summarize_landing_analytics(session: Session, *, event_id: int) -> list[LandingAnalyticsSummaryRead]:
    rows = session.exec(
        select(LandingAnalyticsEvent).where(LandingAnalyticsEvent.event_id == event_id)
    ).all()
    grouped: dict[tuple[str, str], dict[str, object]] = {}

    for row in rows:
        key = (row.categoria, row.tema)
        bucket = grouped.setdefault(
            key,
            {
                "page_views": 0,
                "form_starts": 0,
                "submit_attempts": 0,
                "submit_successes": 0,
                "variants": {},
            },
        )
        if row.event_name == ANALYTICS_EVENT_PAGE_VIEW:
            bucket["page_views"] = int(bucket["page_views"]) + 1
        elif row.event_name == ANALYTICS_EVENT_FORM_START:
            bucket["form_starts"] = int(bucket["form_starts"]) + 1
        elif row.event_name == ANALYTICS_EVENT_SUBMIT_ATTEMPT:
            bucket["submit_attempts"] = int(bucket["submit_attempts"]) + 1
        elif row.event_name == ANALYTICS_EVENT_SUBMIT_SUCCESS:
            bucket["submit_successes"] = int(bucket["submit_successes"]) + 1

        if row.cta_variant_id:
            variants = bucket["variants"]
            assert isinstance(variants, dict)
            variant_bucket = variants.setdefault(
                row.cta_variant_id,
                {"views": 0, "submits": 0, "successes": 0},
            )
            if row.event_name in {ANALYTICS_EVENT_PAGE_VIEW, ANALYTICS_EVENT_CTA_EXPOSURE}:
                variant_bucket["views"] += 1
            elif row.event_name == ANALYTICS_EVENT_SUBMIT_ATTEMPT:
                variant_bucket["submits"] += 1
            elif row.event_name == ANALYTICS_EVENT_SUBMIT_SUCCESS:
                variant_bucket["successes"] += 1

    summaries: list[LandingAnalyticsSummaryRead] = []
    for (categoria, tema), bucket in grouped.items():
        page_views = int(bucket["page_views"])
        submit_successes = int(bucket["submit_successes"])
        conversion_rate = round((submit_successes / page_views) if page_views else 0.0, 4)
        variants = bucket["variants"]
        assert isinstance(variants, dict)
        summaries.append(
            LandingAnalyticsSummaryRead(
                event_id=event_id,
                categoria=categoria,
                tema=tema,
                page_views=page_views,
                form_starts=int(bucket["form_starts"]),
                submit_attempts=int(bucket["submit_attempts"]),
                submit_successes=submit_successes,
                conversion_rate=conversion_rate,
                variants=[
                    LandingAnalyticsVariantSummaryRead(
                        cta_variant_id=variant_id,
                        views=counts["views"],
                        submits=counts["submits"],
                        successes=counts["successes"],
                    )
                    for variant_id, counts in sorted(variants.items())
                ],
            )
        )
    return sorted(summaries, key=lambda item: (item.categoria, item.tema))
