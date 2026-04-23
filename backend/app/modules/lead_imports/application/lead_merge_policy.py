"""Single merge policy for Gold, ETL, and legacy lead imports."""

from __future__ import annotations

from typing import Any

from app.models.models import Lead


def lead_field_has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def merge_lead_payload_fill_missing(lead: Lead, payload: dict[str, object]) -> None:
    """Apply non-destructive merge: only set attributes that are empty on `lead`.

    Incoming empty values (None, blank strings) never clear existing data.
    """
    for field, value in payload.items():
        if not lead_field_has_value(value):
            continue
        current = getattr(lead, field, None)
        if lead_field_has_value(current):
            continue
        setattr(lead, field, value)
