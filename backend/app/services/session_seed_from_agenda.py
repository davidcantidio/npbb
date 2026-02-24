"""Seed/update canonical `event_sessions` from master agenda input.

This module applies an idempotent upsert routine over `event_sessions` using
the natural key:
`event_id + session_start_at + session_type`.

It also registers an ingestion run for agenda updates so changes remain
traceable in ETL audit logs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
import sys
from typing import Any, Literal

from sqlmodel import Session, select

from app.models.etl_registry import IngestionStatus
from app.models.events_sessions import EventSession, EventSessionType
from app.services.etl_registry_service import (
    finish_ingestion_run,
    register_source_from_path,
    start_ingestion_run,
)

try:  # pragma: no cover - import style depends on process cwd
    from core.sessions import SessionType
    from etl.transform.agenda_loader import AgendaMaster
except ModuleNotFoundError:  # pragma: no cover
    ROOT_DIR = Path(__file__).resolve().parents[3]
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))
    from core.sessions import SessionType
    from etl.transform.agenda_loader import AgendaMaster


class SessionSeedFromAgendaError(ValueError):
    """Raised when agenda seeding finds invalid or ambiguous DB state."""


@dataclass(frozen=True)
class SessionFieldChange:
    """One field-level change captured during upsert diff."""

    field: str
    old_value: str | None
    new_value: str | None


@dataclass(frozen=True)
class SessionSeedDiff:
    """Diff entry for one natural-key agenda upsert operation."""

    action: Literal["created", "updated", "unchanged"]
    natural_key: str
    session_id: int
    session_key: str
    changes: tuple[SessionFieldChange, ...] = ()


@dataclass(frozen=True)
class SessionSeedSummary:
    """Summary of one agenda seed run."""

    source_id: str
    ingestion_id: int
    created_count: int
    updated_count: int
    unchanged_count: int
    diffs: tuple[SessionSeedDiff, ...]


def _to_event_session_type(value: SessionType) -> EventSessionType:
    """Map core session type into canonical DB enum domain."""

    if value == SessionType.DIURNO_GRATUITO:
        return EventSessionType.DIURNO_GRATUITO
    if value == SessionType.NOTURNO_SHOW:
        return EventSessionType.NOTURNO_SHOW
    return EventSessionType.OUTRO


def _session_key_suffix(session_type: EventSessionType) -> str:
    """Return stable key suffix by session type."""

    if session_type == EventSessionType.NOTURNO_SHOW:
        return "SHOW"
    if session_type == EventSessionType.DIURNO_GRATUITO:
        return "DIURNO"
    return "OUTRO"


def _default_session_key(
    *,
    event_id: int,
    start_at: datetime,
    session_type: EventSessionType,
) -> str:
    """Build deterministic session key when agenda entry has no explicit key."""

    return (
        f"E{event_id}_"
        f"{start_at.strftime('%Y%m%dT%H%M%S')}_"
        f"{_session_key_suffix(session_type)}"
    )


def _natural_key_repr(
    *,
    event_id: int,
    start_at: datetime,
    session_type: EventSessionType,
) -> str:
    """Return stable string representation of session natural key."""

    return f"{event_id}|{start_at.isoformat()}|{session_type.value}"


def _audit_notes(
    *,
    actor: str,
    agenda_path: Path,
    summary: SessionSeedSummary,
) -> str:
    """Build ingestion audit notes with actor and diff payload."""

    payload: dict[str, Any] = {
        "actor": actor,
        "agenda_path": str(agenda_path),
        "created": summary.created_count,
        "updated": summary.updated_count,
        "unchanged": summary.unchanged_count,
        "diff": [
            {
                "action": item.action,
                "natural_key": item.natural_key,
                "session_id": item.session_id,
                "session_key": item.session_key,
                "changes": [
                    {
                        "field": change.field,
                        "old": change.old_value,
                        "new": change.new_value,
                    }
                    for change in item.changes
                ],
            }
            for item in summary.diffs
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def _find_by_natural_key(
    session: Session,
    *,
    event_id: int,
    start_at: datetime,
    session_type: EventSessionType,
) -> EventSession | None:
    """Find one session row using natural key and enforce non-ambiguity."""

    rows = session.exec(
        select(EventSession).where(
            EventSession.event_id == event_id,
            EventSession.session_start_at == start_at,
            EventSession.session_type == session_type,
        )
    ).all()
    if not rows:
        return None
    if len(rows) > 1:
        key_repr = _natural_key_repr(
            event_id=event_id,
            start_at=start_at,
            session_type=session_type,
        )
        raise SessionSeedFromAgendaError(
            "Chave natural ambigua em event_sessions. "
            f"Como corrigir: manter somente uma linha para ({key_repr})."
        )
    return rows[0]


def _apply_updates_from_agenda(
    row: EventSession,
    *,
    session_date: date,
    session_name: str,
    session_key: str,
) -> tuple[SessionFieldChange, ...]:
    """Apply agenda values on existing row and return field-level diff."""

    changes: list[SessionFieldChange] = []

    if row.session_date != session_date:
        changes.append(
            SessionFieldChange(
                field="session_date",
                old_value=row.session_date.isoformat(),
                new_value=session_date.isoformat(),
            )
        )
        row.session_date = session_date

    if row.session_name != session_name:
        changes.append(
            SessionFieldChange(
                field="session_name",
                old_value=row.session_name,
                new_value=session_name,
            )
        )
        row.session_name = session_name

    if row.session_key != session_key:
        changes.append(
            SessionFieldChange(
                field="session_key",
                old_value=row.session_key,
                new_value=session_key,
            )
        )
        row.session_key = session_key

    return tuple(changes)


def upsert_event_sessions_from_agenda(
    session: Session,
    agenda: AgendaMaster,
    *,
    source_id: str = "SRC_CONFIG_AGENDA_MASTER",
    extractor_name: str = "seed_event_sessions_from_agenda",
    actor: str = "system",
) -> SessionSeedSummary:
    """Upsert `event_sessions` from agenda master using natural-key idempotency.

    Natural key:
        `event_id + session_start_at + session_type`

    Update rules for existing rows:
    - `session_name` is overwritten from agenda.
    - `session_date` is overwritten from agenda (must match `start_at.date()`).
    - `session_key` is updated to agenda value when provided, otherwise to the
      deterministic key generated by this service.

    Args:
        session: Open SQLModel DB session.
        agenda: Validated agenda master contract.
        source_id: Registry source identifier for agenda file.
        extractor_name: Registry extractor/load step label.
        actor: Audit actor name written to ingestion notes.

    Returns:
        `SessionSeedSummary` with counts and full diff payload.

    Raises:
        SessionSeedFromAgendaError: If DB has ambiguous natural-key rows.
        ValueError: If registry operations fail.
    """

    source = register_source_from_path(session, source_id, agenda.source_path)
    run = start_ingestion_run(session, source.source_id, extractor_name)
    created_count = 0
    updated_count = 0
    unchanged_count = 0
    diffs: list[SessionSeedDiff] = []

    try:
        for agenda_session in agenda.sessions:
            session_type = _to_event_session_type(agenda_session.session_type)
            session_key = (
                agenda_session.session_key
                or _default_session_key(
                    event_id=agenda_session.event_id,
                    start_at=agenda_session.start_at,
                    session_type=session_type,
                )
            )
            natural_key = _natural_key_repr(
                event_id=agenda_session.event_id,
                start_at=agenda_session.start_at,
                session_type=session_type,
            )

            existing = _find_by_natural_key(
                session,
                event_id=agenda_session.event_id,
                start_at=agenda_session.start_at,
                session_type=session_type,
            )
            if existing is None:
                row = EventSession(
                    event_id=agenda_session.event_id,
                    session_key=session_key,
                    session_name=agenda_session.name,
                    session_type=session_type,
                    session_date=agenda_session.session_date,
                    session_start_at=agenda_session.start_at,
                )
                session.add(row)
                session.flush()
                created_count += 1
                diffs.append(
                    SessionSeedDiff(
                        action="created",
                        natural_key=natural_key,
                        session_id=int(row.id),
                        session_key=row.session_key,
                    )
                )
                continue

            changes = _apply_updates_from_agenda(
                existing,
                session_date=agenda_session.session_date,
                session_name=agenda_session.name,
                session_key=session_key,
            )
            session.add(existing)
            session.flush()

            if changes:
                updated_count += 1
                diffs.append(
                    SessionSeedDiff(
                        action="updated",
                        natural_key=natural_key,
                        session_id=int(existing.id),
                        session_key=existing.session_key,
                        changes=changes,
                    )
                )
            else:
                unchanged_count += 1
                diffs.append(
                    SessionSeedDiff(
                        action="unchanged",
                        natural_key=natural_key,
                        session_id=int(existing.id),
                        session_key=existing.session_key,
                    )
                )

        session.commit()
        summary = SessionSeedSummary(
            source_id=source.source_id,
            ingestion_id=int(run.id),
            created_count=created_count,
            updated_count=updated_count,
            unchanged_count=unchanged_count,
            diffs=tuple(diffs),
        )
        finish_ingestion_run(
            session,
            ingestion_id=run.id,
            status=IngestionStatus.SUCCESS,
            notes=_audit_notes(actor=actor, agenda_path=agenda.source_path, summary=summary),
        )
        return summary
    except Exception as exc:
        session.rollback()
        finish_ingestion_run(
            session,
            ingestion_id=run.id,
            status=IngestionStatus.FAILED,
            notes=(
                "Falha ao aplicar agenda master em event_sessions. "
                f"actor={actor}; agenda_path={agenda.source_path}; erro={exc}"
            ),
        )
        raise
