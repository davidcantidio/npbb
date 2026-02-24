"""Master agenda loader for TMJ session coverage control.

This module loads and validates the controlled master agenda input used to
define expected sessions (daytime free vs night show), preventing per-day
omissions in downstream coverage checks.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from core.sessions import SessionType, coerce_session_type


DEFAULT_AGENDA_MASTER_PATH = Path(__file__).resolve().parent / "config" / "agenda_master.yml"
_SUPPORTED_SUFFIXES = {".yml", ".yaml", ".csv"}
_ALLOWED_MASTER_TYPES = {
    SessionType.DIURNO_GRATUITO,
    SessionType.NOTURNO_SHOW,
}


class AgendaMasterError(ValueError):
    """Raised when master agenda format/content is invalid."""


@dataclass(frozen=True)
class AgendaSession:
    """Validated master-agenda session entry.

    Args:
        event_id: Event identifier.
        session_date: Session date.
        start_at: Session start datetime.
        session_type: Controlled session type (`diurno_gratuito` or `noturno_show`).
        name: Human-readable session name.
        session_key: Optional stable key for deterministic references.
    """

    event_id: int
    session_date: date
    start_at: datetime
    session_type: SessionType
    name: str
    session_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize one session entry to JSON-friendly dictionary."""

        payload: dict[str, Any] = {
            "event_id": self.event_id,
            "session_date": self.session_date.isoformat(),
            "start_at": self.start_at.isoformat(),
            "type": self.session_type.value,
            "name": self.name,
        }
        if self.session_key:
            payload["session_key"] = self.session_key
        return payload


@dataclass(frozen=True)
class AgendaMaster:
    """Validated master agenda contract.

    Args:
        version: Agenda schema/content version.
        sessions: Validated session entries.
        source_path: File path used to load this agenda.
    """

    version: int
    sessions: tuple[AgendaSession, ...]
    source_path: Path

    def to_dict(self) -> dict[str, Any]:
        """Serialize master agenda to JSON-friendly dictionary."""

        return {
            "version": self.version,
            "source_path": str(self.source_path),
            "sessions": [session.to_dict() for session in self.sessions],
        }


def _as_mapping(value: Any, *, field: str) -> Mapping[str, Any]:
    """Ensure one value is a mapping node."""

    if isinstance(value, Mapping):
        return value
    raise AgendaMasterError(
        f"{field} invalido: esperado objeto. Como corrigir: usar chave: valor."
    )


def _parse_version(value: Any, *, field: str, default: int = 1) -> int:
    """Parse positive integer version field."""

    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AgendaMasterError(
            f"{field} invalido: esperado inteiro positivo."
        ) from exc
    if parsed <= 0:
        raise AgendaMasterError(
            f"{field} invalido: esperado inteiro positivo."
        )
    return parsed


def _require_non_empty_text(mapping: Mapping[str, Any], keys: Sequence[str], *, field: str) -> str:
    """Read one required text field using aliases."""

    for key in keys:
        value = mapping.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    aliases = ", ".join(keys)
    raise AgendaMasterError(
        f"{field} ausente/vazio. Como corrigir: informar campo ({aliases})."
    )


def _parse_event_id(mapping: Mapping[str, Any], *, field: str) -> int:
    """Parse one positive event_id from entry mapping."""

    raw = mapping.get("event_id")
    if raw is None:
        raise AgendaMasterError(
            f"{field}.event_id ausente. Como corrigir: informar inteiro positivo."
        )
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise AgendaMasterError(
            f"{field}.event_id invalido: esperado inteiro positivo."
        ) from exc
    if value <= 0:
        raise AgendaMasterError(
            f"{field}.event_id invalido: esperado inteiro positivo."
        )
    return value


def _parse_session_date(raw: Any, *, field: str) -> date:
    """Parse session_date field as `date`."""

    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    text = str(raw or "").strip()
    if not text:
        raise AgendaMasterError(
            f"{field}.session_date ausente/vazio. Como corrigir: usar YYYY-MM-DD."
        )
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise AgendaMasterError(
            f"{field}.session_date invalido: esperado YYYY-MM-DD."
        ) from exc


def _parse_start_at(raw: Any, *, field: str) -> datetime:
    """Parse start_at field as `datetime`."""

    if isinstance(raw, datetime):
        return raw
    text = str(raw or "").strip()
    if not text:
        raise AgendaMasterError(
            f"{field}.start_at ausente/vazio. Como corrigir: usar YYYY-MM-DDTHH:MM:SS."
        )
    try:
        return datetime.fromisoformat(text.replace(" ", "T"))
    except ValueError as exc:
        raise AgendaMasterError(
            f"{field}.start_at invalido: esperado YYYY-MM-DDTHH:MM:SS."
        ) from exc


def _parse_session_type(raw: Any, *, field: str) -> SessionType:
    """Parse and validate controlled master-agenda session type."""

    text = str(raw or "").strip()
    if not text:
        raise AgendaMasterError(
            f"{field}.type ausente/vazio. Como corrigir: usar diurno_gratuito ou noturno_show."
        )
    try:
        session_type = coerce_session_type(text)
    except ValueError as exc:
        raise AgendaMasterError(
            f"{field}.type invalido ({text!r}). Como corrigir: usar diurno_gratuito ou noturno_show."
        ) from exc
    if session_type not in _ALLOWED_MASTER_TYPES:
        raise AgendaMasterError(
            f"{field}.type invalido ({text!r}). Como corrigir: usar diurno_gratuito ou noturno_show."
        )
    return session_type


def _validate_session_entry(entry: Mapping[str, Any], *, field: str) -> AgendaSession:
    """Validate one agenda session entry."""

    event_id = _parse_event_id(entry, field=field)
    session_date = _parse_session_date(
        entry.get("session_date", entry.get("date")),
        field=field,
    )
    start_at = _parse_start_at(
        entry.get("start_at", entry.get("session_start_at")),
        field=field,
    )
    session_type = _parse_session_type(
        entry.get("type", entry.get("session_type")),
        field=field,
    )
    name = _require_non_empty_text(
        entry,
        ("name", "session_name", "sessao"),
        field=f"{field}.name",
    )
    session_key = str(entry.get("session_key", "")).strip() or None

    if start_at.date() != session_date:
        raise AgendaMasterError(
            f"{field} inconsistente: session_date={session_date.isoformat()} "
            f"diferente de start_at={start_at.isoformat()}. "
            "Como corrigir: alinhar a data da sessao com a data de inicio."
        )

    return AgendaSession(
        event_id=event_id,
        session_date=session_date,
        start_at=start_at,
        session_type=session_type,
        name=name,
        session_key=session_key,
    )


def _validate_unique_sessions(sessions: Sequence[AgendaSession]) -> None:
    """Validate duplicate session keys across the loaded agenda."""

    seen: dict[tuple[Any, ...], int] = {}
    for index, session in enumerate(sessions):
        key = (
            session.event_id,
            session.session_date.isoformat(),
            session.start_at.isoformat(),
            session.name.casefold(),
        )
        if key in seen:
            previous_index = seen[key]
            raise AgendaMasterError(
                "Sessao duplicada na agenda master: "
                f"entrada {index} duplica entrada {previous_index} "
                f"({session.name} em {session.start_at.isoformat()}). "
                "Como corrigir: remover duplicidade ou ajustar horario/nome."
            )
        seen[key] = index


def _load_yaml_agenda(path: Path) -> tuple[int, list[Mapping[str, Any]]]:
    """Load raw YAML agenda payload."""

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    root = _as_mapping(raw, field="$")
    version = _parse_version(root.get("version"), field="$.version", default=1)
    sessions_raw = root.get("sessions")
    if not isinstance(sessions_raw, list) or not sessions_raw:
        raise AgendaMasterError(
            "$.sessions invalido: esperado lista nao vazia. "
            "Como corrigir: adicionar ao menos uma sessao."
        )
    output: list[Mapping[str, Any]] = []
    for index, item in enumerate(sessions_raw):
        output.append(_as_mapping(item, field=f"$.sessions[{index}]"))
    return version, output


def _normalize_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize CSV row keys to lowercase snake-like aliases."""

    normalized: dict[str, Any] = {}
    for key, value in row.items():
        normalized_key = str(key or "").strip().casefold()
        normalized[normalized_key] = value
    return normalized


def _load_csv_agenda(path: Path) -> tuple[int, list[Mapping[str, Any]]]:
    """Load raw CSV agenda payload."""

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise AgendaMasterError(
                "CSV da agenda master sem cabecalho. "
                "Como corrigir: incluir colunas event_id, session_date, start_at, type, name."
            )
        rows = [_normalize_csv_row(dict(row)) for row in reader]

    if not rows:
        raise AgendaMasterError(
            "CSV da agenda master vazio. Como corrigir: adicionar ao menos uma sessao."
        )
    return 1, rows


def load_agenda_master(path: Path | str | None = None) -> AgendaMaster:
    """Load and validate master agenda from YAML or CSV.

    Supported formats:
    - `.yml` / `.yaml` with root fields `version` and `sessions`.
    - `.csv` with columns `event_id`, `session_date`, `start_at`, `type`, `name`.

    Args:
        path: Optional agenda file path. Defaults to bundled YAML config.

    Returns:
        Validated `AgendaMaster` contract.

    Raises:
        FileNotFoundError: If file path does not exist.
        AgendaMasterError: If format/schema/content validation fails.
    """

    agenda_path = Path(path) if path is not None else DEFAULT_AGENDA_MASTER_PATH
    if not agenda_path.exists():
        raise FileNotFoundError(f"Arquivo de agenda master nao encontrado: {agenda_path}")

    suffix = agenda_path.suffix.casefold()
    if suffix not in _SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(_SUPPORTED_SUFFIXES))
        raise AgendaMasterError(
            f"Formato de agenda nao suportado ({suffix}). Como corrigir: usar {supported}."
        )

    if suffix in {".yml", ".yaml"}:
        version, entries = _load_yaml_agenda(agenda_path)
    else:
        version, entries = _load_csv_agenda(agenda_path)

    sessions = [
        _validate_session_entry(entry, field=f"agenda.sessions[{index}]")
        for index, entry in enumerate(entries)
    ]
    _validate_unique_sessions(sessions)
    sessions_sorted = tuple(
        sorted(
            sessions,
            key=lambda item: (
                item.event_id,
                item.session_date.isoformat(),
                item.start_at.isoformat(),
                item.name.casefold(),
            ),
        )
    )
    return AgendaMaster(
        version=version,
        sessions=sessions_sorted,
        source_path=agenda_path,
    )
