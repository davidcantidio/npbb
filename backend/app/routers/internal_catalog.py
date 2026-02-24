"""Internal API endpoints for ETL operational catalog queries.

Endpoints are read-only and designed for observability/audit integration:
- list sources with latest ingestion metadata,
- list ingestion runs with source context.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.etl_registry import IngestionStatus, SourceKind
from app.models.models import Usuario, UsuarioTipo
from app.schemas.internal_catalog import CatalogIngestionRead, CatalogSourceRead
from app.services.etl_catalog_queries import latest_ingestion_by_source, list_ingestion_runs


router = APIRouter(prefix="/internal/catalog", tags=["internal"])


def require_npbb_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Allow access only to NPBB users.

    Args:
        current_user: Authenticated user resolved from bearer token.

    Returns:
        Current authenticated user when type is NPBB.

    Raises:
        HTTPException: When user is not NPBB.
    """

    if current_user.tipo_usuario != UsuarioTipo.NPBB:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Acesso restrito a usuarios NPBB"},
        )
    return current_user


def _validate_pagination(limit: int, offset: int) -> None:
    """Validate pagination inputs for internal catalog endpoints.

    Args:
        limit: Maximum number of rows returned by one call.
        offset: Number of rows skipped from the start.

    Raises:
        HTTPException: If `limit` or `offset` values are outside accepted range.
    """

    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})
    if offset < 0:
        raise HTTPException(status_code=400, detail={"code": "BAD_OFFSET", "message": "offset invalido"})


@router.get("/sources", response_model=list[CatalogSourceRead])
def list_catalog_sources(
    status_in: Optional[IngestionStatus] = Query(default=None, alias="status"),
    source_type: Optional[SourceKind] = Query(default=None),
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """List sources with latest ingestion metadata and basic filters.

    Args:
        status_in: Optional latest-ingestion status filter.
        source_type: Optional source kind filter (`pdf`, `xlsx`, `pptx`, ...).
        limit: Maximum number of rows in the response.
        offset: Offset used for pagination.
        session: Open SQLModel session dependency.
        _user: Authenticated NPBB user dependency.

    Returns:
        List of source rows with latest ingestion context.

    Raises:
        HTTPException: If pagination inputs are invalid.
    """

    _validate_pagination(limit, offset)
    rows = latest_ingestion_by_source(
        session,
        statuses=[status_in] if status_in is not None else None,
        source_kinds=[source_type] if source_type is not None else None,
    )
    return rows[offset : offset + limit]


@router.get("/ingestions", response_model=list[CatalogIngestionRead])
def list_catalog_ingestions(
    status_in: Optional[IngestionStatus] = Query(default=None, alias="status"),
    source_type: Optional[SourceKind] = Query(default=None),
    source_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """List ingestion runs with source metadata and filters.

    Args:
        status_in: Optional ingestion status filter.
        source_type: Optional source kind filter (`pdf`, `xlsx`, `pptx`, ...).
        source_id: Optional exact source identifier filter.
        limit: Maximum number of rows in the response.
        offset: Offset used for pagination.
        session: Open SQLModel session dependency.
        _user: Authenticated NPBB user dependency.

    Returns:
        List of ingestion rows enriched with source metadata.

    Raises:
        HTTPException: If pagination inputs are invalid.
    """

    _validate_pagination(limit, offset)
    return list_ingestion_runs(
        session,
        statuses=[status_in] if status_in is not None else None,
        source_kinds=[source_type] if source_type is not None else None,
        source_ids=[source_id] if source_id else None,
        limit=limit,
        offset=offset,
    )
