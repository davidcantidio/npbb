"""Prometheus metrics endpoint (NPBB user or optional scrape token)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.core.auth import get_current_user_optional
from app.models.models import Usuario, UsuarioTipo
from app.observability.prometheus_leads_import import metrics_response_body, metrics_token_valid

router = APIRouter(prefix="/internal", tags=["internal"])


def _require_npbb_or_scrape(
    scrape_token: str | None = Query(None, alias="token"),
    user: Usuario | None = Depends(get_current_user_optional),
) -> None:
    if metrics_token_valid(scrape_token):
        return
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais ausentes ou token de scrape invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.tipo_usuario != UsuarioTipo.NPBB:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a usuarios NPBB ou token NPBB_METRICS_SCRAPE_TOKEN.",
        )


@router.get("/metrics", include_in_schema=False)
def prometheus_metrics(
    _: None = Depends(_require_npbb_or_scrape),
) -> Response:
    body, ctype = metrics_response_body()
    return Response(content=body, media_type=ctype)
