"""Consolidated internal ETL API endpoints.

This router provides one canonical namespace (`/internal/etl/*`) while legacy
routes remain available during migration.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.database import get_session
from app.models.etl_registry import IngestionStatus, SourceKind
from app.models.models import Usuario
from app.platform.security.rbac import require_npbb_user
from app.schemas.internal_catalog import CatalogIngestionRead, CatalogSourceRead
from app.services.etl_catalog_queries import latest_ingestion_by_source, list_ingestion_runs


router = APIRouter(prefix="/internal/etl", tags=["internal"])


def _validate_pagination(limit: int, offset: int) -> None:
    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})
    if offset < 0:
        raise HTTPException(status_code=400, detail={"code": "BAD_OFFSET", "message": "offset invalido"})


@router.get("/sources", response_model=list[CatalogSourceRead])
def list_etl_sources(
    status_in: Optional[IngestionStatus] = Query(default=None, alias="status"),
    source_type: Optional[SourceKind] = Query(default=None),
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    _validate_pagination(limit, offset)
    rows = latest_ingestion_by_source(
        session,
        statuses=[status_in] if status_in is not None else None,
        source_kinds=[source_type] if source_type is not None else None,
        limit=limit,
        offset=offset,
    )
    return rows


@router.get("/ingestions", response_model=list[CatalogIngestionRead])
def list_etl_ingestions(
    status_in: Optional[IngestionStatus] = Query(default=None, alias="status"),
    source_type: Optional[SourceKind] = Query(default=None),
    source_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    _validate_pagination(limit, offset)
    return list_ingestion_runs(
        session,
        statuses=[status_in] if status_in is not None else None,
        source_kinds=[source_type] if source_type is not None else None,
        source_ids=[source_id] if source_id else None,
        limit=limit,
        offset=offset,
    )
