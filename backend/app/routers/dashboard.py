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
from app.schemas.dashboard import (
    AGE_ANALYSIS_RESPONSE_EXAMPLE,
    AgeAnalysisQuery,
    AgeAnalysisResponse,
)
from app.services.dashboard_service import build_age_analysis

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _parse_age_analysis_query(
    data_inicio: date | None = Query(
        default=None,
        description="Data inicial do filtro sobre a criacao do lead. Intervalo inclusivo.",
        openapi_examples={
            "inicio_janeiro": {
                "summary": "Inicio do periodo",
                "value": "2026-01-01",
            }
        },
    ),
    data_fim: date | None = Query(
        default=None,
        description="Data final do filtro sobre a criacao do lead. Intervalo inclusivo.",
        openapi_examples={
            "fim_janeiro": {
                "summary": "Fim do periodo",
                "value": "2026-01-31",
            }
        },
    ),
    evento_id: int | None = Query(
        default=None,
        ge=1,
        description="Filtra a analise para um evento especifico.",
        openapi_examples={
            "evento_especifico": {
                "summary": "Filtrar por evento",
                "value": 42,
            }
        },
    ),
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
    status_code=200,
    summary="Analise etaria de leads por evento",
    description=(
        "Retorna a distribuicao etaria por evento e o consolidado geral, "
        "com cobertura de cruzamento BB e filtros opcionais."
    ),
    response_description="Payload tipado da analise etaria consolidada e por evento.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": AGE_ANALYSIS_RESPONSE_EXAMPLE,
                }
            }
        }
    },
)
def dashboard_leads_age_analysis(
    params: AgeAnalysisQuery = Depends(_parse_age_analysis_query),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return build_age_analysis(session, params, current_user)
