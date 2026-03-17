"""Reusable backend-only lead persistence helpers."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.models import Lead, LeadEventoSourceKind
from app.services.lead_event_service import ensure_lead_event, resolve_unique_evento_by_name
from app.utils.log_sanitize import sanitize_exception

logger = logging.getLogger(__name__)


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
) -> tuple[int, int, int, bool]:
    created = 0
    updated = 0
    skipped = 0
    has_errors = False
    new_objects: list[Lead] = []
    new_payloads: list[dict[str, object]] = []
    update_objects: list[tuple[Lead, dict[str, object]]] = []
    lead_cache: dict[str, Lead] = {}

    for item in batch:
        if not item:
            continue
        payload, _row_number = item
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

    try:
        if new_objects:
            session.add_all(new_objects)
            session.flush()
            for lead, payload in zip(new_objects, new_payloads, strict=False):
                _ensure_canonical_event_link(session, lead=lead, payload=payload)
            created += len(new_objects)
        if update_objects:
            session.add_all([lead for lead, _payload in update_objects])
            for lead, payload in update_objects:
                _ensure_canonical_event_link(session, lead=lead, payload=payload)
            updated += len(update_objects)
        session.commit()
        return created, updated, skipped, has_errors
    except Exception as exc:
        session.rollback()
        has_errors = True
        logger.warning(
            "Lead import bulk fallback activated detail=%s",
            sanitize_exception(exc),
        )

    for item in batch:
        if not item:
            continue
        payload, row_number = item
        key = build_dedupe_key(payload)
        existing = lead_cache.get(key) if key else None
        if existing is None:
            existing = find_existing_lead(session, payload)
            if existing and key:
                lead_cache[key] = existing
        if existing:
            merge_lead(existing, payload)
            session.add(existing)
            updated += 1
            continue

        lead = Lead(**payload)
        try:
            session.add(lead)
            session.flush()
            _ensure_canonical_event_link(session, lead=lead, payload=payload)
            created += 1
        except IntegrityError as exc:
            session.rollback()
            existing = find_existing_lead(session, payload)
            if not existing:
                skipped += 1
                has_errors = True
                logger.warning(
                    "Lead import error row=%s error=INTEGRITY_ERROR detail=%s",
                    row_number,
                    sanitize_exception(exc),
                )
                continue
            merge_lead(existing, payload)
            session.add(existing)
            _ensure_canonical_event_link(session, lead=existing, payload=payload)
            updated += 1
        except Exception as exc:
            session.rollback()
            skipped += 1
            has_errors = True
            logger.warning(
                "Lead import error row=%s error=UNKNOWN detail=%s",
                row_number,
                sanitize_exception(exc),
            )
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        has_errors = True
        logger.warning(
            "Lead import batch commit error detail=%s",
            sanitize_exception(exc),
        )
        return created, updated, skipped + sum(1 for item in batch if item), has_errors
    return created, updated, skipped, has_errors
