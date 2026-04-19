"""Create ETL preview snapshots."""

from __future__ import annotations

import json
import logging
import secrets
import time
from typing import Any

from sqlmodel import Session

from app.models.models import Evento
from app.observability.import_events import log_import_event, session_token_prefix

from .contracts import EtlCpfColumnRequired, EtlFieldAliasSelection, EtlHeaderRequired, EtlPreviewSnapshot
from .dq_report_mapper import map_check_report
from .dq_report_policy import compute_has_warnings
from .exceptions import EtlImportContractError
from .extract import (
    clamp_etl_max_scan_rows,
    compute_file_fingerprint,
    extract_csv_rows,
    extract_xlsx_rows,
    read_upload_bytes,
)
from .preview_session_repository import create_snapshot
from .transform_validate import run_preview_validation

logger = logging.getLogger(__name__)


def _parse_field_aliases_json(raw: str | None) -> dict[str, EtlFieldAliasSelection]:
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EtlImportContractError("field_aliases_json deve ser um JSON valido.") from exc
    if not isinstance(payload, dict):
        raise EtlImportContractError("field_aliases_json deve ser um objeto JSON.")

    aliases: dict[str, EtlFieldAliasSelection] = {}
    for raw_field, raw_value in payload.items():
        field_name = str(raw_field or "").strip().lower()
        if not field_name:
            continue
        if not isinstance(raw_value, dict):
            raise EtlImportContractError("Cada alias de campo deve ser um objeto JSON.")
        value: dict[str, Any] = raw_value
        column_index_raw = value.get("column_index")
        column_index: int | None = None
        if column_index_raw is not None and column_index_raw != "":
            try:
                column_index = int(column_index_raw)
            except (TypeError, ValueError) as exc:
                raise EtlImportContractError("column_index de alias deve ser inteiro.") from exc
            if column_index < 1:
                raise EtlImportContractError("column_index de alias deve ser 1-indexed e positivo.")
        source_value_raw = value.get("source_value")
        source_value = str(source_value_raw).strip() if source_value_raw is not None else None
        aliases[field_name] = EtlFieldAliasSelection(
            column_index=column_index,
            source_value=source_value or None,
        )
    return aliases


def create_preview_snapshot(
    *,
    file,
    evento_id: int,
    strict: bool,
    db: Session,
    max_bytes: int,
    header_row: int | None = None,
    field_aliases_json: str | None = None,
    sheet_name: str | None = None,
    max_scan_rows: int | None = None,
) -> EtlPreviewSnapshot | EtlHeaderRequired | EtlCpfColumnRequired:
    started_at = time.perf_counter()
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise EtlImportContractError(f"Evento inexistente: {evento_id}")

    log_import_event(
        logger,
        "etl.preview.start",
        evento_id=evento_id,
        filename_hint=(getattr(file, "filename", None) or "")[:240] or None,
    )

    filename, ext, payload = read_upload_bytes(file, max_bytes=max_bytes)
    field_aliases = _parse_field_aliases_json(field_aliases_json)
    scan_rows = clamp_etl_max_scan_rows(max_scan_rows)
    if ext == ".xlsx":
        extracted = extract_xlsx_rows(
            payload,
            db=db,
            header_row=header_row,
            field_aliases=field_aliases,
            sheet_name=sheet_name,
            max_scan_rows=scan_rows,
        )
    elif ext == ".csv":
        extracted = extract_csv_rows(
            payload,
            db=db,
            header_row=header_row,
            field_aliases=field_aliases,
            max_scan_rows=scan_rows,
        )
    else:
        raise EtlImportContractError("Fluxo ETL suporta apenas arquivos .csv ou .xlsx.")
    if isinstance(extracted, (EtlHeaderRequired, EtlCpfColumnRequired)):
        log_import_event(
            logger,
            "etl.preview.blocked",
            evento_id=evento_id,
            outcome="blocked",
            blocked_status=extracted.status,
            duration_ms=round((time.perf_counter() - started_at) * 1000),
        )
        return extracted

    extracted_rows, metadata = extracted
    state, report = run_preview_validation(extracted_rows, evento_nome=str(evento.nome))
    dq_report = map_check_report(report)
    file_fingerprint = compute_file_fingerprint(filename, payload)
    header_context = {
        "header_row": metadata.get("header_row"),
        "field_aliases": metadata.get("applied_field_aliases") or {},
        "sheet_name": metadata.get("sheet_name"),
        "max_scan_rows": scan_rows,
    }
    header_context_digest = compute_file_fingerprint(
        "header-context",
        json.dumps(header_context, sort_keys=True, ensure_ascii=False).encode("utf-8"),
    )[:16]
    sheet_snap: str | None = None
    avail_snap: tuple[str, ...] = ()
    if ext == ".xlsx":
        raw_name = metadata.get("sheet_name")
        sheet_snap = str(raw_name) if raw_name is not None else None
        raw_list = metadata.get("available_sheets") or []
        if isinstance(raw_list, list):
            avail_snap = tuple(str(s) for s in raw_list if s is not None)

    snapshot = EtlPreviewSnapshot(
        session_token=secrets.token_urlsafe(24),
        filename=filename,
        evento_id=evento_id,
        evento_nome=str(evento.nome),
        strict=bool(strict),
        total_rows=len(extracted_rows),
        valid_rows=len(state.approved_rows),
        invalid_rows=len(state.rejected_rows),
        approved_rows=state.approved_rows,
        rejected_rows=state.rejected_rows,
        dq_report=dq_report,
        status="previewed",
        idempotency_key=(
            f"lead-etl-preview:{evento_id}:{file_fingerprint}:"
            f"{int(bool(strict))}:h{header_context_digest}"
        ),
        has_validation_errors=any(item.severity == "error" for item in dq_report),
        has_warnings=compute_has_warnings(dq_report),
        sheet_name=sheet_snap,
        available_sheets=avail_snap,
    )
    out = create_snapshot(db, snapshot)
    log_import_event(
        logger,
        "etl.preview.completed",
        evento_id=evento_id,
        outcome="previewed",
        session_token_prefix=session_token_prefix(out.session_token),
        total_rows=out.total_rows,
        valid_rows=out.valid_rows,
        invalid_rows=out.invalid_rows,
        duration_ms=round((time.perf_counter() - started_at) * 1000),
    )
    return out
