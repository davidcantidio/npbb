"""Database-facing protocols used by core lead ETL validation."""

from __future__ import annotations

from typing import Any, Protocol


class SessionLike(Protocol):
    """Minimal session surface required by core validation helpers."""

    def get_bind(self) -> Any:
        """Return SQLAlchemy bind/engine."""

    def execute(self, statement: Any) -> Any:
        """Execute SQLAlchemy statement."""

    def add(self, instance: Any) -> None:
        """Add row/object to the session."""

    def delete(self, instance: Any) -> None:
        """Delete row/object from the session."""

    def flush(self) -> None:
        """Flush pending statements."""

    def commit(self) -> None:
        """Commit pending statements."""

