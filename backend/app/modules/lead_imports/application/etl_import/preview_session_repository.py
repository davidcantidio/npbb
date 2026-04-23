"""Persistence for ETL preview snapshots."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.models import LeadImportEtlPreviewSession

from .contracts import EtlCommitResult, EtlPreviewDQItem, EtlPreviewRow, EtlPreviewSnapshot
from .dq_report_policy import compute_has_warnings
from .exceptions import EtlPreviewSessionNotFoundError
from .rejection_reasons import record_etl_preview_rejection_metrics


DEFAULT_INLINE_PREVIEW_ROW_LIMIT = 1000


def inline_preview_row_limit() -> int:
    raw = os.getenv("LEAD_IMPORT_ETL_INLINE_PREVIEW_ROW_LIMIT", "").strip()
    if not raw:
        return DEFAULT_INLINE_PREVIEW_ROW_LIMIT
    try:
        return max(int(raw), 0)
    except ValueError:
        return DEFAULT_INLINE_PREVIEW_ROW_LIMIT


def _serialize_preview_context(snapshot: EtlPreviewSnapshot) -> str | None:
    if snapshot.sheet_name is None and not snapshot.available_sheets:
        return None
    return json.dumps(
        {"sheet_name": snapshot.sheet_name, "available_sheets": list(snapshot.available_sheets)},
        ensure_ascii=False,
    )


def _deserialize_preview_context(raw: str | None) -> tuple[str | None, tuple[str, ...]]:
    if not raw or not raw.strip():
        return None, ()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None, ()
    if not isinstance(payload, dict):
        return None, ()
    sheet = payload.get("sheet_name")
    sheet_name = str(sheet) if sheet is not None else None
    raw_sheets = payload.get("available_sheets") or []
    if not isinstance(raw_sheets, list):
        return sheet_name, ()
    return sheet_name, tuple(str(s) for s in raw_sheets if s is not None)


def _serialize_rows(rows: tuple[EtlPreviewRow, ...]) -> str:
    return json.dumps(
        [
            {"row_number": row.row_number, "payload": row.payload, "errors": row.errors}
            for row in rows
        ],
        ensure_ascii=False,
        default=str,
    )


def _deserialize_rows(raw: str) -> tuple[EtlPreviewRow, ...]:
    payload = json.loads(raw or "[]")
    return tuple(
        EtlPreviewRow(
            row_number=int(item["row_number"]),
            payload=dict(item["payload"]),
            errors=list(item.get("errors") or []),
        )
        for item in payload
    )


def _serialize_dq(items: tuple[EtlPreviewDQItem, ...]) -> str:
    return json.dumps(
        [
            {
                "check_name": item.check_name,
                "severity": item.severity,
                "affected_rows": item.affected_rows,
                "sample": item.sample,
                "check_id": item.check_id,
                "message": item.message,
            }
            for item in items
        ],
        ensure_ascii=False,
    )


def _deserialize_dq(raw: str) -> tuple[EtlPreviewDQItem, ...]:
    payload = json.loads(raw or "[]")
    return tuple(
        EtlPreviewDQItem(
            check_name=item["check_name"],
            severity=item["severity"],
            affected_rows=int(item["affected_rows"]),
            sample=list(item.get("sample") or []),
            check_id=item.get("check_id"),
            message=item.get("message"),
        )
        for item in payload
    )


def create_snapshot(session: Session, snapshot: EtlPreviewSnapshot) -> EtlPreviewSnapshot:
    existing = session.get(LeadImportEtlPreviewSession, snapshot.session_token)
    if existing is None:
        existing = session.exec(
            select(LeadImportEtlPreviewSession).where(
                LeadImportEtlPreviewSession.idempotency_key == snapshot.idempotency_key
            )
        ).first()
    if existing is not None:
        return get_snapshot(session, existing.session_token)

    record_etl_preview_rejection_metrics(snapshot.rejected_rows)
    keep_inline_rows = snapshot.total_rows <= inline_preview_row_limit()
    entity = LeadImportEtlPreviewSession(
        session_token=snapshot.session_token,
        idempotency_key=snapshot.idempotency_key,
        evento_id=snapshot.evento_id,
        evento_nome=snapshot.evento_nome,
        filename=snapshot.filename,
        strict=snapshot.strict,
        status=snapshot.status,
        total_rows=snapshot.total_rows,
        valid_rows=snapshot.valid_rows,
        invalid_rows=snapshot.invalid_rows,
        has_validation_errors=snapshot.has_validation_errors,
        approved_rows_json=_serialize_rows(snapshot.approved_rows if keep_inline_rows else ()),
        rejected_rows_json=_serialize_rows(snapshot.rejected_rows if keep_inline_rows else ()),
        dq_report_json=_serialize_dq(snapshot.dq_report),
        preview_context_json=_serialize_preview_context(snapshot),
    )
    session.add(entity)
    session.commit()
    return snapshot


def update_import_session_after_staging(
    session: Session,
    *,
    session_token: str,
    requested_by: int | None,
    source_file_size_bytes: int,
    ingestion_strategy: str,
    staged_rows: int,
    duplicate_rows: int,
) -> None:
    entity = session.get(LeadImportEtlPreviewSession, session_token)
    if entity is None:
        raise EtlPreviewSessionNotFoundError(f"Preview session not found: {session_token}")
    if requested_by is not None:
        entity.requested_by = requested_by
    entity.source_file_size_bytes = int(source_file_size_bytes)
    entity.ingestion_strategy = ingestion_strategy
    entity.staged_rows = int(staged_rows)
    entity.duplicate_rows = int(duplicate_rows)
    session.add(entity)
    session.commit()


def get_snapshot(session: Session, session_token: str) -> EtlPreviewSnapshot:
    entity = session.get(LeadImportEtlPreviewSession, session_token)
    if entity is None:
        raise EtlPreviewSessionNotFoundError(f"Preview session not found: {session_token}")
    dq_report = _deserialize_dq(entity.dq_report_json)
    sheet_name, available_sheets = _deserialize_preview_context(getattr(entity, "preview_context_json", None))
    return EtlPreviewSnapshot(
        session_token=entity.session_token,
        filename=entity.filename,
        evento_id=entity.evento_id,
        evento_nome=entity.evento_nome,
        strict=entity.strict,
        total_rows=entity.total_rows,
        valid_rows=entity.valid_rows,
        invalid_rows=entity.invalid_rows,
        approved_rows=_deserialize_rows(entity.approved_rows_json),
        rejected_rows=_deserialize_rows(entity.rejected_rows_json),
        dq_report=dq_report,
        status=entity.status,  # type: ignore[arg-type]
        idempotency_key=entity.idempotency_key,
        has_validation_errors=entity.has_validation_errors,
        has_warnings=compute_has_warnings(dq_report),
        sheet_name=sheet_name,
        available_sheets=available_sheets,
    )


def read_import_session_summary(session: Session, session_token: str) -> dict[str, object]:
    entity = session.get(LeadImportEtlPreviewSession, session_token)
    if entity is None:
        raise EtlPreviewSessionNotFoundError(f"Preview session not found: {session_token}")
    return {
        "session_token": entity.session_token,
        "total_rows": int(entity.total_rows),
        "staged_rows": int(entity.staged_rows),
        "valid_rows": int(entity.valid_rows),
        "invalid_rows": int(entity.invalid_rows),
        "duplicate_rows": int(entity.duplicate_rows),
        "created_rows": int(entity.created_rows),
        "updated_rows": int(entity.updated_rows),
        "skipped_rows": int(entity.skipped_rows),
        "error_rows": int(entity.error_rows),
        "ingestion_strategy": entity.ingestion_strategy,
        "merge_strategy": "backend_staging_merge",
        "source_file_size_bytes": entity.source_file_size_bytes,
        "committed_at": entity.committed_at,
    }


def _persistence_failures_from_payload(payload: dict[str, object]) -> tuple[tuple[int, str], ...]:
    raw = payload.get("persistence_failures") or []
    if not isinstance(raw, list):
        return ()
    out: list[tuple[int, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        out.append((int(item["row_number"]), str(item["reason"])))
    return tuple(out)


def mark_committed(
    session: Session,
    result: EtlCommitResult,
    *,
    auto_commit: bool = True,
) -> EtlCommitResult:
    entity = session.get(LeadImportEtlPreviewSession, result.session_token)
    if entity is None:
        raise EtlPreviewSessionNotFoundError(f"Preview session not found: {result.session_token}")
    entity.status = result.status
    entity.committed_at = datetime.now(timezone.utc)
    entity.created_rows = int(result.created)
    entity.updated_rows = int(result.updated)
    entity.skipped_rows = int(result.skipped)
    entity.error_rows = int(result.errors)
    entity.commit_result_json = json.dumps(
        {
            "session_token": result.session_token,
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": result.invalid_rows,
            "created": result.created,
            "updated": result.updated,
            "skipped": result.skipped,
            "errors": result.errors,
            "strict": result.strict,
            "status": result.status,
            "duplicate_rows": result.duplicate_rows,
            "staged_rows": result.staged_rows,
            "ingestion_strategy": result.ingestion_strategy,
            "merge_strategy": result.merge_strategy,
            "persistence_failures": [
                {"row_number": row_number, "reason": reason}
                for row_number, reason in result.persistence_failures
            ],
        },
        ensure_ascii=False,
    )
    session.add(entity)
    if auto_commit:
        session.commit()
    return result


def get_commit_result(session: Session, session_token: str) -> EtlCommitResult | None:
    """Idempotency cache for a fully successful commit only (`status == committed`)."""
    entity = session.get(LeadImportEtlPreviewSession, session_token)
    if entity is None or not entity.commit_result_json:
        return None
    payload = json.loads(entity.commit_result_json)
    if payload.get("status") != "committed":
        return None
    return EtlCommitResult(
        session_token=payload["session_token"],
        total_rows=int(payload["total_rows"]),
        valid_rows=int(payload["valid_rows"]),
        invalid_rows=int(payload["invalid_rows"]),
        created=int(payload["created"]),
        updated=int(payload["updated"]),
        skipped=int(payload["skipped"]),
        errors=int(payload["errors"]),
        strict=bool(payload["strict"]),
        status=payload["status"],
        duplicate_rows=int(payload.get("duplicate_rows") or 0),
        staged_rows=int(payload.get("staged_rows") or 0),
        ingestion_strategy=str(payload.get("ingestion_strategy") or "") or None,
        merge_strategy=str(payload.get("merge_strategy") or "") or None,
        dq_report=_deserialize_dq(entity.dq_report_json),
        persistence_failures=_persistence_failures_from_payload(payload),
    )
