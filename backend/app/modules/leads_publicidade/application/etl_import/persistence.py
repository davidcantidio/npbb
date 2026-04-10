"""Reusable backend-only lead persistence helpers."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from sqlmodel import Session, select

from app.models.models import Lead, LeadEventoSourceKind
from app.services.lead_event_service import ensure_lead_event, resolve_unique_evento_by_name
from app.utils.log_sanitize import sanitize_exception

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LeadPersistenceFailedRow:
    row_index: int
    reason: str


@dataclass(frozen=True)
class LeadBatchPersistenceResult:
    created: int = 0
    updated: int = 0
    failed_rows: list[LeadPersistenceFailedRow] = field(default_factory=list)
    skipped_rows: list[Any] = field(default_factory=list)

    @property
    def imported_count(self) -> int:
        return self.created + self.updated

    @property
    def skipped(self) -> int:
        return len(self.failed_rows) + len(self.skipped_rows)

    @property
    def has_errors(self) -> bool:
        return bool(self.failed_rows)

    def __iter__(self) -> Iterator[int | bool]:
        yield self.created
        yield self.updated
        yield self.skipped
        yield self.has_errors


def build_dedupe_key(payload: dict[str, object]) -> str | None:
    email = payload.get("email") or ""
    cpf = payload.get("cpf") or ""
    if not email and not cpf:
        return None
    evento_nome = payload.get("evento_nome") or ""
    sessao = payload.get("sessao") or ""
    return f"{email}|{cpf}|{evento_nome}|{sessao}"


def find_existing_lead(session: Session, payload: dict[str, object]) -> Lead | None:
    email = payload.get("email")
    cpf = payload.get("cpf")
    if not email and not cpf:
        return None

    filters = []
    if email and cpf:
        filters.append(Lead.email == email)
        filters.append(Lead.cpf == cpf)
    elif email:
        filters.append(Lead.email == email)
    else:
        filters.append(Lead.cpf == cpf)

    evento_nome = payload.get("evento_nome")
    sessao = payload.get("sessao")
    if evento_nome is not None:
        filters.append(Lead.evento_nome == evento_nome)
    if sessao is not None:
        filters.append(Lead.sessao == sessao)

    return session.exec(select(Lead).where(*filters)).first()


def merge_lead(existing: Lead, payload: dict[str, object]) -> None:
    for key, value in payload.items():
        if value is None:
            continue
        if key in {"email", "cpf"}:
            if getattr(existing, key):
                continue
            setattr(existing, key, value)
            continue
        if key == "fonte_origem":
            if getattr(existing, key):
                continue
            setattr(existing, key, value)
            continue
        setattr(existing, key, value)


def _ensure_canonical_event_link(
    session: Session,
    *,
    lead: Lead,
    payload: dict[str, object],
) -> None:
    if lead.id is None:
        return
    resolution = resolve_unique_evento_by_name(
        session,
        str(payload.get("evento_nome") or ""),
    )
    if resolution.status != "resolved" or resolution.evento_id is None:
        return
    ensure_lead_event(
        session,
        lead_id=lead.id,
        evento_id=resolution.evento_id,
        source_kind=LeadEventoSourceKind.EVENT_NAME_BACKFILL,
    )


def persist_lead_batch(
    session: Session,
    batch: list[tuple[dict[str, object], int] | None],
) -> LeadBatchPersistenceResult:
    effective_items: list[tuple[dict[str, object], int]] = [
        item for item in batch if item is not None
    ]
    if not effective_items:
        return LeadBatchPersistenceResult()

    _ensure_outer_transaction(session)

    try:
        with session.begin_nested():
            created, updated = _persist_lead_batch_bulk(session, effective_items)
    except Exception as exc:
        logger.warning(
            "Lead import bulk fallback activated detail=%s",
            sanitize_exception(exc),
        )
        result = _persist_lead_batch_row_by_row(session, effective_items)
        result = _ensure_attempted_rows_are_reported(result, effective_items)
        return _commit_or_failure(session, result, effective_items)

    result = LeadBatchPersistenceResult(created=created, updated=updated)
    result = _ensure_attempted_rows_are_reported(result, effective_items)
    return _commit_or_failure(session, result, effective_items)


def _ensure_outer_transaction(session: Session) -> None:
    if not session.in_transaction():
        session.begin()


def _persist_lead_batch_bulk(
    session: Session,
    batch: list[tuple[dict[str, object], int]],
) -> tuple[int, int]:
    created = 0
    updated = 0
    new_objects: list[Lead] = []
    new_payloads: list[dict[str, object]] = []
    update_objects: list[tuple[Lead, dict[str, object]]] = []
    lead_cache: dict[str, Lead] = {}

    for payload, _row_number in batch:
        key = build_dedupe_key(payload)
        existing = lead_cache.get(key) if key else None
        if existing is None:
            existing = find_existing_lead(session, payload)
            if existing and key:
                lead_cache[key] = existing
        if existing:
            merge_lead(existing, payload)
            update_objects.append((existing, payload))
            continue
        new_objects.append(Lead(**payload))
        new_payloads.append(payload)

    if new_objects:
        session.add_all(new_objects)
        session.flush()
        for lead, payload in zip(new_objects, new_payloads, strict=False):
            _ensure_canonical_event_link(session, lead=lead, payload=payload)
        created += len(new_objects)
    if update_objects:
        session.add_all([lead for lead, _payload in update_objects])
        session.flush()
        for lead, payload in update_objects:
            _ensure_canonical_event_link(session, lead=lead, payload=payload)
        updated += len(update_objects)
    return created, updated


def _persist_lead_batch_row_by_row(
    session: Session,
    batch: list[tuple[dict[str, object], int]],
) -> LeadBatchPersistenceResult:
    created = 0
    updated = 0
    failed_rows: list[LeadPersistenceFailedRow] = []

    for payload, row_number in batch:
        try:
            with session.begin_nested():
                action = _persist_single_lead_row(session, payload)
        except Exception as exc:
            reason = sanitize_exception(exc)
            failed_rows.append(LeadPersistenceFailedRow(row_index=row_number, reason=reason))
            logger.warning(
                "Lead import error row=%s detail=%s",
                row_number,
                reason,
            )
            continue
        if action == "created":
            created += 1
        else:
            updated += 1

    return LeadBatchPersistenceResult(
        created=created,
        updated=updated,
        failed_rows=failed_rows,
    )


def _persist_single_lead_row(session: Session, payload: dict[str, object]) -> str:
    existing = find_existing_lead(session, payload)
    if existing:
        merge_lead(existing, payload)
        session.add(existing)
        session.flush()
        _ensure_canonical_event_link(session, lead=existing, payload=payload)
        return "updated"

    lead = Lead(**payload)
    session.add(lead)
    session.flush()
    _ensure_canonical_event_link(session, lead=lead, payload=payload)
    return "created"


def _commit_or_failure(
    session: Session,
    result: LeadBatchPersistenceResult,
    attempted_rows: list[tuple[dict[str, object], int]],
) -> LeadBatchPersistenceResult:
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        reason = sanitize_exception(exc)
        logger.warning(
            "Lead import batch commit error detail=%s",
            reason,
        )
        return _failure_result_for_all_rows(attempted_rows, reason)
    return result


def _ensure_attempted_rows_are_reported(
    result: LeadBatchPersistenceResult,
    attempted_rows: list[tuple[dict[str, object], int]],
) -> LeadBatchPersistenceResult:
    if result.imported_count > 0 or result.failed_rows or not attempted_rows:
        return result
    return _failure_result_for_all_rows(attempted_rows, "No rows were persisted.")


def _failure_result_for_all_rows(
    attempted_rows: list[tuple[dict[str, object], int]],
    reason: str,
) -> LeadBatchPersistenceResult:
    return LeadBatchPersistenceResult(
        failed_rows=[
            LeadPersistenceFailedRow(row_index=row_number, reason=reason)
            for _payload, row_number in attempted_rows
        ]
    )
