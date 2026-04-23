"""Use cases for leads import endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from fastapi import UploadFile, status
from pydantic import TypeAdapter, ValidationError
from sqlmodel import Session, select

from app.models.models import Lead, LeadAlias, LeadAliasTipo
from app.schemas.lead_import import LeadImportMapping


def preview_import_sample_usecase(
    *,
    file: UploadFile,
    sample_rows: int,
    session: Session,
    current_user: Any,
    allowed_import_extensions: set[str],
    max_import_file_bytes: int,
    read_xlsx_sample: Callable[..., dict[str, Any]],
    read_csv_sample: Callable[..., dict[str, Any]],
    column_samples: Callable[[list[list[str]], int], list[str]],
    infer_column_mapping: Callable[[str, list[str]], LeadImportMapping],
    normalize_alias_value: Callable[[str], str],
    raise_http_error: Callable[..., None],
) -> dict[str, Any]:
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in allowed_import_extensions:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_import_file_bytes:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message="Arquivo excede o tamanho maximo permitido",
            field="file",
            extra={"max_bytes": max_import_file_bytes},
        )

    if size == 0:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )

    if sample_rows < 1 or sample_rows > 50:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_SAMPLE_SIZE",
            message="sample_rows deve ser entre 1 e 50",
            field="sample_rows",
        )

    if ext == ".xlsx":
        preview = read_xlsx_sample(file, max_rows=sample_rows)
    else:
        preview = read_csv_sample(file, max_rows=sample_rows)

    if not preview["rows"] and not preview["headers"]:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Arquivo vazio",
            field="file",
        )

    headers = preview["headers"]
    rows = preview["rows"]
    suggestions: list[LeadImportMapping] = []
    samples_by_column: list[list[str]] = []
    alias_hits: list[dict[str, Any] | None] = []

    for idx, header in enumerate(headers):
        samples = column_samples(rows, idx)
        samples_by_column.append(samples)
        suggestion = infer_column_mapping(header, samples)
        suggestions.append(suggestion)

        hit = None
        if suggestion.campo in {"evento_nome", "cidade", "estado", "genero"} and samples:
            alias_tipo = {
                "evento_nome": LeadAliasTipo.EVENTO,
                "cidade": LeadAliasTipo.CIDADE,
                "estado": LeadAliasTipo.ESTADO,
                "genero": LeadAliasTipo.GENERO,
            }[suggestion.campo]
            normalized = normalize_alias_value(samples[0])
            alias = session.exec(
                select(LeadAlias).where(
                    LeadAlias.tipo == alias_tipo,
                    LeadAlias.valor_normalizado == normalized,
                )
            ).first()
            if alias:
                hit = {
                    "tipo": alias.tipo,
                    "valor_origem": alias.valor_origem,
                    "canonical_value": alias.canonical_value,
                    "evento_id": alias.evento_id,
                }

        alias_hits.append(hit)

    return {
        "filename": filename,
        **preview,
        "suggestions": [s.model_dump() for s in suggestions],
        "samples_by_column": samples_by_column,
        "alias_hits": alias_hits,
    }


def validar_mapeamento_usecase(
    *,
    mappings: list[LeadImportMapping],
    ensure_mapping_has_essential: Callable[[list[LeadImportMapping]], None],
) -> dict[str, bool]:
    ensure_mapping_has_essential(mappings)
    return {"ok": True}


def importar_leads_usecase(
    *,
    file: UploadFile,
    mappings_json: str,
    fonte_origem: str | None,
    enriquecer_cep: bool,
    session: Session,
    current_user: Any,
    allowed_import_extensions: set[str],
    read_xlsx_sample: Callable[..., dict[str, Any]],
    read_csv_sample: Callable[..., dict[str, Any]],
    iter_xlsx_data_rows: Callable[..., Any],
    iter_csv_data_rows: Callable[..., Any],
    ensure_mapping_has_essential: Callable[[list[LeadImportMapping]], None],
    dedupe_key: Callable[[dict[str, object]], str | None],
    process_batch: Callable[[Session, list[tuple[dict[str, object], int] | None]], tuple[int, int, int, bool]],
    fetch_cep_data: Callable[[str], dict[str, str] | None],
    coerce_field: Callable[[str, Any], Any],
    log_memory_usage: Callable[..., None],
    batch_size: int,
    batch_summary_limit: int,
    raise_http_error: Callable[..., None],
) -> dict[str, Any]:
    _ = current_user
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in allowed_import_extensions:
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Formato de arquivo invalido (use .csv ou .xlsx)",
            field="file",
        )

    try:
        raw = json.loads(mappings_json)
        mappings = TypeAdapter(list[LeadImportMapping]).validate_python(raw)
    except (json.JSONDecodeError, ValidationError):
        raise_http_error(
            status.HTTP_400_BAD_REQUEST,
            code="INVALID_MAPPING",
            message="Mapeamento invalido",
            field="mappings",
        )

    ensure_mapping_has_essential(mappings)

    if ext == ".xlsx":
        preview = read_xlsx_sample(file, max_rows=20)
        start_index = preview["start_index"]
        row_iter = iter_xlsx_data_rows(file, start_index)
    else:
        preview = read_csv_sample(file, max_rows=20)
        start_index = preview["start_index"]
        delimiter = preview["delimiter"]
        row_iter = iter_csv_data_rows(file, delimiter, start_index)

    mapping_by_index: dict[int, str] = {}
    for idx, mapping in enumerate(mappings):
        if mapping.campo:
            mapping_by_index[idx] = mapping.campo

    created = 0
    updated = 0
    skipped = 0
    total = 0
    batch_stats: list[dict[str, int | bool]] = []
    batch_index = 0

    log_memory_usage("start")
    batch: list[tuple[dict[str, object], int] | None] = []
    key_to_index: dict[str, int] = {}

    for offset, row in enumerate(row_iter):
        if not row:
            continue

        payload: dict[str, object] = {}
        for idx, field in mapping_by_index.items():
            if idx >= len(row):
                continue
            payload[field] = coerce_field(field, row[idx])

        if enriquecer_cep:
            cep = payload.get("cep")
            if isinstance(cep, str) and cep:
                cep_data = fetch_cep_data(cep)
                if cep_data:
                    for key, value in cep_data.items():
                        if value and not payload.get(key):
                            payload[key] = value

        if "fonte_origem" in Lead.model_fields and fonte_origem:
            payload["fonte_origem"] = fonte_origem

        if isinstance(payload.get("data_compra"), datetime):
            payload["data_compra_data"] = payload["data_compra"].date()
            payload["data_compra_hora"] = payload["data_compra"].time()

        row_number = start_index + 2 + offset
        key = dedupe_key(payload)
        if key:
            prev_idx = key_to_index.get(key)
            if prev_idx is not None:
                batch[prev_idx] = None
            key_to_index[key] = len(batch)

        batch.append((payload, row_number))
        if len(batch) < batch_size:
            continue

        batch_total = sum(1 for item in batch if item)
        batch_created, batch_updated, batch_skipped, batch_has_errors = process_batch(session, batch)
        created += batch_created
        updated += batch_updated
        skipped += batch_skipped
        total += batch_total
        batch_stats.append(
            {
                "batch": batch_index,
                "created": batch_created,
                "updated": batch_updated,
                "skipped": batch_skipped,
                "has_errors": batch_has_errors,
            }
        )
        log_memory_usage("batch", batch_index)
        batch_index += 1
        batch = []
        key_to_index = {}

    if batch:
        batch_total = sum(1 for item in batch if item)
        batch_created, batch_updated, batch_skipped, batch_has_errors = process_batch(session, batch)
        created += batch_created
        updated += batch_updated
        skipped += batch_skipped
        total += batch_total
        batch_stats.append(
            {
                "batch": batch_index,
                "created": batch_created,
                "updated": batch_updated,
                "skipped": batch_skipped,
                "has_errors": batch_has_errors,
            }
        )
        log_memory_usage("batch", batch_index)

    log_memory_usage("end")

    batch_stats.sort(key=lambda item: int(item["batch"]))
    batches_total = len(batch_stats)
    batches_truncated = False
    batches = batch_stats
    if batches_total > batch_summary_limit:
        batches = batch_stats[:batch_summary_limit]
        batches_truncated = True

    errors = skipped
    summary = {
        "filename": filename,
        "total": total,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }

    return {
        "filename": filename,
        "total": total,
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "summary": summary,
        "batches": batches,
        "batches_total": batches_total,
        "batches_truncated": batches_truncated,
    }
