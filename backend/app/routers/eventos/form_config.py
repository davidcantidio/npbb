"""Rotas de configuração do formulário de lead e preview da landing."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import delete as sa_delete
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    FormularioLandingTemplate,
    FormularioLeadCampo,
    FormularioLeadConfig,
    Usuario,
    now_utc,
)
from app.schemas.formulario_lead import (
    FormularioLeadCampoRead,
    FormularioLeadConfigRead,
    FormularioLeadConfigUpsert,
    FormularioLeadPreviewRequest,
)
from app.schemas.landing_public import LandingPageRead
from app.services.formulario_lead_catalog import (
    FORMULARIO_CAMPOS_DEFAULT,
    FORMULARIO_CAMPOS_ORDEM_BY_LOWER,
)
from app.services.landing_pages import (
    build_landing_fields_from_config,
    build_landing_payload,
    get_formulario_template_name_by_id,
)
from app.utils.urls import build_evento_public_urls

from . import _shared

router = APIRouter()


@router.get("/{evento_id}/form-config", response_model=FormularioLeadConfigRead)
@router.get("/{evento_id}/form-config/", response_model=FormularioLeadConfigRead)
def obter_formulario_lead_config(
    evento_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna a configuração da Landing Page para um evento."""
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    computed_urls = build_evento_public_urls(evento_id, backend_base_url=str(request.base_url))

    config = session.exec(
        select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)
    ).first()
    if not config:
        default_campos = [
            FormularioLeadCampoRead(
                nome_campo=nome,
                obrigatorio=obrigatorio,
                ordem=FORMULARIO_CAMPOS_ORDEM_BY_LOWER.get(nome.lower(), 0),
            )
            for nome, obrigatorio in FORMULARIO_CAMPOS_DEFAULT
        ]
        return FormularioLeadConfigRead(
            evento_id=evento_id, template_id=None, campos=default_campos, **computed_urls
        )

    campos = session.exec(
        select(FormularioLeadCampo)
        .where(FormularioLeadCampo.config_id == config.id)
        .order_by(FormularioLeadCampo.ordem, FormularioLeadCampo.id)
    ).all()

    read = FormularioLeadConfigRead.model_validate(config, from_attributes=True)
    url_updates = {key: value for key, value in computed_urls.items() if getattr(read, key) is None}
    return read.model_copy(
        update={
            "campos": [
                FormularioLeadCampoRead.model_validate(c, from_attributes=True) for c in campos
            ],
            **url_updates,
        }
    )


@router.post("/{evento_id}/landing-preview", response_model=LandingPageRead)
@router.post("/{evento_id}/landing-preview/", response_model=LandingPageRead)
def preview_formulario_lead_landing(
    evento_id: int,
    payload: FormularioLeadPreviewRequest,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    evento = _shared._check_evento_visible_or_404(session, evento_id, current_user)

    transient_updates: dict[str, str | None] = {}
    if "template_override" in payload.model_fields_set:
        transient_updates["template_override"] = _shared._normalize_template_override_or_error(
            payload.template_override
        )
    if "cta_personalizado" in payload.model_fields_set:
        transient_updates["cta_personalizado"] = _shared._normalize_str(payload.cta_personalizado)
    if "descricao_curta" in payload.model_fields_set:
        transient_updates["descricao_curta"] = _shared._normalize_str(payload.descricao_curta)

    preview_evento = evento.model_copy(update=transient_updates) if transient_updates else evento

    preview_kwargs: dict[str, object] = {}
    if "template_id" in payload.model_fields_set:
        if payload.template_id is not None:
            _shared._validate_fk(
                session,
                FormularioLandingTemplate,
                payload.template_id,
                "FORM_TEMPLATE_NOT_FOUND",
                "Template nao encontrado",
            )
        preview_kwargs["template_name_override"] = get_formulario_template_name_by_id(
            session, payload.template_id
        )

    if "campos" in payload.model_fields_set:
        preview_kwargs["fields_override"] = build_landing_fields_from_config(payload.campos or [])

    return build_landing_payload(
        session,
        evento=preview_evento,
        ativacao=None,
        backend_base_url=str(request.base_url),
        **preview_kwargs,
    )


@router.put("/{evento_id}/form-config", response_model=FormularioLeadConfigRead)
@router.put("/{evento_id}/form-config/", response_model=FormularioLeadConfigRead)
def upsert_formulario_lead_config(
    evento_id: int,
    payload: FormularioLeadConfigUpsert,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Cria/atualiza config da Landing Page (MVP: template + campos)."""
    _shared._check_evento_visible_or_404(session, evento_id, current_user)

    update_template = "template_id" in payload.model_fields_set
    if update_template and payload.template_id is not None:
        _shared._validate_fk(
            session,
            FormularioLandingTemplate,
            payload.template_id,
            "FORM_TEMPLATE_NOT_FOUND",
            "Template nao encontrado",
        )

    config = session.exec(
        select(FormularioLeadConfig).where(FormularioLeadConfig.evento_id == evento_id)
    ).first()
    if not config:
        config = FormularioLeadConfig(
            evento_id=evento_id,
            nome="Landing Page",
        )
    if update_template:
        config.template_id = payload.template_id
    config.atualizado_em = now_utc()
    session.add(config)

    replace_campos = "campos" in payload.model_fields_set

    try:
        session.flush()

        if replace_campos:
            session.exec(
                sa_delete(FormularioLeadCampo).where(FormularioLeadCampo.config_id == config.id)
            )
            for campo in payload.campos:
                session.add(
                    FormularioLeadCampo(
                        config_id=config.id,
                        nome_campo=campo.nome_campo.strip(),
                        obrigatorio=campo.obrigatorio,
                        ordem=campo.ordem,
                    )
                )

        session.commit()
    except Exception:
        session.rollback()
        raise

    session.refresh(config)

    campos = session.exec(
        select(FormularioLeadCampo)
        .where(FormularioLeadCampo.config_id == config.id)
        .order_by(FormularioLeadCampo.ordem, FormularioLeadCampo.id)
    ).all()

    computed_urls = build_evento_public_urls(evento_id, backend_base_url=str(request.base_url))
    read = FormularioLeadConfigRead.model_validate(config, from_attributes=True)
    url_updates = {key: value for key, value in computed_urls.items() if getattr(read, key) is None}
    return read.model_copy(
        update={
            "campos": [
                FormularioLeadCampoRead.model_validate(c, from_attributes=True) for c in campos
            ],
            **url_updates,
        }
    )
