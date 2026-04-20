"""Chunked upload spooling helpers for import payloads."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from tempfile import SpooledTemporaryFile
from typing import BinaryIO

from fastapi import UploadFile

from app.services.imports.file_reader import BYTES_PER_MEGABYTE, ImportFileError

DEFAULT_UPLOAD_SPOOL_MAX_MEMORY_BYTES = 2 * 1024 * 1024
DEFAULT_UPLOAD_READ_CHUNK_BYTES = 1024 * 1024


@dataclass
class SpooledUploadPayload:
    filename: str
    sha256: str
    size_bytes: int
    file: BinaryIO

    def close(self) -> None:
        self.file.close()


def spool_upload_payload(
    upload: UploadFile,
    *,
    max_bytes: int,
    spool_max_memory_bytes: int = DEFAULT_UPLOAD_SPOOL_MAX_MEMORY_BYTES,
    chunk_size: int = DEFAULT_UPLOAD_READ_CHUNK_BYTES,
) -> SpooledUploadPayload:
    """Copy an UploadFile to a spooled file while computing size and SHA-256."""
    filename = upload.filename or ""
    digest = hashlib.sha256()
    total_size = 0
    spool = SpooledTemporaryFile(max_size=spool_max_memory_bytes, mode="w+b")
    try:
        upload.file.seek(0)
        while True:
            chunk = upload.file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_bytes:
                raise ImportFileError(
                    code="FILE_TOO_LARGE",
                    message=(
                        f"Arquivo muito grande: {total_size / BYTES_PER_MEGABYTE:.1f} MB. "
                        f"Limite permitido: {max_bytes / BYTES_PER_MEGABYTE:.1f} MB"
                    ),
                    field="file",
                    extra={"max_bytes": max_bytes},
                )
            digest.update(chunk)
            spool.write(chunk)
        if total_size == 0:
            raise ImportFileError(code="EMPTY_FILE", message="Arquivo vazio", field="file")
        spool.seek(0)
        upload.file.seek(0)
        return SpooledUploadPayload(
            filename=filename,
            sha256=digest.hexdigest(),
            size_bytes=total_size,
            file=spool,
        )
    except Exception:
        spool.close()
        raise
