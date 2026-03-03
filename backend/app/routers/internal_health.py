"""Internal read-only API endpoints for ETL health and session coverage.

Endpoints in this router are intended for operational observability and
triage, exposing:
- source health status snapshots (latest ingestion + DQ/load counters),
- session coverage matrix summary by dataset requirements.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.database import get_session
from app.models.etl_registry import IngestionStatus, SourceKind
from app.models.models import Usuario
from app.platform.security.rbac import require_npbb_user
from app.services.etl_health_queries import (
    build_health_alerts,
    build_coverage_health_payload,
    list_source_health_status,
    source_health_rows_to_dicts,
    source_health_summary_to_dict,
    summarize_source_health,
)


router = APIRouter(prefix="/internal/health", tags=["internal"])


def _validate_pagination(limit: int, offset: int) -> None:
    """Validate basic pagination parameters.

    Args:
        limit: Maximum rows returned by call.
        offset: Rows skipped from beginning.

    Raises:
        HTTPException: When limit/offset are outside accepted range.
    """

    if limit <= 0 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_LIMIT", "message": "limit invalido"},
        )
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_OFFSET", "message": "offset invalido"},
        )


def _summarize_coverage_sessions(sessions: list[dict[str, Any]]) -> dict[str, int]:
    """Build session coverage counters from session rows.

    Args:
        sessions: Coverage session rows with `status` field.

    Returns:
        Dictionary with `total_sessions`, `ok_sessions`, `partial_sessions`,
        and `gap_sessions`.
    """

    total = len(sessions)
    ok = sum(1 for row in sessions if row.get("status") == "ok")
    partial = sum(1 for row in sessions if row.get("status") == "partial")
    gap = total - ok - partial
    return {
        "total_sessions": int(total),
        "ok_sessions": int(ok),
        "partial_sessions": int(partial),
        "gap_sessions": int(gap),
    }


@router.get("/sources")
def get_health_sources(
    status_in: Optional[IngestionStatus] = Query(default=None, alias="status"),
    source_type: Optional[SourceKind] = Query(default=None),
    limit: int = 100,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """Return paginated ETL source-health snapshot with basic filters.

    Args:
        status_in: Optional filter by latest ingestion status.
        source_type: Optional filter by source kind.
        limit: Maximum rows returned.
        offset: Pagination offset.
        session: Open SQLModel session.
        _user: Authenticated NPBB user.

    Returns:
        Source-health payload with summary counters and paginated items.

    Raises:
        HTTPException: If pagination values are invalid.
    """

    _validate_pagination(limit, offset)
    rows = list_source_health_status(
        session,
        statuses=[status_in] if status_in is not None else None,
        source_kinds=[source_type] if source_type is not None else None,
    )
    total = len(rows)
    page_rows = rows[offset : offset + limit]
    summary = summarize_source_health(rows)
    health_payload = {
        "summary": source_health_summary_to_dict(summary),
        "items": source_health_rows_to_dicts(rows),
    }
    return {
        "total": int(total),
        "limit": int(limit),
        "offset": int(offset),
        "summary": source_health_summary_to_dict(summary),
        "items": source_health_rows_to_dicts(page_rows),
        "alerts": build_health_alerts(health_payload=health_payload, coverage_payload=None),
    }


@router.get("/coverage")
def get_health_coverage(
    event_id: Optional[int] = None,
    status_in: Optional[str] = Query(
        default=None,
        alias="status",
        pattern="^(ok|partial|gap)$",
    ),
    limit: int = 200,
    offset: int = 0,
    session: Session = Depends(get_session),
    _user: Usuario = Depends(require_npbb_user),
):
    """Return paginated session-coverage snapshot for ETL health.

    Args:
        event_id: Optional event scope for coverage matrix.
        status_in: Optional filter over session coverage status.
        limit: Maximum session rows returned.
        offset: Session pagination offset.
        session: Open SQLModel session.
        _user: Authenticated NPBB user.

    Returns:
        Coverage payload with session summary, paginated sessions and matrix.

    Raises:
        HTTPException: If pagination values are invalid.
    """

    _validate_pagination(limit, offset)
    payload = build_coverage_health_payload(session, event_id=event_id)
    health_rows = list_source_health_status(session)
    health_payload = {
        "summary": source_health_summary_to_dict(summarize_source_health(health_rows)),
        "items": source_health_rows_to_dicts(health_rows),
    }

    sessions_all = list(payload.get("sessions", []))
    if status_in is not None:
        sessions_all = [
            row
            for row in sessions_all
            if isinstance(row, dict) and row.get("status") == status_in
        ]

    total = len(sessions_all)
    page_sessions = sessions_all[offset : offset + limit]
    sessions_all_ids = {
        int(item["session_id"])
        for item in sessions_all
        if isinstance(item, dict) and item.get("session_id") is not None
    }
    page_session_ids = {
        int(item["session_id"])
        for item in page_sessions
        if isinstance(item, dict) and item.get("session_id") is not None
    }
    matrix = [
        row
        for row in payload.get("matrix", [])
        if isinstance(row, dict) and row.get("session_id") in page_session_ids
    ]
    matrix_all = [
        row
        for row in payload.get("matrix", [])
        if isinstance(row, dict) and row.get("session_id") in sessions_all_ids
    ]
    coverage_for_alerts = {
        **payload,
        "sessions": sessions_all,
        "matrix": matrix_all,
    }

    response: dict[str, Any] = {
        "generated_at": payload.get("generated_at"),
        "event_id": event_id,
        "status": payload.get("status"),
        "reason": payload.get("reason"),
        "total": int(total),
        "limit": int(limit),
        "offset": int(offset),
        "summary": _summarize_coverage_sessions(page_sessions),
        "sessions": page_sessions,
        "matrix": matrix,
        "unresolved_without_session": payload.get("unresolved_without_session", {}),
        "config": payload.get("config", {}),
        "alerts": build_health_alerts(
            health_payload=health_payload,
            coverage_payload=coverage_for_alerts,
        ),
    }
    return response
