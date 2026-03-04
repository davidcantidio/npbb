"""Actionable adapter errors for canonical lead-row payloads."""

from __future__ import annotations

from collections.abc import Iterable


class LeadRowAdapterError(ValueError):
    """Raised when a payload cannot be adapted into the canonical lead shape."""

    def __init__(
        self,
        *,
        source: str,
        message: str,
        invalid_keys: Iterable[str] = (),
    ) -> None:
        self.source = source
        self.invalid_keys = tuple(sorted({key for key in invalid_keys if key}))
        detail = message
        if self.invalid_keys:
            detail = f"{message} Chaves: {', '.join(self.invalid_keys)}."
        super().__init__(detail)
