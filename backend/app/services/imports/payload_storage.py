"""Persist and read import payloads from object storage with legacy blob fallback."""

from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx

from app.models.lead_batch import LeadBatch
from app.models.lead_public_models import LeadImportEtlJob


class PayloadStorageError(RuntimeError):
    """Base error for storage failures."""


class PayloadNotFoundError(PayloadStorageError):
    """Raised when the requested object does not exist."""


@dataclass(frozen=True)
class StoredPayload:
    bucket: str
    key: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _storage_backend() -> str:
    return (os.getenv("OBJECT_STORAGE_BACKEND", "local").strip() or "local").lower()


def _storage_bucket() -> str:
    return os.getenv("OBJECT_STORAGE_BUCKET", "lead-imports").strip() or "lead-imports"


def _storage_local_root() -> Path:
    raw = os.getenv("OBJECT_STORAGE_LOCAL_ROOT", "").strip()
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parents[3] / "var" / "object_storage"


def _guess_content_type(filename: str | None, explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    guessed, _ = mimetypes.guess_type(filename or "")
    return guessed or "application/octet-stream"


def _supabase_base_url() -> str:
    raw = (
        os.getenv("SUPABASE_STORAGE_URL")
        or os.getenv("SUPABASE_URL")
        or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        or ""
    ).strip().rstrip("/")
    if not raw:
        raise PayloadStorageError(
            "SUPABASE_STORAGE_URL/SUPABASE_URL obrigatoria para OBJECT_STORAGE_BACKEND=supabase."
        )
    return raw


def _supabase_service_role_key() -> str:
    raw = (
        os.getenv("SUPABASE_STORAGE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    ).strip()
    if not raw:
        raise PayloadStorageError(
            "SUPABASE_STORAGE_SERVICE_ROLE_KEY/SUPABASE_SERVICE_ROLE_KEY obrigatoria para OBJECT_STORAGE_BACKEND=supabase."
        )
    return raw


def _build_key(*, prefix: str, stable_id: str, filename: str, sha256: str | None = None) -> str:
    safe_name = Path(filename or "arquivo").name or "arquivo"
    key_parts = [prefix.strip("/"), stable_id.strip("/")]
    if sha256:
        key_parts.append(sha256)
    key_parts.append(f"{uuid4().hex}-{safe_name}")
    return "/".join(part for part in key_parts if part)


def _store_local(*, bucket: str, key: str, payload: bytes, content_type: str) -> StoredPayload:
    root = _storage_local_root() / bucket
    path = root / Path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return StoredPayload(
        bucket=bucket,
        key=key,
        content_type=content_type,
        size_bytes=len(payload),
        uploaded_at=_now_utc(),
    )


def _read_local(*, bucket: str, key: str) -> bytes:
    path = _storage_local_root() / bucket / Path(key)
    if not path.exists():
        raise PayloadNotFoundError(f"Objeto nao encontrado no storage local: {bucket}/{key}")
    return path.read_bytes()


def _store_supabase(*, bucket: str, key: str, payload: bytes, content_type: str) -> StoredPayload:
    base_url = _supabase_base_url()
    service_role_key = _supabase_service_role_key()
    url = f"{base_url}/storage/v1/object/{bucket}/{key}"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "x-upsert": "true",
        "Content-Type": content_type,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, content=payload)
    if response.status_code >= 400:
        raise PayloadStorageError(
            f"Falha ao gravar objeto no Supabase Storage ({response.status_code}): {response.text[:240]}"
        )
    return StoredPayload(
        bucket=bucket,
        key=key,
        content_type=content_type,
        size_bytes=len(payload),
        uploaded_at=_now_utc(),
    )


def _read_supabase(*, bucket: str, key: str) -> bytes:
    base_url = _supabase_base_url()
    service_role_key = _supabase_service_role_key()
    url = f"{base_url}/storage/v1/object/{bucket}/{key}"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, headers=headers)
    if response.status_code == 404:
        raise PayloadNotFoundError(f"Objeto nao encontrado no Supabase Storage: {bucket}/{key}")
    if response.status_code >= 400:
        raise PayloadStorageError(
            f"Falha ao ler objeto do Supabase Storage ({response.status_code}): {response.text[:240]}"
        )
    return bytes(response.content)


def _store_bytes(*, bucket: str, key: str, payload: bytes, content_type: str) -> StoredPayload:
    backend = _storage_backend()
    if backend == "supabase":
        return _store_supabase(bucket=bucket, key=key, payload=payload, content_type=content_type)
    return _store_local(bucket=bucket, key=key, payload=payload, content_type=content_type)


def _read_bytes(*, bucket: str, key: str) -> bytes:
    backend = _storage_backend()
    if backend == "supabase":
        return _read_supabase(bucket=bucket, key=key)
    return _read_local(bucket=bucket, key=key)


def persist_batch_payload(
    batch: LeadBatch,
    payload: bytes,
    *,
    content_type: str | None = None,
) -> StoredPayload:
    bucket = _storage_bucket()
    key = _build_key(
        prefix="lead-batches",
        stable_id=str(int(batch.enviado_por)),
        filename=batch.nome_arquivo_original,
        sha256=batch.arquivo_sha256,
    )
    stored = _store_bytes(
        bucket=bucket,
        key=key,
        payload=payload,
        content_type=_guess_content_type(batch.nome_arquivo_original, content_type),
    )
    batch.bronze_storage_bucket = stored.bucket
    batch.bronze_storage_key = stored.key
    batch.bronze_content_type = stored.content_type
    batch.bronze_size_bytes = stored.size_bytes
    batch.bronze_uploaded_at = stored.uploaded_at
    batch.arquivo_bronze = None
    return stored


def read_batch_payload(batch: LeadBatch) -> bytes | None:
    if batch.bronze_storage_bucket and batch.bronze_storage_key:
        return _read_bytes(bucket=batch.bronze_storage_bucket, key=batch.bronze_storage_key)
    return batch.arquivo_bronze


def persist_etl_job_payload(
    job: LeadImportEtlJob,
    payload: bytes,
    *,
    content_type: str | None = None,
) -> StoredPayload:
    bucket = _storage_bucket()
    key = _build_key(
        prefix="lead-import-etl-jobs",
        stable_id=job.job_id,
        filename=job.filename,
    )
    stored = _store_bytes(
        bucket=bucket,
        key=key,
        payload=payload,
        content_type=_guess_content_type(job.filename, content_type),
    )
    job.file_storage_bucket = stored.bucket
    job.file_storage_key = stored.key
    job.file_content_type = stored.content_type
    job.file_size_bytes = stored.size_bytes
    job.file_uploaded_at = stored.uploaded_at
    job.file_blob = None
    return stored


def read_etl_job_payload(job: LeadImportEtlJob) -> bytes | None:
    if job.file_storage_bucket and job.file_storage_key:
        return _read_bytes(bucket=job.file_storage_bucket, key=job.file_storage_key)
    return job.file_blob
