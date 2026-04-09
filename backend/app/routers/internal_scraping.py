"""Internal API endpoints for scraping ingestion persistence."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.db.database import get_session
from app.models.models import Usuario
from app.platform.security.rbac import require_npbb_user

# TODO(npbb): conectar aos contratos definitivos de schema ao integrar o modulo.
from app.schemas.scraping_ingestion import ScrapingIngestionPayload, ScrapingIngestionResponse

# TODO(npbb): conectar ao service layer definitivo ao integrar o modulo.
from app.services.scraping_ingestion_service import (
    ScrapingIngestionServiceError,
    ingest_scraping_payload,
)


router = APIRouter(prefix="/internal/scraping", tags=["internal"])
logger = logging.getLogger(__name__)


def _build_error_detail(code: str, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    detail: dict[str, Any] = {"code": code, "message": message}
    if extra:
        detail["extra"] = extra
    return detail


def _is_empty_payload(payload: ScrapingIngestionPayload) -> bool:
    payload_dict = payload.model_dump(exclude_none=True)
    return len(payload_dict) == 0


def _status_code_from_service_error(exc: ScrapingIngestionServiceError) -> int:
    error_code = str(getattr(exc, "code", "") or "").upper()
    if any(token in error_code for token in ("INVALID", "VALIDATION", "PAYLOAD", "BAD_REQUEST")):
        return status.HTTP_400_BAD_REQUEST
    if any(token in error_code for token in ("CONFLICT", "DEDUP", "DUPLICATE")):
        return status.HTTP_409_CONFLICT

    default_status_code = getattr(exc, "status_code", None)
    if isinstance(default_status_code, int) and default_status_code in (
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_409_CONFLICT,
    ):
        return default_status_code

    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _extract_ingestion_context(payload: ScrapingIngestionPayload) -> dict[str, Any]:
    payload_dict = payload.model_dump(exclude_none=True)
    return {
        "sponsor_id": payload_dict.get("sponsor_id"),
        "sponsor_slug": payload_dict.get("sponsor_slug"),
        "handle": payload_dict.get("handle") or payload_dict.get("profile_handle"),
    }


@router.post(
    "/ingestions",
    response_model=ScrapingIngestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scraping_ingestion(
    payload: ScrapingIngestionPayload,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
) -> ScrapingIngestionResponse:
    """Receive scraping payload and delegate persistence to service layer."""

    if _is_empty_payload(payload):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_build_error_detail(
                code="SCRAPING_PAYLOAD_INVALIDO",
                message="Payload de scraping vazio ou invalido.",
            ),
        )

    context = _extract_ingestion_context(payload)
    logger.info(
        "Iniciando ingestao de scraping.",
        extra={
            "sponsor_id": context.get("sponsor_id"),
            "sponsor_slug": context.get("sponsor_slug"),
            "handle": context.get("handle"),
        },
    )

    try:
        result = ingest_scraping_payload(session=session, payload=payload)
    except ScrapingIngestionServiceError as exc:
        mapped_status_code = _status_code_from_service_error(exc)
        error_code = str(getattr(exc, "code", "") or "SCRAPING_INGESTION_ERRO")
        error_message = str(getattr(exc, "message", "") or "Falha ao processar ingestao de scraping.")
        error_extra = getattr(exc, "extra", None)

        logger.warning(
            "Falha de dominio na ingestao de scraping.",
            extra={
                "error_type": exc.__class__.__name__,
                "error_code": error_code,
                "status_code": mapped_status_code,
                "sponsor_id": context.get("sponsor_id"),
                "sponsor_slug": context.get("sponsor_slug"),
                "handle": context.get("handle"),
            },
        )
        raise HTTPException(
            status_code=mapped_status_code,
            detail=_build_error_detail(
                code=error_code,
                message=error_message,
                extra=error_extra if isinstance(error_extra, dict) else None,
            ),
        ) from exc
    except Exception as exc:  # pragma: no cover - guardrail for unexpected runtime failures.
        logger.exception(
            "Erro inesperado na ingestao de scraping.",
            extra={
                "error_type": exc.__class__.__name__,
                "sponsor_id": context.get("sponsor_id"),
                "sponsor_slug": context.get("sponsor_slug"),
                "handle": context.get("handle"),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_build_error_detail(
                code="SCRAPING_INGESTION_INTERNAL_ERROR",
                message="Erro interno ao processar ingestao de scraping.",
            ),
        ) from exc

    if hasattr(result, "model_dump"):
        result_dict = result.model_dump(exclude_none=True)
    elif isinstance(result, dict):
        result_dict = result
    else:
        result_dict = {}
    logger.info(
        "Ingestao de scraping concluida com sucesso.",
        extra={
            "ingestion_id": result_dict.get("ingestion_id") or result_dict.get("run_id"),
            "sponsor_id": result_dict.get("sponsor_id") or context.get("sponsor_id"),
            "sponsor_slug": result_dict.get("sponsor_slug") or context.get("sponsor_slug"),
            "posts_inserted": result_dict.get("posts_inserted"),
            "posts_updated": result_dict.get("posts_updated"),
            "profiles_inserted": result_dict.get("profiles_inserted"),
            "profiles_updated": result_dict.get("profiles_updated"),
            "indicators_inserted": result_dict.get("indicators_inserted"),
            "indicators_updated": result_dict.get("indicators_updated"),
        },
    )
    return result


@router.get("/health")
def internal_scraping_health(
    _user: Usuario = Depends(require_npbb_user),
) -> dict[str, str]:
    """Return internal module health status."""

    return {"status": "ok", "module": "internal_scraping"}
