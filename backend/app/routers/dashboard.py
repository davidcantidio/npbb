"""Endpoints de dashboard focados em analises consolidadas."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Usuario
from app.schemas.dashboard import AgeAnalysisQuery, AgeAnalysisResponse
from app.services.dashboard_service import build_age_analysis

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _parse_age_analysis_query(
    data_inicio: date | None = Query(default=None),
    data_fim: date | None = Query(default=None),
    evento_id: int | None = Query(default=None, ge=1),
) -> AgeAnalysisQuery:
    try:
        return AgeAnalysisQuery(
            data_inicio=data_inicio,
            data_fim=data_fim,
            evento_id=evento_id,
        )
    except ValidationError as exc:
        raise RequestValidationError(exc.errors()) from exc


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
    params: AgeAnalysisQuery = Depends(_parse_age_analysis_query),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return build_age_analysis(session, params, current_user)
