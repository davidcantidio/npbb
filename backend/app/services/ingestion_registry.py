"""Ingestion Registry / Catalogo de fontes.

This module centralizes:
- Source registration (stable `source_id` keys for planning and audit),
- Ingestion run tracking (status, timings, logs),
- File snapshotting (sha256/size/mtime) for versioning.

The goal is operational discipline: no data should enter the system without a
traceable source and an ingestion run record.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from app.models.models import IngestionRun, IngestionStatus, Source, SourceKind, now_utc


SOURCE_ID_ALLOWED_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")


@dataclass(frozen=True)
class FileSnapshot:
    """Snapshot of a file at a point in time (best-effort)."""

    sha256: str
    size_bytes: int
    mtime_utc: datetime


def normalize_source_id(value: str) -> str:
    """Normalize a `source_id` to the repository convention (uppercase, underscores).

    Convention (recommended):
    - starts with SRC_
    - uppercase A-Z, digits, underscore
    - examples: SRC_PDF_ACESSO_NOTURNO_TREZE, SRC_XLSX_OPTIN_ACEITOS_DOZE

    Args:
        value: Raw source id provided by operator/pipeline.

    Returns:
        Normalized id (uppercase, spaces->underscore).

    Raises:
        ValueError: When the normalized id is empty or violates the allowed pattern.
    """
    raw = (value or "").strip()
    if not raw:
        raise ValueError("source_id vazio")
    normalized = raw.upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not SOURCE_ID_ALLOWED_RE.match(normalized):
        raise ValueError(
            "source_id invalido. Use apenas A-Z, 0-9 e underscore, com tamanho entre 3 e 160."
        )
    return normalized


def compute_sha256(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Compute sha256 for a file.

    Args:
        path: File path.
        chunk_size: Read size per iteration.

    Returns:
        Hex digest string.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def build_file_snapshot(path: Path) -> FileSnapshot:
    """Build a FileSnapshot from a path."""
    st = path.stat()
    return FileSnapshot(
        sha256=compute_sha256(path),
        size_bytes=int(st.st_size),
        mtime_utc=datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
    )


def register_source(
    session: Session,
    *,
    source_id: str,
    kind: SourceKind,
    uri: str,
    display_name: Optional[str] = None,
    snapshot: Optional[FileSnapshot] = None,
) -> Source:
    """Create or update a Source registry record."""
    sid = normalize_source_id(source_id)
    src = session.get(Source, sid)
    if src is None:
        src = Source(
            source_id=sid,
            kind=kind,
            uri=uri,
            display_name=display_name,
        )
        session.add(src)
    else:
        src.kind = kind
        src.uri = uri
        if display_name is not None:
            src.display_name = display_name
        src.updated_at = now_utc()

    if snapshot is not None:
        src.file_sha256 = snapshot.sha256
        src.file_size_bytes = snapshot.size_bytes
        src.file_mtime_utc = snapshot.mtime_utc

    session.commit()
    session.refresh(src)
    return src


def start_ingestion(
    session: Session,
    *,
    source_id: str,
    pipeline: str | None = None,
    snapshot: Optional[FileSnapshot] = None,
) -> IngestionRun:
    """Create an ingestion run with status RUNNING."""
    sid = normalize_source_id(source_id)
    src = session.get(Source, sid)
    if src is None:
        raise ValueError(f"Source nao registrada: {sid}")

    if snapshot is not None:
        # Keep latest file snapshot on the Source as well.
        src.file_sha256 = snapshot.sha256
        src.file_size_bytes = snapshot.size_bytes
        src.file_mtime_utc = snapshot.mtime_utc
        src.updated_at = now_utc()

    run = IngestionRun(
        source_id=sid,
        pipeline=pipeline,
        status=IngestionStatus.RUNNING,
        file_sha256=snapshot.sha256 if snapshot else None,
        file_size_bytes=snapshot.size_bytes if snapshot else None,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def finish_ingestion(
    session: Session,
    *,
    ingestion_id: int,
    status: IngestionStatus,
    log_text: str | None = None,
    error_message: str | None = None,
) -> IngestionRun:
    """Finish an ingestion run and persist final status and logs."""
    run = session.get(IngestionRun, ingestion_id)
    if run is None:
        raise ValueError(f"IngestionRun nao encontrada: {ingestion_id}")

    run.status = status
    run.finished_at = now_utc()
    if log_text is not None:
        run.log_text = log_text
    if error_message is not None:
        run.error_message = error_message

    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def get_latest_ingestion_by_source(session: Session, *, source_id: str) -> Optional[IngestionRun]:
    """Return the latest ingestion for a given source_id."""
    sid = normalize_source_id(source_id)
    stmt = (
        select(IngestionRun)
        .where(IngestionRun.source_id == sid)
        .order_by(IngestionRun.started_at.desc())
        .limit(1)
    )
    return session.exec(stmt).first()

