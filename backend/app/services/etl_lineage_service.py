"""Helpers to persist and attach lineage references in ETL pipelines.

Extractors/loaders should use these helpers to avoid "data without source":
- create one `LineageRef` for each extracted metric evidence
- attach `lineage_ref_id` to staging/canonical records
"""

from __future__ import annotations

from collections.abc import MutableMapping
import re
from typing import Any, TypeVar, cast

from sqlmodel import Session, select

from app.models.etl_lineage import LineageLocationType, LineageRef, now_utc
from app.models.etl_registry import IngestionRun, Source


_SOURCE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,159}$")
_PAGE_RE = re.compile(r"^page:([1-9][0-9]*)$")
_SLIDE_RE = re.compile(r"^slide:([1-9][0-9]*)$")
_SHEET_RE = re.compile(r"^sheet:(.+)$")
_RANGE_RE = re.compile(
    r"^range:([A-Z]{1,3}[1-9][0-9]*):([A-Z]{1,3}[1-9][0-9]*)$",
    flags=re.IGNORECASE,
)

RecordT = TypeVar("RecordT")


def _normalize_source_id(value: str) -> str:
    """Normalize and validate source identifiers.

    Args:
        value: Raw source ID.

    Returns:
        Normalized uppercase source ID.

    Raises:
        ValueError: If source ID is empty or violates expected format.
    """

    normalized = (value or "").strip().upper().replace(" ", "_").replace("-", "_")
    normalized = re.sub(r"_+", "_", normalized)
    if not _SOURCE_ID_RE.match(normalized):
        raise ValueError(
            "source_id invalido. "
            "Como corrigir: usar 3-160 chars com A-Z, 0-9 e underscore."
        )
    return normalized


def _coerce_location_type(value: str | LineageLocationType) -> LineageLocationType:
    """Coerce raw location type input to `LineageLocationType`.

    Args:
        value: Raw or enum location type.

    Returns:
        Validated `LineageLocationType` enum value.

    Raises:
        ValueError: If location type is unsupported.
    """

    if isinstance(value, LineageLocationType):
        return value
    raw = (value or "").strip().lower()
    try:
        return LineageLocationType(raw)
    except ValueError as exc:
        raise ValueError(
            "location_type invalido. "
            "Como corrigir: usar {page, slide, sheet, range}."
        ) from exc


def _normalize_location_value(
    location_type: LineageLocationType,
    location_value: str,
) -> str:
    """Validate and normalize canonical location reference strings.

    Args:
        location_type: Domain of source location.
        location_value: Raw location value to validate.

    Returns:
        Canonical location value string.

    Raises:
        ValueError: If format/domain does not match expected canonical pattern.
    """

    raw = (location_value or "").strip()
    if not raw:
        raise ValueError(
            "location_value vazio. "
            "Como corrigir: usar formato canonico (ex.: page:12, slide:3, sheet:aba x, range:A1:D20)."
        )

    if location_type == LineageLocationType.PAGE:
        if not _PAGE_RE.match(raw):
            raise ValueError(
                f"location_value invalido para page: {raw!r}. "
                "Como corrigir: usar page:<inteiro_positivo>."
            )
        return raw

    if location_type == LineageLocationType.SLIDE:
        if not _SLIDE_RE.match(raw):
            raise ValueError(
                f"location_value invalido para slide: {raw!r}. "
                "Como corrigir: usar slide:<inteiro_positivo>."
            )
        return raw

    if location_type == LineageLocationType.SHEET:
        match = _SHEET_RE.match(raw)
        if not match:
            raise ValueError(
                f"location_value invalido para sheet: {raw!r}. "
                "Como corrigir: usar sheet:<nome_da_aba>."
            )
        sheet_name = re.sub(r"\s+", " ", match.group(1)).strip().lower()
        if not sheet_name:
            raise ValueError(
                "location_value invalido para sheet. "
                "Como corrigir: informar nome de aba nao vazio."
            )
        return f"sheet:{sheet_name}"

    match = _RANGE_RE.match(raw)
    if not match:
        raise ValueError(
            f"location_value invalido para range: {raw!r}. "
            "Como corrigir: usar range:<CELA_INICIO>:<CELA_FIM>."
        )
    return f"range:{match.group(1).upper()}:{match.group(2).upper()}"


def create_lineage_ref(
    session: Session,
    *,
    source_id: str,
    location_type: str | LineageLocationType,
    location_value: str,
    ingestion_id: int | None = None,
    evidence_text: str | None = None,
    is_aggregated_metric: bool = False,
) -> LineageRef:
    """Persist one lineage reference used by extractor/loader outputs.

    Extractors should pass `evidence_text` as the source label that supports the
    metric (for example: table title in PDF or slide chart label in PPTX).

    Args:
        session: Open database session.
        source_id: Stable source identifier (`sources.source_id`).
        location_type: Location domain (`page`, `slide`, `sheet`, `range`).
        location_value: Canonical location string for the chosen type.
        ingestion_id: Optional ingestion run identifier associated with source.
        evidence_text: Human-readable evidence label/title from source.
        is_aggregated_metric: Whether this lineage represents aggregated metric.

    Returns:
        Persisted `LineageRef`.

    Raises:
        ValueError: If source/ingestion is invalid, location format is invalid,
            or evidence is missing for aggregated metrics.
    """

    normalized_source_id = _normalize_source_id(source_id)
    source = session.exec(select(Source).where(Source.source_id == normalized_source_id)).first()
    if source is None:
        raise ValueError(f"Fonte nao registrada no ETL registry: {normalized_source_id}")

    run: IngestionRun | None = None
    if ingestion_id is not None:
        run = session.get(IngestionRun, ingestion_id)
        if run is None:
            raise ValueError(f"Ingestion run nao encontrado: {ingestion_id}")
        if run.source_pk != source.id:
            raise ValueError(
                "Ingestion run nao pertence ao source informado. "
                "Como corrigir: usar source_id correspondente ao ingestion_id."
            )

    evidence = (evidence_text or "").strip() or None
    if is_aggregated_metric and not evidence:
        raise ValueError(
            "evidence_text obrigatorio para metrica agregada. "
            "Como corrigir: informar titulo da tabela/label do slide que comprova o numero."
        )

    kind = _coerce_location_type(location_type)
    normalized_location = _normalize_location_value(kind, location_value)

    lineage_ref = LineageRef(
        source_id=normalized_source_id,
        ingestion_id=run.id if run else None,
        location_type=kind,
        location_value=normalized_location,
        evidence_text=evidence,
        created_at=now_utc(),
    )
    session.add(lineage_ref)
    session.commit()
    session.refresh(lineage_ref)
    return lineage_ref


def attach_lineage(record: RecordT, lineage_ref_id: int) -> RecordT:
    """Attach one lineage reference ID to a staging/canonical record.

    Standard field name is always `lineage_ref_id` to avoid extractor-specific
    variations.

    Args:
        record: Mutable mapping or object to receive lineage reference ID.
        lineage_ref_id: Persisted lineage reference identifier.

    Returns:
        Same record instance (or dict copy for pydantic-like records).

    Raises:
        ValueError: If `lineage_ref_id` is not a positive integer.
        TypeError: If record type cannot receive `lineage_ref_id`.
    """

    if lineage_ref_id <= 0:
        raise ValueError(
            f"lineage_ref_id invalido: {lineage_ref_id}. "
            "Como corrigir: informar ID positivo gerado por create_lineage_ref."
        )

    if isinstance(record, MutableMapping):
        record["lineage_ref_id"] = lineage_ref_id
        return record

    if hasattr(record, "model_dump"):
        dumped = cast(dict[str, Any], record.model_dump())  # pydantic-like
        dumped["lineage_ref_id"] = lineage_ref_id
        return cast(RecordT, dumped)

    try:
        setattr(record, "lineage_ref_id", lineage_ref_id)
        return record
    except Exception as exc:  # pragma: no cover - defensive guard
        raise TypeError(
            "record nao suportado para attach_lineage. "
            "Como corrigir: usar dict mutavel ou objeto com atributo lineage_ref_id."
        ) from exc

