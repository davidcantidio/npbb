"""Persistence helpers for ETL import jobs."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session

from app.models.lead_public_models import LeadImportEtlJob


TRANSIENT_JOB_STATUSES = {"queued", "running", "commit_queued", "committing"}
PREVIEW_RESULT_JOB_STATUSES = {"header_required", "cpf_column_required", "previewed"}
COMMIT_RESULT_JOB_STATUSES = {"committed", "partial_failure"}
TERMINAL_JOB_STATUSES = PREVIEW_RESULT_JOB_STATUSES | COMMIT_RESULT_JOB_STATUSES | {"failed"}


def now_job_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def etl_job_stale_after_seconds() -> int:
    raw = os.getenv("LEAD_IMPORT_ETL_JOB_STALE_SECONDS", "1800").strip()
    try:
        return max(int(raw), 60)
    except ValueError:
        return 1800


def build_job_progress(*, phase: str, label: str, pct: int | None) -> dict[str, Any]:
    return {
        "phase": phase,
        "label": label,
        "pct": pct,
        "updated_at": now_job_timestamp().isoformat(),
    }


def _coerce_job_timestamp(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def create_job(session: Session, job: LeadImportEtlJob) -> LeadImportEtlJob:
    session.add(job)
    session.commit()
    return job


def get_job(session: Session, job_id: str) -> LeadImportEtlJob | None:
    return session.get(LeadImportEtlJob, job_id)


def is_terminal_job_status(status: str) -> bool:
    return status in TERMINAL_JOB_STATUSES


def maybe_mark_job_stale(session: Session, job: LeadImportEtlJob | None) -> LeadImportEtlJob | None:
    if job is None or job.status not in TRANSIENT_JOB_STATUSES:
        return job
    updated_at = _coerce_job_timestamp(job.updated_at)
    if updated_at is None:
        return job
    if now_job_timestamp() - updated_at <= timedelta(seconds=etl_job_stale_after_seconds()):
        return job
    stale_phase = "commit" if job.status in {"commit_queued", "committing"} else "preview"
    job.status = "failed"
    job.progress_json = build_job_progress(
        phase=stale_phase,
        label="Job ETL expirou sem finalizar",
        pct=None,
    )
    job.error_json = {
        "code": "ETL_JOB_STALE",
        "message": "Processamento ETL expirou sem finalizar. Reenvie ou reprocesse o job.",
    }
    job.file_blob = None
    job.completed_at = now_job_timestamp()
    session.add(job)
    session.commit()
    return job


def set_preview_queued(job: LeadImportEtlJob) -> None:
    job.status = "queued"
    job.result_json = None
    job.error_json = None
    job.completed_at = None
    job.progress_json = build_job_progress(phase="preview", label="Na fila para gerar preview ETL", pct=0)


def set_preview_running(job: LeadImportEtlJob) -> None:
    job.status = "running"
    job.error_json = None
    job.progress_json = build_job_progress(phase="preview", label="Gerando preview ETL no backend", pct=25)


def set_preview_result(
    job: LeadImportEtlJob,
    *,
    status: str,
    result_json: dict[str, Any],
    preview_session_token: str | None,
    keep_file_blob: bool,
) -> None:
    job.status = status
    job.result_json = result_json
    job.error_json = None
    job.preview_session_token = preview_session_token
    job.file_blob = job.file_blob if keep_file_blob else None
    job.completed_at = now_job_timestamp()
    job.progress_json = build_job_progress(phase="preview", label="Preview ETL concluido", pct=100)


def set_commit_queued(job: LeadImportEtlJob) -> None:
    job.status = "commit_queued"
    job.error_json = None
    job.completed_at = None
    job.progress_json = build_job_progress(phase="commit", label="Na fila para aplicar commit ETL", pct=0)


def set_commit_running(job: LeadImportEtlJob) -> None:
    job.status = "committing"
    job.error_json = None
    job.progress_json = build_job_progress(phase="commit", label="Aplicando merge ETL a partir do staging", pct=35)


def set_commit_result(job: LeadImportEtlJob, *, status: str, result_json: dict[str, Any]) -> None:
    job.status = status
    job.result_json = result_json
    job.error_json = None
    job.file_blob = None
    job.completed_at = now_job_timestamp()
    job.progress_json = build_job_progress(phase="commit", label="Commit ETL concluido", pct=100)


def set_failed_job(
    job: LeadImportEtlJob,
    *,
    phase: str,
    code: str,
    message: str,
    keep_file_blob: bool,
) -> None:
    job.status = "failed"
    job.error_json = {"code": code, "message": message}
    job.file_blob = job.file_blob if keep_file_blob else None
    job.completed_at = now_job_timestamp()
    job.progress_json = build_job_progress(phase=phase, label=message, pct=None)
