"""Commit approved ETL preview rows into leads table."""

from __future__ import annotations

import logging
import time

from sqlmodel import Session

from app.models.models import LeadImportEtlPreviewSession
from app.observability.import_events import log_import_event, session_token_prefix

from .contracts import EtlCommitResult, PreviewStatus
from .exceptions import EtlImportValidationError, EtlPreviewSessionConflictError
from .persistence import persist_lead_batch
from .preview_session_repository import get_commit_result, get_snapshot, mark_committed
from .staging_repository import (
    count_rows_by_merge_status,
    list_merge_failures,
    load_rows_for_merge,
    mark_merge_failures,
    mark_merge_success,
    mark_superseded_duplicates,
)

logger = logging.getLogger(__name__)


def commit_preview_session(
    *,
    session_token: str,
    evento_id: int,
    force_warnings: bool,
    db: Session,
) -> EtlCommitResult:
    started_at = time.perf_counter()
    committed = get_commit_result(db, session_token)
    if committed is not None:
        log_import_event(
            logger,
            "etl.commit.idempotent_read",
            outcome="cached",
            session_token_prefix=session_token_prefix(session_token),
            evento_id=evento_id,
            status=committed.status,
        )
        return committed

    snapshot = get_snapshot(db, session_token)
    if snapshot.evento_id != evento_id:
        raise EtlPreviewSessionConflictError("session_token nao pertence ao evento informado.")
    if snapshot.status == "committed":
        raise EtlPreviewSessionConflictError("session_token ja foi consumido.")

    if snapshot.strict and snapshot.has_validation_errors:
        raise EtlImportValidationError("strict=true bloqueia commit quando ha erros de validacao no preview.")
    if snapshot.has_warnings and not force_warnings:
        raise EtlImportValidationError("Commit ETL exige confirmacao explicita para warnings.")

    log_import_event(
        logger,
        "etl.commit.start",
        evento_id=evento_id,
        session_token_prefix=session_token_prefix(session_token),
        valid_rows=snapshot.valid_rows,
    )
    try:
        mark_superseded_duplicates(db, session_token, auto_commit=False)
        batch = load_rows_for_merge(db, session_token)
        batch_result = persist_lead_batch(
            db,
            batch,
            canonical_evento_id=snapshot.evento_id,
            auto_commit=False,
        )
        if batch_result.applied_rows:
            mark_merge_success(
                db,
                session_token,
                applied_rows=[
                    (row.row_index, row.action, row.lead_id)
                    for row in batch_result.applied_rows
                ],
                auto_commit=False,
            )
        if batch_result.failed_rows:
            mark_merge_failures(
                db,
                session_token,
                failed_rows=[
                    (row.row_index, row.reason)
                    for row in batch_result.failed_rows
                ],
                auto_commit=False,
            )

        preview_entity = db.get(LeadImportEtlPreviewSession, session_token)
        created_rows = count_rows_by_merge_status(db, session_token, "created")
        updated_rows = count_rows_by_merge_status(db, session_token, "updated")
        duplicate_rows = count_rows_by_merge_status(db, session_token, "skipped")
        persistence_failures = list_merge_failures(db, session_token)
        error_rows = len(persistence_failures)
        has_errors = error_rows > 0
        outcome_status: PreviewStatus = "partial_failure" if has_errors else "committed"
        result = EtlCommitResult(
            session_token=session_token,
            total_rows=snapshot.total_rows,
            valid_rows=snapshot.valid_rows,
            invalid_rows=snapshot.invalid_rows,
            created=created_rows,
            updated=updated_rows,
            skipped=duplicate_rows,
            errors=error_rows,
            strict=bool(snapshot.strict),
            status=outcome_status,
            duplicate_rows=duplicate_rows,
            staged_rows=int(preview_entity.staged_rows if preview_entity is not None else 0),
            ingestion_strategy=preview_entity.ingestion_strategy if preview_entity is not None else None,
            merge_strategy="backend_staging_merge",
            dq_report=snapshot.dq_report,
            persistence_failures=persistence_failures,
        )
        mark_committed(db, result, auto_commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
    log_import_event(
        logger,
        "etl.commit.completed",
        outcome=result.status,
        evento_id=evento_id,
        session_token_prefix=session_token_prefix(session_token),
        created=result.created,
        updated=result.updated,
        skipped=result.skipped,
        errors=result.errors,
        duration_ms=round((time.perf_counter() - started_at) * 1000),
    )
    return result
