"""Create ETL preview snapshots."""

from __future__ import annotations

import secrets

from sqlmodel import Session

from app.models.models import Evento

from .contracts import EtlPreviewSnapshot
from .dq_report_mapper import map_check_report
from .exceptions import EtlImportContractError
from .extract import compute_file_fingerprint, extract_xlsx_rows, read_upload_bytes
from .preview_session_repository import create_snapshot
from .transform_validate import run_preview_validation


def create_preview_snapshot(
    *,
    file,
    evento_id: int,
    strict: bool,
    db: Session,
    max_bytes: int,
) -> EtlPreviewSnapshot:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise EtlImportContractError(f"Evento inexistente: {evento_id}")

    filename, ext, payload = read_upload_bytes(file, max_bytes=max_bytes)
    if ext != ".xlsx":
        raise EtlImportContractError("Fluxo ETL suporta apenas arquivos .xlsx nesta fase.")

    extracted_rows, _metadata = extract_xlsx_rows(payload)
    state, report = run_preview_validation(extracted_rows, evento_nome=str(evento.nome))
    dq_report = map_check_report(report)
    file_fingerprint = compute_file_fingerprint(filename, payload)
    snapshot = EtlPreviewSnapshot(
        session_token=secrets.token_urlsafe(24),
        filename=filename,
        evento_id=evento_id,
        evento_nome=str(evento.nome),
        strict=bool(strict),
        total_rows=len(extracted_rows),
        valid_rows=len(state.approved_rows),
        invalid_rows=len(state.rejected_rows),
        approved_rows=state.approved_rows,
        rejected_rows=state.rejected_rows,
        dq_report=dq_report,
        status="previewed",
        idempotency_key=f"lead-etl-preview:{evento_id}:{file_fingerprint}:{int(bool(strict))}",
        has_validation_errors=any(item.severity == "error" for item in dq_report),
        has_warnings=any(item.severity == "warning" for item in dq_report),
    )
    return create_snapshot(db, snapshot)
