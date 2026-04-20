"""Reusable backend-only lead persistence helpers."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func as sql_func
from sqlmodel import Session, select

from app.models.models import Lead, LeadEvento, LeadEventoSourceKind
from app.modules.leads_publicidade.application.lead_merge_policy import merge_lead_payload_fill_missing
from app.services.lead_event_service import ensure_lead_event, resolve_unique_evento_by_name
from app.utils.log_sanitize import sanitize_exception

from .validators import format_validation_reasons, validate_normalized_lead_payload

logger = logging.getLogger(__name__)

TICKETING_DEDUPE_INDEX_NAMES = (
    "uq_lead_ticketing_dedupe_norm",
    "uq_lead_ticketing_dedupe",
)
TICKETING_DEDUPE_SQLITE_SIGNATURES = (
    "unique constraint failed: lead.email, lead.cpf, lead.evento_nome, lead.sessao",
)


def _ticketing_field_norm(value: object) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.strip()


def is_ticketing_dedupe_integrity_error(exc: BaseException) -> bool:
    """True when exc is a unique-violation on the ticketing dedupe index/constraint."""

    if not isinstance(exc, IntegrityError):
        return False
    orig = getattr(exc, "orig", None)
    if orig is not None and getattr(orig, "pgcode", None) == "23505":
        diag = getattr(orig, "diag", None)
        cname = getattr(diag, "constraint_name", None) if diag is not None else None
        if cname and any(n in cname for n in TICKETING_DEDUPE_INDEX_NAMES):
            return True
    raw = str(orig) if orig is not None else str(exc)
    lowered = raw.lower()
    if "unique" not in lowered and "duplicate" not in lowered:
        return False
    for name in TICKETING_DEDUPE_INDEX_NAMES:
        if name.lower() in lowered:
            return True
    return any(signature in lowered for signature in TICKETING_DEDUPE_SQLITE_SIGNATURES)


def find_lead_by_ticketing_dedupe_key(session: Session, payload: dict[str, object]) -> Lead | None:
    """Lookup using the same normalization as uq_lead_ticketing_dedupe_norm."""

    cpf_val = _ticketing_field_norm(payload.get("cpf"))
    if not cpf_val:
        return None
    email_n = _ticketing_field_norm(payload.get("email"))
    evento_n = _ticketing_field_norm(payload.get("evento_nome"))
    sessao_n = _ticketing_field_norm(payload.get("sessao"))

    stmt = (
        select(Lead)
        .where(Lead.cpf == cpf_val)
        .where(sql_func.coalesce(sql_func.trim(Lead.email), "") == email_n)
        .where(sql_func.coalesce(sql_func.trim(Lead.evento_nome), "") == evento_n)
        .where(sql_func.coalesce(sql_func.trim(Lead.sessao), "") == sessao_n)
    )
    return session.exec(stmt).first()


@dataclass(frozen=True)
class LeadPersistenceFailedRow:
    row_index: int
    reason: str


@dataclass(frozen=True)
class LeadPersistenceAppliedRow:
    row_index: int
    action: str
    lead_id: int | None


@dataclass(frozen=True)
class LeadBatchPersistenceResult:
    created: int = 0
    updated: int = 0
    applied_rows: list[LeadPersistenceAppliedRow] = field(default_factory=list)
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


@dataclass(frozen=True)
class LeadLookupContext:
    candidates: list[Lead]
    lead_ids_with_any_event_link: set[int]
    lead_ids_with_target_event_link: set[int]


def merge_lead_lookup_context(accumulator: LeadLookupContext, incoming: LeadLookupContext) -> None:
    """Acrescenta candidatos e conjuntos de evento sem duplicar `Lead.id` já presentes."""
    seen_ids: set[int] = {
        int(lead.id)
        for lead in accumulator.candidates
        if getattr(lead, "id", None) is not None
    }
    for lead in incoming.candidates:
        lid = getattr(lead, "id", None)
        if lid is not None:
            ilid = int(lid)
            if ilid in seen_ids:
                continue
            seen_ids.add(ilid)
        accumulator.candidates.append(lead)
    accumulator.lead_ids_with_any_event_link.update(incoming.lead_ids_with_any_event_link)
    accumulator.lead_ids_with_target_event_link.update(incoming.lead_ids_with_target_event_link)


def build_dedupe_key(
    payload: dict[str, object],
    *,
    canonical_evento_id: int | None = None,
) -> str | None:
    email = payload.get("email") or ""
    cpf = payload.get("cpf") or ""
    if not email and not cpf:
        return None
    evento_identity = (
        f"evento_id:{canonical_evento_id}"
        if canonical_evento_id is not None
        else payload.get("evento_nome") or ""
    )
    sessao = payload.get("sessao") or ""
    return f"{email}|{cpf}|{evento_identity}|{sessao}"


def _build_contact_filters(payload: dict[str, object]) -> list[object]:
    email = payload.get("email")
    cpf = payload.get("cpf")
    if not email and not cpf:
        return []

    filters = []
    if email and cpf:
        filters.append(Lead.email == email)
        filters.append(Lead.cpf == cpf)
    elif email:
        filters.append(Lead.email == email)
    else:
        filters.append(Lead.cpf == cpf)
    return filters


def _contact_matches_payload(lead: Lead, payload: dict[str, object]) -> bool:
    email = payload.get("email")
    cpf = payload.get("cpf")
    if not email and not cpf:
        return False

    lead_email = getattr(lead, "email", None)
    lead_cpf = getattr(lead, "cpf", None)
    if email and lead_email == email:
        return True
    if cpf and lead_cpf == cpf:
        return True
    return False


def _legacy_matches_payload(lead: Lead, payload: dict[str, object]) -> bool:
    if not _contact_matches_payload(lead, payload):
        return False

    evento_nome = payload.get("evento_nome")
    if evento_nome is not None and getattr(lead, "evento_nome", None) != evento_nome:
        return False

    sessao = payload.get("sessao")
    if sessao is not None and getattr(lead, "sessao", None) != sessao:
        return False

    return True


def _collect_lookup_terms(batch: list[tuple[dict[str, object], int]]) -> dict[str, set[object]]:
    terms: dict[str, set[object]] = {
        "email": set(),
        "cpf": set(),
        "evento_nome": set(),
        "sessao": set(),
    }
    for payload, _row_number in batch:
        email = payload.get("email")
        cpf = payload.get("cpf")
        evento_nome = payload.get("evento_nome")
        sessao = payload.get("sessao")
        if email:
            terms["email"].add(email)
        if cpf:
            terms["cpf"].add(cpf)
        if evento_nome is not None:
            terms["evento_nome"].add(evento_nome)
        if sessao is not None:
            terms["sessao"].add(sessao)
    return terms


def _load_lead_lookup_context(
    session: Session,
    batch: list[tuple[dict[str, object], int]],
    *,
    canonical_evento_id: int | None = None,
) -> LeadLookupContext:
    terms = _collect_lookup_terms(batch)
    filters = []
    if terms["email"]:
        filters.append(Lead.email.in_(sorted(str(value) for value in terms["email"])))
    if terms["cpf"]:
        filters.append(Lead.cpf.in_(sorted(str(value) for value in terms["cpf"])))
    if terms["evento_nome"]:
        filters.append(Lead.evento_nome.in_(sorted(str(value) for value in terms["evento_nome"])))
    if terms["sessao"]:
        filters.append(Lead.sessao.in_(sorted(str(value) for value in terms["sessao"])))

    if not filters:
        return LeadLookupContext([], set(), set())

    candidates = list(session.exec(select(Lead).where(or_(*filters)).order_by(Lead.id.asc())).all())
    candidate_ids = [int(lead.id) for lead in candidates if lead.id is not None]

    lead_ids_with_any_event_link: set[int] = set()
    lead_ids_with_target_event_link: set[int] = set()
    if candidate_ids:
        lead_ids_with_any_event_link = {
            int(lead_id)
            for lead_id in session.exec(
                select(LeadEvento.lead_id).where(LeadEvento.lead_id.in_(candidate_ids))
            ).all()
            if lead_id is not None
        }
        if canonical_evento_id is not None:
            lead_ids_with_target_event_link = {
                int(lead_id)
                for lead_id in session.exec(
                    select(LeadEvento.lead_id).where(
                        LeadEvento.lead_id.in_(candidate_ids),
                        LeadEvento.evento_id == canonical_evento_id,
                    )
                ).all()
                if lead_id is not None
            }

    return LeadLookupContext(
        candidates=candidates,
        lead_ids_with_any_event_link=lead_ids_with_any_event_link,
        lead_ids_with_target_event_link=lead_ids_with_target_event_link,
    )


def find_existing_lead_from_lookup(
    payload: dict[str, object],
    lookup: LeadLookupContext,
    *,
    canonical_evento_id: int | None = None,
) -> Lead | None:
    if not _build_contact_filters(payload):
        return None

    if canonical_evento_id is not None:
        for candidate in lookup.candidates:
            if candidate.id is None:
                continue
            if candidate.id in lookup.lead_ids_with_target_event_link and _contact_matches_payload(
                candidate, payload
            ):
                return candidate

        for candidate in lookup.candidates:
            if candidate.id is None:
                continue
            if candidate.id in lookup.lead_ids_with_any_event_link:
                continue
            if _legacy_matches_payload(candidate, payload):
                return candidate
        return None

    for candidate in lookup.candidates:
        if _legacy_matches_payload(candidate, payload):
            return candidate
    return None


def _find_lead_by_canonical_event(
    session: Session,
    payload: dict[str, object],
    *,
    canonical_evento_id: int,
) -> Lead | None:
    contact_filters = _build_contact_filters(payload)
    if not contact_filters:
        return None

    stmt = (
        select(Lead)
        .join(LeadEvento, LeadEvento.lead_id == Lead.id)
        .where(LeadEvento.evento_id == canonical_evento_id)
    )
    for filter_ in contact_filters:
        stmt = stmt.where(filter_)

    sessao = payload.get("sessao")
    if sessao is not None:
        stmt = stmt.where(Lead.sessao == sessao)

    return session.exec(stmt).first()


def _find_legacy_lead_candidates(session: Session, payload: dict[str, object]) -> list[Lead]:
    contact_filters = _build_contact_filters(payload)
    if not contact_filters:
        return []

    stmt = select(Lead)
    for filter_ in contact_filters:
        stmt = stmt.where(filter_)

    evento_nome = payload.get("evento_nome")
    sessao = payload.get("sessao")
    if evento_nome is not None:
        stmt = stmt.where(Lead.evento_nome == evento_nome)
    if sessao is not None:
        stmt = stmt.where(Lead.sessao == sessao)

    return list(session.exec(stmt).all())


def _lead_has_any_canonical_event_link(session: Session, lead_id: int | None) -> bool:
    if lead_id is None:
        return False
    return (
        session.exec(select(LeadEvento.id).where(LeadEvento.lead_id == lead_id)).first() is not None
    )


def find_existing_lead(
    session: Session,
    payload: dict[str, object],
    *,
    canonical_evento_id: int | None = None,
) -> Lead | None:
    if not _build_contact_filters(payload):
        return None

    if canonical_evento_id is not None:
        lead = _find_lead_by_canonical_event(
            session,
            payload,
            canonical_evento_id=canonical_evento_id,
        )
        if lead is not None:
            return lead

    candidates = _find_legacy_lead_candidates(session, payload)
    if canonical_evento_id is None:
        return candidates[0] if candidates else None

    for candidate in candidates:
        if not _lead_has_any_canonical_event_link(session, candidate.id):
            return candidate
    return None


def merge_lead(existing: Lead, payload: dict[str, object]) -> None:
    merge_lead_payload_fill_missing(existing, payload)


def _ensure_canonical_event_link(
    session: Session,
    *,
    lead: Lead,
    payload: dict[str, object],
    canonical_evento_id: int | None = None,
) -> None:
    if lead.id is None:
        return
    if canonical_evento_id is not None:
        ensure_lead_event(
            session,
            lead_id=lead.id,
            evento_id=canonical_evento_id,
            source_kind=LeadEventoSourceKind.EVENT_DIRECT,
        )
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
    canonical_evento_id: int | None = None,
    *,
    auto_commit: bool = True,
) -> LeadBatchPersistenceResult:
    effective_items: list[tuple[dict[str, object], int]] = [
        item for item in batch if item is not None
    ]
    if not effective_items:
        return LeadBatchPersistenceResult()

    effective_items, validation_failed_rows = _filter_invalid_rows(effective_items)
    if not effective_items:
        return LeadBatchPersistenceResult(failed_rows=validation_failed_rows)

    _ensure_outer_transaction(session)
    lookup_context = _load_lead_lookup_context(
        session,
        effective_items,
        canonical_evento_id=canonical_evento_id,
    )

    try:
        with session.begin_nested():
            bulk_result = _persist_lead_batch_bulk(
                session,
                effective_items,
                canonical_evento_id=canonical_evento_id,
                lookup_context=lookup_context,
            )
    except Exception as exc:
        logger.warning(
            "Lead import bulk fallback activated detail=%s",
            sanitize_exception(exc),
        )
        result = _persist_lead_batch_row_by_row(
            session,
            effective_items,
            canonical_evento_id=canonical_evento_id,
            lookup_context=lookup_context,
        )
        result = _ensure_attempted_rows_are_reported(result, effective_items)
        if auto_commit:
            result = _commit_or_failure(session, result, effective_items)
        return _with_failed_rows(result, validation_failed_rows)

    result = bulk_result
    result = _ensure_attempted_rows_are_reported(result, effective_items)
    if auto_commit:
        result = _commit_or_failure(session, result, effective_items)
    return _with_failed_rows(result, validation_failed_rows)


def _filter_invalid_rows(
    batch: list[tuple[dict[str, object], int]],
) -> tuple[list[tuple[dict[str, object], int]], list[LeadPersistenceFailedRow]]:
    valid_items: list[tuple[dict[str, object], int]] = []
    failed_rows: list[LeadPersistenceFailedRow] = []

    for payload, row_number in batch:
        reasons = validate_normalized_lead_payload(payload)
        if reasons:
            failed_rows.append(
                LeadPersistenceFailedRow(
                    row_index=row_number,
                    reason=format_validation_reasons(reasons),
                )
            )
            continue
        valid_items.append((payload, row_number))

    return valid_items, failed_rows


def _with_failed_rows(
    result: LeadBatchPersistenceResult,
    failed_rows: list[LeadPersistenceFailedRow],
) -> LeadBatchPersistenceResult:
    if not failed_rows:
        return result
    return LeadBatchPersistenceResult(
        created=result.created,
        updated=result.updated,
        applied_rows=result.applied_rows,
        failed_rows=sorted(
            [*result.failed_rows, *failed_rows],
            key=lambda row: row.row_index,
        ),
        skipped_rows=result.skipped_rows,
    )


def _ensure_outer_transaction(session: Session) -> None:
    bind = session.get_bind()
    if bind.dialect.name != "sqlite":
        if not session.in_transaction():
            session.begin()
        return

    connection = session.connection()
    driver_connection = getattr(connection.connection, "driver_connection", None)
    if driver_connection is not None and not getattr(driver_connection, "in_transaction", True):
        connection.exec_driver_sql("BEGIN")


def _persist_lead_batch_bulk(
    session: Session,
    batch: list[tuple[dict[str, object], int]],
    *,
    canonical_evento_id: int | None = None,
    lookup_context: LeadLookupContext | None = None,
) -> LeadBatchPersistenceResult:
    created = 0
    updated = 0
    applied_rows: list[LeadPersistenceAppliedRow] = []
    new_objects: list[tuple[Lead, dict[str, object], int]] = []
    update_objects: list[tuple[Lead, dict[str, object], int]] = []
    lead_cache: dict[str, Lead] = {}

    for payload, row_number in batch:
        key = build_dedupe_key(payload, canonical_evento_id=canonical_evento_id)
        existing = lead_cache.get(key) if key else None
        if existing is None:
            if lookup_context is not None:
                existing = find_existing_lead_from_lookup(
                    payload,
                    lookup_context,
                    canonical_evento_id=canonical_evento_id,
                )
            else:
                existing = find_existing_lead(
                    session,
                    payload,
                    canonical_evento_id=canonical_evento_id,
                )
            if existing and key:
                lead_cache[key] = existing
        if existing:
            merge_lead(existing, payload)
            update_objects.append((existing, payload, row_number))
            continue
        new_objects.append((Lead(**payload), payload, row_number))

    if new_objects:
        session.add_all([lead for lead, _payload, _row_number in new_objects])
        session.flush()
        for lead, payload, row_number in new_objects:
            _ensure_canonical_event_link(
                session,
                lead=lead,
                payload=payload,
                canonical_evento_id=canonical_evento_id,
            )
            applied_rows.append(
                LeadPersistenceAppliedRow(
                    row_index=row_number,
                    action="created",
                    lead_id=int(lead.id) if lead.id is not None else None,
                )
            )
        created += len(new_objects)
    if update_objects:
        session.add_all([lead for lead, _payload, _row_number in update_objects])
        session.flush()
        for lead, payload, row_number in update_objects:
            _ensure_canonical_event_link(
                session,
                lead=lead,
                payload=payload,
                canonical_evento_id=canonical_evento_id,
            )
            applied_rows.append(
                LeadPersistenceAppliedRow(
                    row_index=row_number,
                    action="updated",
                    lead_id=int(lead.id) if lead.id is not None else None,
                )
            )
        updated += len(update_objects)
    return LeadBatchPersistenceResult(
        created=created,
        updated=updated,
        applied_rows=sorted(applied_rows, key=lambda row: row.row_index),
    )


def _persist_lead_batch_row_by_row(
    session: Session,
    batch: list[tuple[dict[str, object], int]],
    *,
    canonical_evento_id: int | None = None,
    lookup_context: LeadLookupContext | None = None,
) -> LeadBatchPersistenceResult:
    created = 0
    updated = 0
    applied_rows: list[LeadPersistenceAppliedRow] = []
    failed_rows: list[LeadPersistenceFailedRow] = []

    for payload, row_number in batch:
        try:
            with session.begin_nested():
                action, lead_id = _persist_single_lead_row(
                    session,
                    payload,
                    canonical_evento_id=canonical_evento_id,
                    lookup_context=lookup_context,
                )
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
        applied_rows.append(
            LeadPersistenceAppliedRow(
                row_index=row_number,
                action=action,
                lead_id=lead_id,
            )
        )

    return LeadBatchPersistenceResult(
        created=created,
        updated=updated,
        applied_rows=applied_rows,
        failed_rows=failed_rows,
    )


def _persist_single_lead_row(
    session: Session,
    payload: dict[str, object],
    *,
    canonical_evento_id: int | None = None,
    lookup_context: LeadLookupContext | None = None,
) -> tuple[str, int | None]:
    if lookup_context is not None:
        existing = find_existing_lead_from_lookup(
            payload,
            lookup_context,
            canonical_evento_id=canonical_evento_id,
        )
    else:
        existing = find_existing_lead(
            session,
            payload,
            canonical_evento_id=canonical_evento_id,
        )
    if existing:
        merge_lead(existing, payload)
        session.add(existing)
        session.flush()
        _ensure_canonical_event_link(
            session,
            lead=existing,
            payload=payload,
            canonical_evento_id=canonical_evento_id,
        )
        return "updated", int(existing.id) if existing.id is not None else None

    try:
        with session.begin_nested():
            lead = Lead(**payload)
            session.add(lead)
            session.flush()
    except IntegrityError as exc:
        if not is_ticketing_dedupe_integrity_error(exc):
            raise
        winner = find_lead_by_ticketing_dedupe_key(session, payload)
        if winner is None:
            logger.warning(
                "Ticketing dedupe conflict without resolvable row cpf=%s",
                str(payload.get("cpf")),
            )
            raise
        merge_lead(winner, payload)
        session.add(winner)
        session.flush()
        _ensure_canonical_event_link(
            session,
            lead=winner,
            payload=payload,
            canonical_evento_id=canonical_evento_id,
        )
        return "updated", int(winner.id) if winner.id is not None else None
    _ensure_canonical_event_link(
        session,
        lead=lead,
        payload=payload,
        canonical_evento_id=canonical_evento_id,
    )
    return "created", int(lead.id) if lead.id is not None else None


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
