"""Commit approved ETL preview rows into leads table."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session

from core.leads_etl.models import backend_payload_to_lead_row

from .contracts import EtlCommitResult
from .exceptions import EtlImportValidationError, EtlPreviewSessionConflictError
from .persistence import build_dedupe_key, persist_lead_batch
from .preview_session_repository import get_commit_result, get_snapshot, mark_committed


def commit_preview_session(
    *,
    session_token: str,
    evento_id: int,
    force_warnings: bool,
    db: Session,
) -> EtlCommitResult:
    committed = get_commit_result(db, session_token)
    if committed is not None:
        return committed

    snapshot = get_snapshot(db, session_token)
    if snapshot.evento_id != evento_id:
        raise EtlPreviewSessionConflictError("session_token nao pertence ao evento informado.")
    if snapshot.status == "committed":
        raise EtlPreviewSessionConflictError("session_token ja foi consumido.")

    if snapshot.has_validation_errors:
        raise EtlImportValidationError("Commit ETL bloqueado por erros de validacao no preview.")
    if snapshot.has_warnings and not force_warnings:
        raise EtlImportValidationError("Commit ETL exige confirmacao explicita para warnings.")

    batch: list[tuple[dict[str, object], int] | None] = []
    key_to_index: dict[str, int] = {}
    for row in snapshot.approved_rows:
        payload = backend_payload_to_lead_row(dict(row.payload)).model_dump(mode="python")
        if isinstance(payload.get("data_compra"), datetime):
            payload["data_compra_data"] = payload["data_compra"].date()
            payload["data_compra_hora"] = payload["data_compra"].time()
        key = build_dedupe_key(payload)
        if key:
            previous_index = key_to_index.get(key)
            if previous_index is not None:
                batch[previous_index] = None
            key_to_index[key] = len(batch)
        batch.append((payload, row.row_number))

    created, updated, skipped, has_errors = persist_lead_batch(db, batch)
    result = EtlCommitResult(
        session_token=session_token,
        total_rows=snapshot.total_rows,
        valid_rows=snapshot.valid_rows,
        invalid_rows=snapshot.invalid_rows,
        created=created,
        updated=updated,
        skipped=skipped,
        errors=skipped if has_errors else 0,
        strict=bool(snapshot.strict),
        status="committed",
        dq_report=snapshot.dq_report,
    )
    return mark_committed(db, result)
