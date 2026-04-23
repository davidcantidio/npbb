
"""Helpers e constantes compartilhados entre subrouters de leads."""

from __future__ import annotations

import logging
import os
import re

from fastapi import status
from sqlmodel import Session, select

from app.models.lead_batch import LeadBatch
from app.models.models import Usuario
from app.utils.http_errors import raise_http_error

logger = logging.getLogger(__name__)

ALLOWED_IMPORT_EXTENSIONS = {".csv", ".xlsx"}
BATCH_SIZE = 500
DEFAULT_IMPORT_MAX_BYTES = 50 * 1024 * 1024
DEFAULT_BATCH_SUMMARY_LIMIT = 200
DEFAULT_LOG_MEMORY = "0"
ARQUIVO_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default

MAX_IMPORT_FILE_BYTES = _get_env_int("LEADS_IMPORT_MAX_BYTES", DEFAULT_IMPORT_MAX_BYTES)
BATCH_SUMMARY_LIMIT = _get_env_int("LEADS_IMPORT_BATCH_SUMMARY_LIMIT", DEFAULT_BATCH_SUMMARY_LIMIT)
LOG_MEMORY = os.getenv("LEADS_IMPORT_LOG_MEMORY", DEFAULT_LOG_MEMORY).strip().lower() in {"1", "true", "yes"}


def _should_execute_import_jobs_inline() -> bool:
    raw = os.getenv("LEAD_IMPORT_JOB_INLINE_EXECUTION", "").strip().lower()
    return os.getenv("TESTING", "").strip().lower() == "true" or raw in {"1", "true", "yes", "on"}

def _require_current_user_id(current_user: Usuario, *, message: str = "Usuario autenticado invalido") -> int:
    user_id = getattr(current_user, "id", None)
    if not user_id:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_USER",
            message=message,
        )
    return int(user_id)

def _load_owned_batch_or_404(*, session: Session, batch_id: int, user_id: int) -> LeadBatch:
    batch = session.exec(
        select(LeadBatch).where(
            LeadBatch.id == batch_id,
            LeadBatch.enviado_por == user_id,
        )
    ).first()
    if batch is None:
        raise_http_error(
            status.HTTP_404_NOT_FOUND,
            code="BATCH_NOT_FOUND",
            message="Lote nao encontrado",
        )
    return batch
