"""Internal endpoints for Data Quality + Observabilidade.

These endpoints expose:
- persisted quality check results,
- evidence summaries (layout signatures),
- and operational health views per source/session.

Protected to NPBB users only.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import (
    AttendanceAccessControl,
    DataQualityResult,
    DataQualityScope,
    DataQualitySeverity,
    DataQualityStatus,
    EventSession,
    FestivalLead,
    IngestionEvidence,
    IngestionRun,
    OptinTransaction,
    Source,
    Usuario,
    UsuarioTipo,
)
from app.schemas.data_quality import (
    DataQualityResultRead,
    DataQualitySummaryRead,
    IngestionEvidenceRead,
)
from app.services.data_quality import quality_gate_blocked, quality_summary


router = APIRouter(prefix="/internal/quality", tags=["internal"])


def require_npbb_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario != UsuarioTipo.NPBB:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Acesso restrito a usuarios NPBB"},
        )
    return current_user


@router.get("/results", response_model=list[DataQualityResultRead])
def list_quality_results(
    ingestion_id: Optional[int] = None,
    source_id: Optional[str] = None,
    scope: Optional[DataQualityScope] = None,
    severity: Optional[DataQualitySeverity] = None,
    status_in: Optional[DataQualityStatus] = None,
    limit: int = 500,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    if limit <= 0 or limit > 5000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})

    stmt = select(DataQualityResult).order_by(DataQualityResult.created_at.desc()).limit(limit)
    if ingestion_id is not None:
        stmt = stmt.where(DataQualityResult.ingestion_id == ingestion_id)
    if source_id:
        stmt = stmt.where(DataQualityResult.source_id == source_id)
    if scope is not None:
        stmt = stmt.where(DataQualityResult.scope == scope)
    if severity is not None:
        stmt = stmt.where(DataQualityResult.severity == severity)
    if status_in is not None:
        stmt = stmt.where(DataQualityResult.status == status_in)
    return session.exec(stmt).all()


@router.get("/summary", response_model=DataQualitySummaryRead)
def get_quality_summary(
    ingestion_id: int,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    run = session.get(IngestionRun, ingestion_id)
    if run is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "ingestion nao encontrada"})
    counts = quality_summary(session, ingestion_id=ingestion_id)
    return DataQualitySummaryRead(
        ingestion_id=ingestion_id,
        source_id=run.source_id,
        total=int(counts["total"]),
        error_fail=int(counts["error_fail"]),
        warn_fail=int(counts["warn_fail"]),
        passed=int(counts["passed"]),
        gate_blocked=bool(quality_gate_blocked(session, ingestion_id=ingestion_id)),
    )


@router.get("/evidence", response_model=list[IngestionEvidenceRead])
def list_ingestion_evidence(
    ingestion_id: Optional[int] = None,
    source_id: Optional[str] = None,
    limit: int = 200,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    if limit <= 0 or limit > 5000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})
    stmt = select(IngestionEvidence).order_by(IngestionEvidence.created_at.desc()).limit(limit)
    if ingestion_id is not None:
        stmt = stmt.where(IngestionEvidence.ingestion_id == ingestion_id)
    if source_id:
        stmt = stmt.where(IngestionEvidence.source_id == source_id)
    return session.exec(stmt).all()


@router.get("/health/sources")
def health_sources(
    limit: int = 200,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """Operational health per source (latest ingestion + DQ counts)."""
    if limit <= 0 or limit > 2000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})

    # Latest ingestion per source.
    sub = (
        select(IngestionRun.source_id, func.max(IngestionRun.started_at).label("max_started"))
        .group_by(IngestionRun.source_id)
        .subquery()
    )
    stmt = (
        select(Source, IngestionRun)
        .join(sub, sub.c.source_id == Source.source_id, isouter=True)
        .join(
            IngestionRun,
            (IngestionRun.source_id == sub.c.source_id) & (IngestionRun.started_at == sub.c.max_started),
            isouter=True,
        )
        .order_by(Source.source_id)
        .limit(limit)
    )

    rows = session.exec(stmt).all()
    out: list[dict] = []
    for src, run in rows:
        if run is None:
            out.append(
                {
                    "source_id": src.source_id,
                    "kind": src.kind,
                    "uri": src.uri,
                    "latest_ingestion_id": None,
                    "latest_status": None,
                    "latest_started_at": None,
                    "dq_error_fail": 0,
                    "dq_warn_fail": 0,
                    "dq_gate_blocked": False,
                }
            )
            continue

        counts = quality_summary(session, ingestion_id=run.id)
        out.append(
            {
                "source_id": src.source_id,
                "kind": src.kind,
                "uri": src.uri,
                "latest_ingestion_id": run.id,
                "latest_status": run.status,
                "latest_started_at": run.started_at,
                "dq_error_fail": int(counts["error_fail"]),
                "dq_warn_fail": int(counts["warn_fail"]),
                "dq_gate_blocked": bool(quality_gate_blocked(session, ingestion_id=run.id)),
            }
        )
    return out


@router.get("/health/sessions")
def health_sessions(
    limit: int = 500,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """Operational health per session (coverage + DQ counts)."""
    if limit <= 0 or limit > 5000:
        raise HTTPException(status_code=400, detail={"code": "BAD_LIMIT", "message": "limit invalido"})

    # Coverage computed from canonical tables (avoid relying on DB views during tests).
    stmt = (
        select(
            EventSession.id,
            EventSession.session_key,
            EventSession.session_name,
            EventSession.session_type,
            EventSession.session_date,
            (func.count(OptinTransaction.id) > 0).label("has_optin"),
            (func.count(AttendanceAccessControl.id) > 0).label("has_access_control"),
            (func.count(FestivalLead.id) > 0).label("has_leads"),
        )
        .join(OptinTransaction, OptinTransaction.session_id == EventSession.id, isouter=True)
        .join(AttendanceAccessControl, AttendanceAccessControl.session_id == EventSession.id, isouter=True)
        .join(FestivalLead, FestivalLead.session_id == EventSession.id, isouter=True)
        .group_by(
            EventSession.id,
            EventSession.session_key,
            EventSession.session_name,
            EventSession.session_type,
            EventSession.session_date,
        )
        .order_by(EventSession.session_date, EventSession.session_type, EventSession.session_key)
        .limit(limit)
    )
    sessions = session.exec(stmt).all()

    # DQ counts per session.
    dq_stmt = (
        select(
            DataQualityResult.session_id,
            func.sum(
                case(
                    (
                        (DataQualityResult.severity == DataQualitySeverity.ERROR)
                        & (DataQualityResult.status == DataQualityStatus.FAIL),
                        1,
                    ),
                    else_=0,
                )
            ).label("error_fail"),
            func.sum(
                case(
                    (
                        (DataQualityResult.severity == DataQualitySeverity.WARN)
                        & (DataQualityResult.status == DataQualityStatus.FAIL),
                        1,
                    ),
                    else_=0,
                )
            ).label("warn_fail"),
        )
        .where(DataQualityResult.session_id.is_not(None))
        .group_by(DataQualityResult.session_id)
    )
    dq_by_session = {
        int(sid): {"error_fail": int(err or 0), "warn_fail": int(warn or 0)}
        for sid, err, warn in session.exec(dq_stmt).all()
        if sid is not None
    }

    out: list[dict] = []
    for sid, key, name, typ, day, has_optin, has_ac, has_leads in sessions:
        dq = dq_by_session.get(int(sid), {"error_fail": 0, "warn_fail": 0})
        out.append(
            {
                "session_id": sid,
                "session_key": key,
                "session_name": name,
                "session_type": typ,
                "session_date": day,
                "has_optin": bool(has_optin),
                "has_access_control": bool(has_ac),
                "has_leads": bool(has_leads),
                "dq_error_fail": dq["error_fail"],
                "dq_warn_fail": dq["warn_fail"],
            }
        )
    return out
