"""Service helpers for ETL registry (`sources` and `ingestions`) persistence.

This module centralizes source registration from local files and ingestion run
lifecycle management (start/finish) for extractors and loaders.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any

from sqlmodel import Session, select

from app.models.etl_registry import IngestionRun, IngestionStatus, Source, SourceKind, now_utc


_SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
_READ_CHUNK_SIZE_BYTES = 1024 * 1024
_LINEAGE_POLICIES = ("required", "optional")
_LINEAGE_SEVERITIES = ("partial", "failed")


def _normalize_source_id(value: str) -> str:
    """Normalize and validate source ID for stable upsert operations.

    Args:
        value: Raw source identifier.

    Returns:
        Normalized identifier with uppercase letters and underscores.

    Raises:
        ValueError: If source ID is empty or does not match allowed pattern.
    """

    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not _SOURCE_ID_RE.match(normalized):
        raise ValueError(
            "source_id invalido. Use 3-160 chars com A-Z, 0-9 e underscore."
        )
    return normalized


def _resolve_source_kind(path: Path) -> SourceKind:
    """Infer source kind from file extension.

    Args:
        path: Path to source file.

    Returns:
        SourceKind inferred from extension or `OTHER` when unknown.
    """

    suffix = path.suffix.lower()
    if suffix in {".yml", ".yaml", ".json"}:
        return SourceKind.CONFIG
    if suffix == ".pdf":
        return SourceKind.PDF
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return SourceKind.XLSX
    if suffix == ".pptx":
        return SourceKind.PPTX
    if suffix == ".docx":
        return SourceKind.DOCX
    if suffix == ".csv":
        return SourceKind.CSV
    return SourceKind.OTHER


def _compute_file_sha256(path: Path) -> str:
    """Compute SHA256 digest for a source file.

    Args:
        path: File path to hash.

    Returns:
        SHA256 hexadecimal digest.
    """

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(_READ_CHUNK_SIZE_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def register_source_from_path(session: Session, source_id: str, path: str | Path) -> Source:
    """Register or update one source from a local file path.

    Args:
        session: Open SQLModel session.
        source_id: Stable business identifier for the source.
        path: File path used for source registration.

    Returns:
        Persisted Source model.

    Raises:
        FileNotFoundError: If path does not point to an existing file.
        PermissionError: If file metadata/content cannot be read.
        ValueError: If source_id is invalid.
    """

    normalized_source_id = _normalize_source_id(source_id)
    source_path = Path(path).expanduser()
    if not source_path.is_file():
        raise FileNotFoundError(f"Arquivo de fonte nao encontrado: {source_path}")

    file_stats = source_path.stat()
    file_sha256 = _compute_file_sha256(source_path)
    file_mtime_utc = datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)

    existing = session.exec(
        select(Source).where(Source.source_id == normalized_source_id)
    ).first()
    if existing is None:
        source = Source(
            source_id=normalized_source_id,
            kind=_resolve_source_kind(source_path),
            uri=str(source_path.resolve()),
            display_name=source_path.name,
            file_sha256=file_sha256,
            file_size_bytes=int(file_stats.st_size),
            file_mtime_utc=file_mtime_utc,
        )
        session.add(source)
    else:
        source = existing
        source.kind = _resolve_source_kind(source_path)
        source.uri = str(source_path.resolve())
        source.display_name = source_path.name
        source.file_sha256 = file_sha256
        source.file_size_bytes = int(file_stats.st_size)
        source.file_mtime_utc = file_mtime_utc
        source.updated_at = now_utc()

    session.commit()
    session.refresh(source)
    return source


def start_ingestion_run(
    session: Session,
    source_id: str,
    extractor_name: str,
) -> IngestionRun:
    """Start one ingestion run linked to an existing source.

    Args:
        session: Open SQLModel session.
        source_id: Stable source identifier.
        extractor_name: Extractor/loader name for run traceability.

    Returns:
        Persisted IngestionRun model.

    Raises:
        ValueError: If source does not exist or input is invalid.
    """

    normalized_source_id = _normalize_source_id(source_id)
    source = session.exec(
        select(Source).where(Source.source_id == normalized_source_id)
    ).first()
    if source is None:
        raise ValueError(f"Fonte nao registrada no ETL registry: {normalized_source_id}")

    run = IngestionRun(
        source_pk=source.id,
        extractor_name=(extractor_name or "").strip() or None,
        status=IngestionStatus.PARTIAL,
        started_at=now_utc(),
        file_sha256=source.file_sha256,
        file_size_bytes=source.file_size_bytes,
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def finish_ingestion_run(
    session: Session,
    ingestion_id: int,
    status: IngestionStatus,
    notes: str | None = None,
) -> None:
    """Finish an ingestion run by setting terminal status and notes.

    Args:
        session: Open SQLModel session.
        ingestion_id: Ingestion run primary key.
        status: Final ingestion status (`success`, `failed`, `partial`).
        notes: Optional run summary, warning or error text.

    Raises:
        ValueError: If run does not exist.
    """

    run = session.get(IngestionRun, ingestion_id)
    if run is None:
        raise ValueError(f"Ingestion run nao encontrado: {ingestion_id}")

    run.status = status
    run.finished_at = now_utc()
    run.notes = notes
    session.add(run)
    session.commit()


def _coerce_lineage_policy(value: str) -> str:
    """Normalize lineage policy name and validate domain."""
    normalized = (value or "").strip().lower()
    if normalized not in _LINEAGE_POLICIES:
        raise ValueError(
            "lineage policy invalida. Como corrigir: usar policy em {required, optional}."
        )
    return normalized


def _coerce_lineage_severity(value: str) -> str:
    """Normalize lineage severity and validate domain."""
    normalized = (value or "").strip().lower()
    if normalized not in _LINEAGE_SEVERITIES:
        raise ValueError(
            "lineage severity invalida. Como corrigir: usar severity_on_missing em {partial, failed}."
        )
    return normalized


def _record_has_lineage(record: Any, lineage_field: str) -> bool:
    """Check whether one record carries a valid lineage reference ID."""
    lineage_value = None
    if isinstance(record, dict):
        lineage_value = record.get(lineage_field)
    elif hasattr(record, lineage_field):
        lineage_value = getattr(record, lineage_field)
    elif hasattr(record, "model_dump"):
        dumped = record.model_dump()
        if isinstance(dumped, dict):
            lineage_value = dumped.get(lineage_field)

    try:
        return int(lineage_value) > 0
    except (TypeError, ValueError):
        return False


def _append_note(existing: str | None, message: str) -> str:
    """Append one enforcement note preserving existing run notes."""
    previous = (existing or "").strip()
    return f"{previous}\n{message}".strip() if previous else message


def enforce_lineage_policy(
    session: Session,
    *,
    ingestion_id: int,
    dataset_name: str,
    records: Sequence[Any],
    policy: str = "optional",
    severity_on_missing: str = "partial",
    lineage_field: str = "lineage_ref_id",
) -> None:
    """Enforce lineage coverage for a dataset and update ingestion run status.

    Args:
        session: Open SQLModel session.
        ingestion_id: Target ingestion run primary key.
        dataset_name: Dataset name for actionable error messages.
        records: Records to inspect for lineage field.
        policy: Lineage policy (`required` or `optional`).
        severity_on_missing: Status when required lineage is missing (`partial` or `failed`).
        lineage_field: Field name that should contain lineage reference ID.

    Raises:
        ValueError: If ingestion run is missing, policy config is invalid, or
            required lineage is missing.
    """

    run = session.get(IngestionRun, ingestion_id)
    if run is None:
        raise ValueError(f"Ingestion run nao encontrado: {ingestion_id}")

    dataset = (dataset_name or "").strip()
    if not dataset:
        raise ValueError("dataset_name vazio. Como corrigir: informar nome do dataset.")

    normalized_policy = _coerce_lineage_policy(policy)
    normalized_severity = _coerce_lineage_severity(severity_on_missing)
    field_name = (lineage_field or "").strip()
    if not field_name:
        raise ValueError("lineage_field vazio. Como corrigir: informar nome de campo valido.")

    missing_indexes: list[int] = []
    for index, record in enumerate(records):
        if not _record_has_lineage(record, field_name):
            missing_indexes.append(index)

    if normalized_policy == "optional" or not missing_indexes:
        return

    final_status = (
        IngestionStatus.FAILED
        if normalized_severity == "failed"
        else IngestionStatus.PARTIAL
    )
    message = (
        f"Dataset '{dataset}' exige linhagem e possui {len(missing_indexes)}/{len(records)} "
        f"registros sem '{field_name}' (indices: {missing_indexes[:10]}). "
        "Como corrigir: gerar lineage_ref_id para todos os registros antes do load."
    )
    run.status = final_status
    run.finished_at = now_utc()
    run.notes = _append_note(run.notes, message)
    session.add(run)
    session.commit()
    raise ValueError(message)
