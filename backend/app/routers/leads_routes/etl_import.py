
"""Rotas do fluxo ETL de importacao de leads."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlmodel import Session

from app.core.auth import get_current_user
from app.db.database import get_session
from app.models.models import Usuario
from app.modules.lead_imports.application.etl_import.exceptions import (
    EtlImportContractError,
    EtlImportJobConflictError,
    EtlImportJobNotFoundError,
    EtlImportValidationError,
    EtlPreviewSessionConflictError,
    EtlPreviewSessionNotFoundError,
)
from app.modules.lead_imports.application.etl_import.extract import ETL_MAX_SCAN_ROWS_CAP
from app.modules.lead_imports.application.etl_import.job_service import (
    create_preview_job,
    execute_commit_job,
    execute_preview_job,
    queue_commit_job,
    queue_preview_reprocess,
    read_job,
    read_job_errors,
)
from app.modules.lead_imports.application.etl_import.rejection_reasons import aggregate_rejection_reason_counts
from app.modules.lead_imports.application.leads_import_etl_usecases import (
    commit_leads_with_etl,
    import_leads_with_etl,
)
from app.schemas.lead_import_etl import (
    ImportEtlCommitRequest,
    ImportEtlCpfColumnRequiredResponse,
    ImportEtlHeaderRequiredResponse,
    ImportEtlJobCommitRequest,
    ImportEtlJobErrorsResponse,
    ImportEtlJobQueuedResponse,
    ImportEtlJobRead,
    ImportEtlJobReprocessRequest,
    ImportEtlPreviewResponse,
    ImportEtlPreviewResponseUnion,
    ImportEtlResult,
)
from app.services.imports.file_reader import ImportFileError
from app.utils.http_errors import raise_http_error

from ._shared import _should_execute_import_jobs_inline

router = APIRouter()


def _map_etl_import_error(exc: Exception) -> None:
    if isinstance(exc, EtlImportJobNotFoundError):
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ETL_JOB_NOT_FOUND",
            message="job_id invalido ou expirado",
            field="job_id",
        )
    if isinstance(exc, EtlImportJobConflictError):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ETL_JOB_CONFLICT",
            message=str(exc),
            field="job_id",
        )
    if isinstance(exc, EtlPreviewSessionNotFoundError):
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="ETL_SESSION_NOT_FOUND",
            message="session_token invalido ou expirado",
            field="session_token",
        )
    if isinstance(exc, EtlPreviewSessionConflictError):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ETL_SESSION_CONFLICT",
            message=str(exc),
            field="session_token",
        )
    if isinstance(exc, EtlImportValidationError):
        raise_http_error(
            status.HTTP_409_CONFLICT,
            code="ETL_COMMIT_BLOCKED",
            message=str(exc),
        )
    if isinstance(exc, EtlImportContractError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="ETL_INVALID_INPUT",
            message=str(exc),
        )
    if isinstance(exc, ImportFileError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code=exc.code,
            message=exc.message,
            field=exc.field,
            extra=exc.extra,
        )
    if isinstance(exc, ValueError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="ETL_INVALID_INPUT",
            message=str(exc),
        )
    raise exc


def _serialize_etl_preview_response(
    result,
) -> ImportEtlPreviewResponse | ImportEtlHeaderRequiredResponse | ImportEtlCpfColumnRequiredResponse:
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
        )
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
        )
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
    )


def _serialize_etl_commit_response(result) -> ImportEtlResult:
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
    )


@router.post("/import/etl/jobs", response_model=ImportEtlJobQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/import/etl/jobs/", response_model=ImportEtlJobQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
def criar_job_import_etl(
    file: UploadFile = File(...),
    evento_id: int = Form(...),
    strict: bool = Form(False),
    header_row: int | None = Form(None),
    field_aliases_json: str | None = Form(None),
    sheet_name: str | None = Form(None),
    max_scan_rows: int | None = Form(None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    if max_scan_rows is not None and (max_scan_rows < 1 or max_scan_rows > ETL_MAX_SCAN_ROWS_CAP):
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="ETL_INVALID_INPUT",
            message=f"max_scan_rows deve estar entre 1 e {ETL_MAX_SCAN_ROWS_CAP}.",
            field="max_scan_rows",
        )
    try:
        field_aliases = json.loads(field_aliases_json) if field_aliases_json and field_aliases_json.strip() else {}
        if field_aliases and not isinstance(field_aliases, dict):
            raise EtlImportContractError("field_aliases_json deve ser um objeto JSON.")
        job = create_preview_job(
            session=session,
            requested_by=int(current_user.id),
            file=file,
            evento_id=evento_id,
            strict=strict,
            header_row=header_row,
            field_aliases=field_aliases,
            sheet_name=sheet_name,
            max_scan_rows=max_scan_rows,
        )
        if _should_execute_import_jobs_inline():
            execute_preview_job(job.job_id)
    except Exception as exc:
        _map_etl_import_error(exc)
    return ImportEtlJobQueuedResponse(job_id=job.job_id, status="queued")


@router.get("/import/etl/jobs/{job_id}", response_model=ImportEtlJobRead)
@router.get("/import/etl/jobs/{job_id}/", response_model=ImportEtlJobRead)
def obter_job_import_etl(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        return read_job(session, job_id, requested_by=int(current_user.id))
    except Exception as exc:
        _map_etl_import_error(exc)


@router.get("/import/etl/jobs/{job_id}/errors", response_model=ImportEtlJobErrorsResponse)
@router.get("/import/etl/jobs/{job_id}/errors/", response_model=ImportEtlJobErrorsResponse)
def obter_erros_job_import_etl(
    job_id: str,
    phase: str = Query("all"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        return read_job_errors(
            session,
            job_id=job_id,
            requested_by=int(current_user.id),
            phase=phase,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        _map_etl_import_error(exc)


@router.post(
    "/import/etl/jobs/{job_id}/reprocess-preview",
    response_model=ImportEtlJobQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/import/etl/jobs/{job_id}/reprocess-preview/",
    response_model=ImportEtlJobQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def reprocessar_job_preview_import_etl(
    job_id: str,
    payload: ImportEtlJobReprocessRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    if payload.max_scan_rows is not None and (
        payload.max_scan_rows < 1 or payload.max_scan_rows > ETL_MAX_SCAN_ROWS_CAP
    ):
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="ETL_INVALID_INPUT",
            message=f"max_scan_rows deve estar entre 1 e {ETL_MAX_SCAN_ROWS_CAP}.",
            field="max_scan_rows",
        )
    try:
        job = queue_preview_reprocess(
            session=session,
            job_id=job_id,
            requested_by=int(current_user.id),
            header_row=payload.header_row,
            field_aliases={key: value.model_dump(exclude_none=True) for key, value in payload.field_aliases.items()},
            sheet_name=payload.sheet_name,
            max_scan_rows=payload.max_scan_rows,
        )
        if _should_execute_import_jobs_inline():
            execute_preview_job(job.job_id)
    except Exception as exc:
        _map_etl_import_error(exc)
    return ImportEtlJobQueuedResponse(job_id=job.job_id, status="queued")


@router.post(
    "/import/etl/jobs/{job_id}/commit",
    response_model=ImportEtlJobQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@router.post(
    "/import/etl/jobs/{job_id}/commit/",
    response_model=ImportEtlJobQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def confirmar_job_import_etl(
    job_id: str,
    payload: ImportEtlJobCommitRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        job = queue_commit_job(
            session=session,
            job_id=job_id,
            requested_by=int(current_user.id),
            force_warnings=payload.force_warnings,
        )
        if _should_execute_import_jobs_inline():
            execute_commit_job(job.job_id)
    except Exception as exc:
        _map_etl_import_error(exc)
    return ImportEtlJobQueuedResponse(job_id=job.job_id, status="commit_queued")


@router.post("/import/etl/preview", response_model=ImportEtlPreviewResponseUnion)
@router.post("/import/etl/preview/", response_model=ImportEtlPreviewResponseUnion)
async def preview_import_etl(
    file: UploadFile = File(...),
    evento_id: int = Form(...),
    strict: bool = Form(False),
    header_row: int | None = Form(None),
    field_aliases_json: str | None = Form(None),
    sheet_name: str | None = Form(None),
    max_scan_rows: int | None = Form(None),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    if max_scan_rows is not None and (max_scan_rows < 1 or max_scan_rows > ETL_MAX_SCAN_ROWS_CAP):
        raise_http_error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="ETL_INVALID_INPUT",
            message=f"max_scan_rows deve estar entre 1 e {ETL_MAX_SCAN_ROWS_CAP}.",
            field="max_scan_rows",
        )
    try:
        result = await import_leads_with_etl(
            file=file,
            evento_id=evento_id,
            db=session,
            strict=strict,
            requested_by=int(current_user.id),
            header_row=header_row,
            field_aliases_json=field_aliases_json,
            sheet_name=sheet_name,
            max_scan_rows=max_scan_rows,
        )
    except Exception as exc:
        _map_etl_import_error(exc)
    return _serialize_etl_preview_response(result)


@router.post("/import/etl/commit", response_model=ImportEtlResult)
@router.post("/import/etl/commit/", response_model=ImportEtlResult)
async def commit_import_etl(
    payload: ImportEtlCommitRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    _ = current_user
    try:
        result = await commit_leads_with_etl(
            session_token=payload.session_token,
            evento_id=payload.evento_id,
            db=session,
            force_warnings=payload.force_warnings,
        )
    except Exception as exc:
        _map_etl_import_error(exc)
    return _serialize_etl_commit_response(result)
