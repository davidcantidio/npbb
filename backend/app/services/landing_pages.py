"""Servico de resolucao e montagem das landing pages publicas."""

from __future__ import annotations

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
    LandingEventRead,
    LandingFieldRead,
    LandingFormRead,
    LandingPageRead,
    LandingSubmitRequest,
    LandingSubmitResponse,
)
from app.services.formulario_lead_catalog import (
    FORMULARIO_CAMPOS_DEFAULT,
    FORMULARIO_CAMPOS_ORDEM_BY_LOWER,
    get_form_field_definition,
)
from app.services.landing_page_templates import (
    TEMPLATE_REGISTRY,
    get_allowed_template_overrides,
    get_template_config,
    normalize_template_override_input,
    resolve_template_category,
)
from app.services.landing_page_submission import submit_landing_lead
from app.services.qr_code import build_qr_code_data_url
from app.utils.urls import build_ativacao_public_urls, build_evento_public_urls

PRIVACY_POLICY_URL = "https://www.bb.com.br/site/privacidade-e-lgpd/"
BRAND_TAGLINE = "Banco do Brasil. Pra tudo que voce imaginar."

ANALYTICS_EVENT_PAGE_VIEW = "page_view"
ANALYTICS_EVENT_FORM_START = "form_start"
ANALYTICS_EVENT_SUBMIT_ATTEMPT = "submit_attempt"
ANALYTICS_EVENT_SUBMIT_SUCCESS = "submit_success"
ANALYTICS_EVENT_CTA_EXPOSURE = "cta_exposure"


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
    template_override: str | None = None,
) -> LandingPageRead:
    fields, template_name = get_landing_fields(session, evento=evento)
    template = get_template_config(
        session,
        evento=evento,
        template_name=template_name,
        template_override=template_override,
    )
    template_data = TEMPLATE_REGISTRY[template.categoria]

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
        ),
        acesso=LandingAccessRead(
            landing_url=ativacao.landing_url if ativacao else event_urls["url_landing"],
            qr_code_url=ativacao.qr_code_url if ativacao else None,
            url_promotor=ativacao.url_promotor if ativacao else event_urls["url_landing"],
        ),
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
