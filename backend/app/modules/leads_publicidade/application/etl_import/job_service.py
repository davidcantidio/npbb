"""Async ETL import jobs backed by persisted status rows."""

from __future__ import annotations

import io
import json
import secrets
from typing import Any

from fastapi import UploadFile
from pydantic import TypeAdapter
from sqlmodel import Session

from app.db.database import engine
from app.models.lead_public_models import LeadImportEtlJob
from app.schemas.lead_import_etl import (
    ImportEtlCpfColumnRequiredResponse,
    ImportEtlHeaderRequiredResponse,
    ImportEtlJobErrorsResponse,
    ImportEtlJobRead,
    ImportEtlPreviewResponse,
    ImportEtlPreviewResponseUnion,
    ImportEtlResult,
)
from app.services.imports.file_reader import DEFAULT_IMPORT_MAX_BYTES, ImportFileError, inspect_upload

from .commit_service import commit_preview_session
from .exceptions import (
    EtlImportContractError,
    EtlImportJobConflictError,
    EtlImportJobNotFoundError,
    EtlImportValidationError,
    EtlPreviewSessionConflictError,
    EtlPreviewSessionNotFoundError,
)
from .job_repository import (
    COMMIT_RESULT_JOB_STATUSES,
    PREVIEW_RESULT_JOB_STATUSES,
    build_job_progress,
    create_job,
    get_job,
    maybe_mark_job_stale,
    set_commit_queued,
    set_commit_result,
    set_commit_running,
    set_failed_job,
    set_preview_queued,
    set_preview_result,
    set_preview_running,
)
from .preview_session_repository import read_import_session_summary
from .preview_service import create_preview_snapshot
from .rejection_reasons import aggregate_rejection_reason_counts
from .staging_repository import list_import_errors


PREVIEW_RESULT_ADAPTER = TypeAdapter(ImportEtlPreviewResponseUnion)


def _build_upload_file(filename: str, payload: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(payload))


def _serialize_preview_result(
    result,
) -> dict[str, Any]:
    if getattr(result, "status", None) == "header_required":
        return ImportEtlHeaderRequiredResponse.model_validate(
            {
                "status": result.status,
                "message": result.message,
                "max_row": result.max_row,
                "scanned_rows": result.scanned_rows,
                "required_fields": list(result.required_fields),
                "available_sheets": list(getattr(result, "available_sheets", ()) or ()),
                "active_sheet": getattr(result, "active_sheet", None),
            }
        ).model_dump(mode="json")
    if getattr(result, "status", None) == "cpf_column_required":
        return ImportEtlCpfColumnRequiredResponse.model_validate(
            {
                "status": result.status,
                "message": result.message,
                "header_row": result.header_row,
                "columns": [column.__dict__ for column in result.columns],
                "required_fields": list(result.required_fields),
                "available_sheets": list(getattr(result, "available_sheets", ()) or ()),
                "active_sheet": getattr(result, "active_sheet", None),
            }
        ).model_dump(mode="json")
    return ImportEtlPreviewResponse.model_validate(
        {
            "status": "previewed",
            "session_token": result.session_token,
            "total_rows": result.total_rows,
            "valid_rows": result.valid_rows,
            "invalid_rows": result.invalid_rows,
            "dq_report": [item.__dict__ for item in result.dq_report],
            "rejection_reason_counts": aggregate_rejection_reason_counts(result.rejected_rows),
            "sheet_name": getattr(result, "sheet_name", None),
            "available_sheets": list(getattr(result, "available_sheets", ()) or ()),
        }
    ).model_dump(mode="json")


def _serialize_commit_result(result) -> dict[str, Any]:
    return ImportEtlResult.model_validate(
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
            "dq_report": [item.__dict__ for item in result.dq_report],
            "persistence_failures": [
                {"row_number": row_number, "reason": reason}
                for row_number, reason in result.persistence_failures
            ],
        }
    ).model_dump(mode="json")


def _preview_options_from_job(job: LeadImportEtlJob) -> dict[str, Any]:
    preview_options = dict((job.options_json or {}).get("preview") or {})
    field_aliases = preview_options.get("field_aliases") or {}
    preview_options["field_aliases_json"] = (
        json.dumps(field_aliases, ensure_ascii=False) if field_aliases else None
    )
    return preview_options


def _map_job_error(exc: Exception) -> tuple[str, str]:
    if isinstance(exc, EtlPreviewSessionNotFoundError):
        return "ETL_SESSION_NOT_FOUND", "session_token invalido ou expirado"
    if isinstance(exc, EtlPreviewSessionConflictError):
        return "ETL_SESSION_CONFLICT", str(exc)
    if isinstance(exc, EtlImportValidationError):
        return "ETL_COMMIT_BLOCKED", str(exc)
    if isinstance(exc, EtlImportContractError):
        return "ETL_INVALID_INPUT", str(exc)
    if isinstance(exc, ImportFileError):
        return exc.code, exc.message
    if isinstance(exc, ValueError):
        return "ETL_INVALID_INPUT", str(exc)
    message = str(exc).strip()
    return "ETL_JOB_FAILED", message or "Falha inesperada no job ETL."


def _load_job_or_raise(session: Session, job_id: str) -> LeadImportEtlJob:
    job = maybe_mark_job_stale(session, get_job(session, job_id))
    if job is None:
        raise EtlImportJobNotFoundError(f"Job ETL nao encontrado: {job_id}")
    return job


def _ensure_job_owner(job: LeadImportEtlJob, requested_by: int | None) -> None:
    if requested_by is None:
        return
    if int(job.requested_by) != int(requested_by):
        raise EtlImportJobNotFoundError(f"Job ETL nao encontrado: {job.job_id}")


def _update_job(session: Session, job: LeadImportEtlJob) -> None:
    session.add(job)
    session.commit()


def create_preview_job(
    *,
    session: Session,
    requested_by: int,
    file: UploadFile,
    evento_id: int,
    strict: bool,
    header_row: int | None,
    field_aliases: dict[str, Any] | None,
    sheet_name: str | None,
    max_scan_rows: int | None,
) -> LeadImportEtlJob:
    filename, _ext, _size = inspect_upload(file, max_bytes=DEFAULT_IMPORT_MAX_BYTES)
    payload = file.file.read()
    job = LeadImportEtlJob(
        job_id=secrets.token_urlsafe(24),
        requested_by=requested_by,
        evento_id=evento_id,
        filename=filename,
        strict=bool(strict),
        status="queued",
        progress_json=build_job_progress(phase="preview", label="Na fila para gerar preview ETL", pct=0),
        options_json={
            "preview": {
                "header_row": header_row,
                "field_aliases": field_aliases or {},
                "sheet_name": sheet_name,
                "max_scan_rows": max_scan_rows,
            },
            "commit": {
                "force_warnings": False,
            },
        },
        file_blob=payload,
    )
    return create_job(session, job)


def queue_preview_reprocess(
    *,
    session: Session,
    job_id: str,
    requested_by: int | None,
    header_row: int | None,
    field_aliases: dict[str, Any] | None,
    sheet_name: str | None,
    max_scan_rows: int | None,
) -> LeadImportEtlJob:
    job = _load_job_or_raise(session, job_id)
    _ensure_job_owner(job, requested_by)
    if not job.file_blob:
        raise EtlImportJobConflictError("Job ETL nao pode ser reprocessado porque o arquivo original nao esta mais disponivel.")
    preview_options = {
        "header_row": header_row,
        "field_aliases": field_aliases or {},
        "sheet_name": sheet_name,
        "max_scan_rows": max_scan_rows,
    }
    options_json = dict(job.options_json or {})
    options_json["preview"] = preview_options
    job.options_json = options_json
    set_preview_queued(job)
    _update_job(session, job)
    return job


def queue_commit_job(
    *,
    session: Session,
    job_id: str,
    requested_by: int | None,
    force_warnings: bool,
) -> LeadImportEtlJob:
    job = _load_job_or_raise(session, job_id)
    _ensure_job_owner(job, requested_by)
    if job.status in {"queued", "running", "commit_queued", "committing"}:
        raise EtlImportJobConflictError("Job ETL ainda esta em processamento.")
    if job.status in {"header_required", "cpf_column_required"}:
        raise EtlImportJobConflictError("Preview ETL ainda requer parametrizacao adicional antes do commit.")
    if not job.preview_session_token:
        raise EtlImportJobConflictError("Job ETL nao possui preview persistido para commit.")
    options_json = dict(job.options_json or {})
    commit_options = dict(options_json.get("commit") or {})
    commit_options["force_warnings"] = bool(force_warnings)
    options_json["commit"] = commit_options
    job.options_json = options_json
    set_commit_queued(job)
    _update_job(session, job)
    return job


def read_job(session: Session, job_id: str, *, requested_by: int | None = None) -> ImportEtlJobRead:
    job = _load_job_or_raise(session, job_id)
    _ensure_job_owner(job, requested_by)
    progress = None
    if isinstance(job.progress_json, dict) and job.progress_json:
        progress = job.progress_json

    preview_result: ImportEtlPreviewResponseUnion | None = None
    commit_result: ImportEtlResult | None = None
    result_json = dict(job.result_json or {})
    result_status = str(result_json.get("status") or "")
    if result_json and result_status in PREVIEW_RESULT_JOB_STATUSES:
        preview_result = PREVIEW_RESULT_ADAPTER.validate_python(result_json)
    elif result_json and result_status in COMMIT_RESULT_JOB_STATUSES:
        commit_result = ImportEtlResult.model_validate(result_json)

    summary = None
    if job.preview_session_token:
        summary = read_import_session_summary(session, job.preview_session_token)

    error_payload = job.error_json or {}
    return ImportEtlJobRead.model_validate(
        {
            "job_id": job.job_id,
            "evento_id": job.evento_id,
            "filename": job.filename,
            "status": job.status,
            "strict": job.strict,
            "preview_session_token": job.preview_session_token,
            "progress": progress,
            "preview_result": preview_result,
            "commit_result": commit_result,
            "summary": summary,
            "error_code": error_payload.get("code"),
            "error_message": error_payload.get("message"),
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "completed_at": job.completed_at,
        }
    )


def read_job_errors(
    session: Session,
    *,
    job_id: str,
    requested_by: int | None = None,
    phase: str = "all",
    limit: int = 200,
    offset: int = 0,
) -> ImportEtlJobErrorsResponse:
    job = _load_job_or_raise(session, job_id)
    _ensure_job_owner(job, requested_by)
    if not job.preview_session_token:
        return ImportEtlJobErrorsResponse(job_id=job.job_id, session_token=None, total=0, items=[])
    total, items = list_import_errors(
        session,
        job.preview_session_token,
        phase=phase if phase in {"validation", "merge", "all"} else "all",
        limit=limit,
        offset=offset,
    )
    return ImportEtlJobErrorsResponse(
        job_id=job.job_id,
        session_token=job.preview_session_token,
        total=total,
        items=items,
    )


def execute_preview_job(job_id: str) -> None:
    with Session(engine) as session:
        job = get_job(session, job_id)
        if job is None:
            return
        set_preview_running(job)
        _update_job(session, job)

    try:
        with Session(engine) as session:
            job = _load_job_or_raise(session, job_id)
            if not job.file_blob:
                raise EtlImportJobConflictError("Arquivo original do job ETL nao esta mais disponivel para preview.")
            preview_options = _preview_options_from_job(job)
            result = create_preview_snapshot(
                file=_build_upload_file(job.filename, job.file_blob),
                evento_id=job.evento_id,
                strict=job.strict,
                db=session,
                max_bytes=DEFAULT_IMPORT_MAX_BYTES,
                requested_by=int(job.requested_by),
                job_id=job.job_id,
                header_row=preview_options.get("header_row"),
                field_aliases_json=preview_options.get("field_aliases_json"),
                sheet_name=preview_options.get("sheet_name"),
                max_scan_rows=preview_options.get("max_scan_rows"),
            )
            serialized = _serialize_preview_result(result)
            preview_session_token = serialized.get("session_token")
            keep_file_blob = serialized.get("status") in {"header_required", "cpf_column_required"}
            set_preview_result(
                job,
                status=str(serialized.get("status")),
                result_json=serialized,
                preview_session_token=str(preview_session_token) if preview_session_token else None,
                keep_file_blob=keep_file_blob,
            )
            _update_job(session, job)
    except Exception as exc:
        code, message = _map_job_error(exc)
        with Session(engine) as session:
            job = get_job(session, job_id)
            if job is None:
                return
            keep_file_blob = job.preview_session_token is None
            set_failed_job(
                job,
                phase="preview",
                code=code,
                message=message,
                keep_file_blob=keep_file_blob,
            )
            _update_job(session, job)


def execute_commit_job(job_id: str) -> None:
    with Session(engine) as session:
        job = get_job(session, job_id)
        if job is None:
            return
        set_commit_running(job)
        _update_job(session, job)

    try:
        with Session(engine) as session:
            job = _load_job_or_raise(session, job_id)
            if not job.preview_session_token:
                raise EtlImportJobConflictError("Job ETL nao possui preview persistido para commit.")
            commit_options = dict((job.options_json or {}).get("commit") or {})
            result = commit_preview_session(
                session_token=job.preview_session_token,
                evento_id=job.evento_id,
                force_warnings=bool(commit_options.get("force_warnings")),
                db=session,
            )
            serialized = _serialize_commit_result(result)
            set_commit_result(job, status=str(serialized.get("status")), result_json=serialized)
            _update_job(session, job)
    except Exception as exc:
        code, message = _map_job_error(exc)
        with Session(engine) as session:
            job = get_job(session, job_id)
            if job is None:
                return
            set_failed_job(
                job,
                phase="commit",
                code=code,
                message=message,
                keep_file_blob=False,
            )
            _update_job(session, job)
