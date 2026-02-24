"""File fingerprint helpers for source registry and ingestion reproducibility.

This module provides deterministic SHA256 hashing and a minimal metadata
snapshot for local files used as ETL sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import stat as statlib
from pathlib import Path

from core.registry.errors import SourceFileError, SourceFileNotFoundError, SourceFilePermissionError

READ_CHUNK_SIZE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class FileMetadata:
    """Minimal immutable metadata used to fingerprint one source file.

    Attributes:
        path: Absolute resolved filesystem path.
        file_size_bytes: File size in bytes.
        file_mtime_utc: Last modified timestamp in UTC.
    """

    path: str
    file_size_bytes: int
    file_mtime_utc: datetime


def compute_file_sha256(path: str | Path, *, chunk_size: int = READ_CHUNK_SIZE_BYTES) -> str:
    """Compute a deterministic SHA256 hash for one file.

    Args:
        path: Source file path.
        chunk_size: Read size in bytes for incremental hashing.

    Returns:
        Lowercase hex SHA256 digest.

    Raises:
        SourceFileNotFoundError: If the file path does not exist.
        SourceFilePermissionError: If file content cannot be read due to permissions.
        SourceFileError: If path does not refer to a regular file.
    """

    target = Path(path).expanduser()
    if chunk_size <= 0:
        raise SourceFileError(
            f"Chunk size invalido para hash: {chunk_size}",
            action="Informar chunk_size inteiro maior que zero.",
        )

    digest = hashlib.sha256()
    try:
        with target.open("rb") as stream:
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
    except FileNotFoundError as exc:
        raise SourceFileNotFoundError(str(target)) from exc
    except PermissionError as exc:
        raise SourceFilePermissionError(str(target), "ler") from exc
    except IsADirectoryError as exc:
        raise SourceFileError(
            f"Caminho nao aponta para arquivo regular: {target}",
            action="Informar caminho de arquivo (nao diretorio) para fingerprint.",
        ) from exc

    return digest.hexdigest()


def collect_file_metadata(path: str | Path) -> FileMetadata:
    """Collect minimum metadata required for source audit and debug.

    Args:
        path: Source file path.

    Returns:
        FileMetadata with absolute path, size and mtime.

    Raises:
        SourceFileNotFoundError: If the file path does not exist.
        SourceFilePermissionError: If metadata cannot be read due to permissions.
        SourceFileError: If path does not refer to a regular file.
    """

    target = Path(path).expanduser()
    try:
        stats = target.stat()
    except FileNotFoundError as exc:
        raise SourceFileNotFoundError(str(target)) from exc
    except PermissionError as exc:
        raise SourceFilePermissionError(str(target), "coletar metadados de") from exc

    if not statlib.S_ISREG(stats.st_mode):
        raise SourceFileError(
            f"Caminho nao aponta para arquivo regular: {target}",
            action="Informar caminho de arquivo (nao diretorio) para coletar metadados.",
        )

    return FileMetadata(
        path=str(target.resolve()),
        file_size_bytes=int(stats.st_size),
        file_mtime_utc=datetime.fromtimestamp(stats.st_mtime, tz=timezone.utc),
    )

