"""Servico de importacao assistida para o dominio de publicidade."""

from __future__ import annotations

import hashlib
import json
from datetime import date

from fastapi import UploadFile
from sqlmodel import Session, select

from app.models.models import EventPublicity, Evento, PublicityImportStaging
from app.schemas.publicidade_import import PublicidadeImportError, PublicidadeImportMapping, PublicidadeImportReport
from app.services.imports.alias_service import find_alias
from app.services.imports.domain_publicidade import PUBLICIDADE_DOMAIN_SPEC, normalize_publicidade_value
from app.services.imports.file_reader import DEFAULT_IMPORT_MAX_BYTES, iter_data_rows, read_file_sample

MAX_ERROR_ROWS = 300


def run_publicidade_import(
    session: Session,
    *,
    file: UploadFile,
    mappings: list[PublicidadeImportMapping],
    dry_run: bool = False,
    max_bytes: int = DEFAULT_IMPORT_MAX_BYTES,
) -> PublicidadeImportReport:
    preview, ext = read_file_sample(file, sample_rows=20, max_bytes=max_bytes)
    filename = file.filename or preview.filename or ""
    mapping_by_index = {
        index: str(mapping.campo)
        for index, mapping in enumerate(mappings)
        if mapping.campo
    }
    received_rows = 0
    valid_rows = 0
    staged_inserted = 0
    staged_skipped = 0
    upsert_inserted = 0
    upsert_updated = 0
    unresolved_event_id = 0
    errors: list[PublicidadeImportError] = []

    seen_staging: set[tuple[str, str]] = set()
    seen_natural_keys: set[tuple[object, ...]] = set()
    pending_new_final: dict[tuple[object, ...], EventPublicity] = {}

    row_iter = iter_data_rows(
        file,
        ext=ext,
        start_index=preview.start_index,
        delimiter=preview.delimiter,
    )

    for offset, row in enumerate(row_iter):
        row_number = preview.start_index + 2 + offset
        if not row:
            continue
        received_rows += 1
        raw_payload: dict[str, str] = {}
        for index, field_name in mapping_by_index.items():
            raw_payload[field_name] = row[index] if index < len(row) else ""

        normalized, row_errors = _normalize_payload(raw_payload)
        if row_errors:
            _append_row_errors(errors, row_errors=row_errors, row_number=row_number)
            continue

        valid_rows += 1
        source_row_hash = _canonical_row_hash(normalized)
        staging_key = (filename, source_row_hash)

        if staging_key in seen_staging or _staging_exists(session, filename=filename, source_row_hash=source_row_hash):
            staged_skipped += 1
        else:
            seen_staging.add(staging_key)
            staged_inserted += 1
            if not dry_run:
                staging = PublicityImportStaging(
                    source_file=filename,
                    source_row_hash=source_row_hash,
                    codigo_projeto=str(normalized["codigo_projeto"]),
                    projeto=str(normalized["projeto"]),
                    data_vinculacao=normalized["data_vinculacao"],  # type: ignore[arg-type]
                    meio=str(normalized["meio"]),
                    veiculo=str(normalized["veiculo"]),
                    uf=str(normalized["uf"]),
                    uf_extenso=_string_or_none(normalized.get("uf_extenso")),
                    municipio=_string_or_none(normalized.get("municipio")),
                    camada=str(normalized["camada"]),
                    normalized_payload=json.dumps(_json_ready_payload(normalized), ensure_ascii=True),
                )
                session.add(staging)

        event_id = _resolve_event_id(
            session,
            codigo_projeto=str(normalized["codigo_projeto"]),
        )
        if event_id is None:
            unresolved_event_id += 1

        natural_key = _natural_key(normalized)
        if dry_run and natural_key in seen_natural_keys:
            continue

        existing = pending_new_final.get(natural_key)
        if existing is None:
            existing = session.exec(
                select(EventPublicity).where(
                    EventPublicity.publicity_project_code == str(normalized["codigo_projeto"]),
                    EventPublicity.linked_at == normalized["data_vinculacao"],  # type: ignore[arg-type]
                    EventPublicity.medium == str(normalized["meio"]),
                    EventPublicity.vehicle == str(normalized["veiculo"]),
                    EventPublicity.uf == str(normalized["uf"]),
                    EventPublicity.layer == str(normalized["camada"]),
                )
            ).first()

        if existing:
            changed = _apply_event_publicity_update(
                existing,
                normalized=normalized,
                event_id=event_id,
                source_file=filename,
                source_row_hash=source_row_hash,
            )
            if changed and existing.id is not None:
                upsert_updated += 1
                if not dry_run:
                    session.add(existing)
            seen_natural_keys.add(natural_key)
            continue

        upsert_inserted += 1
        seen_natural_keys.add(natural_key)
        if dry_run:
            continue
        created = EventPublicity(
            event_id=event_id,
            publicity_project_code=str(normalized["codigo_projeto"]),
            publicity_project_name=str(normalized["projeto"]),
            linked_at=normalized["data_vinculacao"],  # type: ignore[arg-type]
            medium=str(normalized["meio"]),
            vehicle=str(normalized["veiculo"]),
            uf=str(normalized["uf"]),
            uf_name=_string_or_none(normalized.get("uf_extenso")),
            municipality=_string_or_none(normalized.get("municipio")),
            layer=str(normalized["camada"]),
            source_file=filename,
            source_row_hash=source_row_hash,
        )
        session.add(created)
        session.flush()
        pending_new_final[natural_key] = created

    if not dry_run:
        session.commit()

    return PublicidadeImportReport(
        filename=filename,
        received_rows=received_rows,
        valid_rows=valid_rows,
        staged_inserted=staged_inserted,
        staged_skipped=staged_skipped,
        upsert_inserted=upsert_inserted,
        upsert_updated=upsert_updated,
        unresolved_event_id=unresolved_event_id,
        errors=errors,
    )


def _normalize_payload(raw_payload: dict[str, str]) -> tuple[dict[str, object], list[tuple[str, str, str | None]]]:
    normalized: dict[str, object] = {}
    errors: list[tuple[str, str, str | None]] = []

    for field_name, raw_value in raw_payload.items():
        value = normalize_publicidade_value(field_name, raw_value)
        if value is None and (raw_value or "").strip() and field_name == "data_vinculacao":
            errors.append((field_name, "Formato de data invalido. Use DD/MM/YYYY ou YYYY-MM-DD.", raw_value))
            continue
        if value is None:
            continue
        normalized[field_name] = value

    for field in PUBLICIDADE_DOMAIN_SPEC.fields:
        if not field.required:
            continue
        if normalized.get(field.name) is None:
            errors.append((field.name, "Campo obrigatorio ausente na linha.", None))

    for field_name in PUBLICIDADE_DOMAIN_SPEC.required_key_fields:
        if normalized.get(field_name) is None:
            errors.append((field_name, "Campo obrigatorio para chave natural.", None))

    return normalized, errors


def _append_row_errors(
    errors: list[PublicidadeImportError],
    *,
    row_errors: list[tuple[str, str, str | None]],
    row_number: int,
) -> None:
    if len(errors) >= MAX_ERROR_ROWS:
        return
    for field_name, message, value in row_errors:
        errors.append(
            PublicidadeImportError(
                line=row_number,
                field=field_name,
                message=message,
                value=value,
            )
        )
        if len(errors) >= MAX_ERROR_ROWS:
            return


def _staging_exists(session: Session, *, filename: str, source_row_hash: str) -> bool:
    return (
        session.exec(
            select(PublicityImportStaging.id).where(
                PublicityImportStaging.source_file == filename,
                PublicityImportStaging.source_row_hash == source_row_hash,
            )
        ).first()
        is not None
    )


def _resolve_event_id(session: Session, *, codigo_projeto: str) -> int | None:
    by_external_code = session.exec(
        select(Evento.id).where(Evento.external_project_code == codigo_projeto)
    ).first()
    if by_external_code:
        return int(by_external_code)

    alias = find_alias(
        session,
        domain=PUBLICIDADE_DOMAIN_SPEC.domain,
        field_name="codigo_projeto",
        source_value=codigo_projeto,
    )
    if not alias:
        return None

    if alias.canonical_ref_id:
        evento = session.get(Evento, int(alias.canonical_ref_id))
        if evento and evento.id:
            return int(evento.id)

    canonical_value = (alias.canonical_value or "").strip()
    if canonical_value:
        by_alias_code = session.exec(
            select(Evento.id).where(Evento.external_project_code == canonical_value)
        ).first()
        if by_alias_code:
            return int(by_alias_code)
    return None


def _natural_key(normalized: dict[str, object]) -> tuple[object, ...]:
    linked_at = normalized.get("data_vinculacao")
    assert isinstance(linked_at, date)
    return (
        str(normalized["codigo_projeto"]),
        linked_at.isoformat(),
        str(normalized["meio"]),
        str(normalized["veiculo"]),
        str(normalized["uf"]),
        str(normalized["camada"]),
    )


def _canonical_row_hash(normalized: dict[str, object]) -> str:
    canonical_payload = _json_ready_payload(normalized)
    raw = json.dumps(canonical_payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _json_ready_payload(normalized: dict[str, object]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in normalized.items():
        if isinstance(value, date):
            payload[key] = value.isoformat()
        else:
            payload[key] = value
    return payload


def _string_or_none(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _apply_event_publicity_update(
    current: EventPublicity,
    *,
    normalized: dict[str, object],
    event_id: int | None,
    source_file: str,
    source_row_hash: str,
) -> bool:
    changed = False
    updates: dict[str, object | None] = {
        "event_id": event_id,
        "publicity_project_name": str(normalized["projeto"]),
        "uf_name": _string_or_none(normalized.get("uf_extenso")),
        "municipality": _string_or_none(normalized.get("municipio")),
        "source_file": source_file,
        "source_row_hash": source_row_hash,
    }
    for attr, value in updates.items():
        if getattr(current, attr) != value:
            setattr(current, attr, value)
            changed = True
    return changed
