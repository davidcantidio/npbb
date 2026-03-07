"""Endpoints de dashboard focados em analises consolidadas."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Usuario
from app.schemas.dashboard import AgeAnalysisQuery, AgeAnalysisResponse
from app.services.dashboard_service import build_age_analysis

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/leads/analise-etaria",
    response_model=AgeAnalysisResponse,
    summary="Analise etaria de leads por evento",
    description=(
        "Retorna a distribuicao etaria por evento e o consolidado geral, "
        "com cobertura de cruzamento BB e filtros opcionais."
    ),
)
def dashboard_leads_age_analysis(
    params: AgeAnalysisQuery = Depends(),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return build_age_analysis(session, params, current_user)
