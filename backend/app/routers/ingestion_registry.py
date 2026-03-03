"""Internal endpoints for ingestion registry and lineage.

These endpoints are intended for operational use (auditing runs, debugging ETL).
They are protected to NPBB users only.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.models import (
    IngestionRun,
    IngestionStatus,
    MetricLineage,
    Source,
    SourceKind,
    Usuario,
)
from app.platform.security.rbac import require_npbb_user
from app.schemas.ingestion_registry import (
    IngestionDetailRead,
    IngestionRead,
    MetricLineageRead,
    SourceRead,
)


router = APIRouter(prefix="/internal/registry", tags=["internal"])


@router.get("/sources", response_model=list[SourceRead])
def list_sources(
    kind: Optional[SourceKind] = None,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    stmt = select(Source).order_by(Source.source_id)
    if kind is not None:
        stmt = stmt.where(Source.kind == kind)
    return session.exec(stmt).all()


@router.get("/ingestions", response_model=list[IngestionRead])
def list_ingestions(
    source_id: Optional[str] = None,
    status_in: Optional[IngestionStatus] = None,
    limit: int = 100,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    if limit <= 0 or limit > 1000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})

    stmt = select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)
    if source_id:
        stmt = stmt.where(IngestionRun.source_id == source_id)
    if status_in is not None:
        stmt = stmt.where(IngestionRun.status == status_in)
    return session.exec(stmt).all()


@router.get("/ingestions/{ingestion_id}", response_model=IngestionDetailRead)
def get_ingestion(
    ingestion_id: int,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    run = session.get(IngestionRun, ingestion_id)
    if run is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "ingestion nao encontrada"})
    return run


@router.get("/lineage", response_model=list[MetricLineageRead])
def list_lineage(
    metric_key: Optional[str] = None,
    source_id: Optional[str] = None,
    docx_section: Optional[str] = None,
    limit: int = 200,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    if limit <= 0 or limit > 5000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})

    stmt = select(MetricLineage).order_by(MetricLineage.created_at.desc()).limit(limit)
    if metric_key:
        stmt = stmt.where(MetricLineage.metric_key == metric_key)
    if source_id:
        stmt = stmt.where(MetricLineage.source_id == source_id)
    if docx_section:
        stmt = stmt.where(MetricLineage.docx_section == docx_section)
    return session.exec(stmt).all()
