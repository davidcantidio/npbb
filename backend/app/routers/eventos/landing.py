"""Rotas de landing (audit, analytics, missing-fields)."""

from __future__ import annotations

import logging
from types import SimpleNamespace

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import EventoTag, EventoTerritorio, StatusEvento, Usuario, now_utc
from app.schemas.landing_public import (
    EventoLandingCustomizationAuditRead,
    LandingAnalyticsSummaryRead,
)
from app.services.data_health import compute_event_missing_fields_details
from app.services.landing_pages import list_landing_customization_audits, summarize_landing_analytics
from sqlmodel import Session, select

from . import _shared

router = APIRouter()
telemetry_logger = logging.getLogger("app.telemetry")


@router.get("/{evento_id}/landing-customizations/audit", response_model=list[EventoLandingCustomizationAuditRead])
def listar_landing_customization_audit(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)
    items = list_landing_customization_audits(session, event_id=evento_id, limit=limit)
    return [EventoLandingCustomizationAuditRead.model_validate(item, from_attributes=True) for item in items]


@router.get("/{evento_id}/landing-analytics", response_model=list[LandingAnalyticsSummaryRead])
def obter_landing_analytics(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _shared._check_evento_visible_or_404(session, evento_id, current_user)
    return summarize_landing_analytics(session, event_id=evento_id)


@router.get("/{evento_id}/missing-fields")
@router.get("/{evento_id}/missing-fields/")
def obter_campos_pendentes(
    evento_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna campos pendentes (com prioridade) para o evento."""
    evento = _shared._check_evento_visible_or_404(session, evento_id, current_user)

    tag_ids = session.exec(
        select(EventoTag.tag_id).where(EventoTag.evento_id == evento_id).order_by(EventoTag.tag_id)
    ).all()
    territorio_ids = session.exec(
        select(EventoTerritorio.territorio_id)
        .where(EventoTerritorio.evento_id == evento_id)
        .order_by(EventoTerritorio.territorio_id)
    ).all()

    status_nome = None
    if evento.status_id:
        status_evento = session.get(StatusEvento, evento.status_id)
        if status_evento:
            status_nome = status_evento.nome

    proxy_data = evento.model_dump()
    proxy_data["tag_ids"] = list(tag_ids)
    proxy_data["territorio_ids"] = list(territorio_ids)

    missing_details = compute_event_missing_fields_details(
        SimpleNamespace(**proxy_data),
        status_name=status_nome,
    )

    telemetry_logger.info(
        "clicked_data_health",
        extra={
            "event_id": evento_id,
            "evento_id": evento_id,
            "field_id": "data_health",
            "user_id": getattr(current_user, "id", None),
        },
    )

    return {
        "evento_id": evento_id,
        "missing_fields": missing_details,
        "total_missing": len(missing_details),
        "last_calculated_at": now_utc(),
    }
