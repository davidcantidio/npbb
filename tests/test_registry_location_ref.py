"""Unit tests for registry location reference format and parsing helpers."""

from __future__ import annotations

import pytest

from core.registry import format_location, parse_location


@pytest.mark.parametrize(
    ("location_type", "parts", "expected"),
    [
        ("page", {"number": 12}, "page:12"),
        ("slide", {"number": 3}, "slide:3"),
        ("sheet", {"name": " aba principal  "}, "sheet:aba principal"),
        ("range", {"start": "a1", "end": "d20"}, "range:A1:D20"),
    ],
)
def test_format_location_outputs_canonical_values(
    location_type: str,
    parts: dict[str, object],
    expected: str,
) -> None:
    """Formatter generates stable canonical representation per location type."""
    assert format_location(location_type, parts) == expected


@pytest.mark.parametrize(
    ("location_type", "value", "expected"),
    [
        ("page", "page:12", {"number": 12}),
        ("slide", "slide:3", {"number": 3}),
        ("sheet", "sheet:aba principal", {"name": "aba principal"}),
        ("range", "range:A1:D20", {"start": "A1", "end": "D20"}),
    ],
)
def test_parse_location_recovers_structured_parts(
    location_type: str,
    value: str,
    expected: dict[str, object],
) -> None:
    """Parser recovers the structured values from canonical location strings."""
    assert parse_location(location_type, value) == expected


@pytest.mark.parametrize(
    ("location_type", "parts"),
    [
        ("page", {"number": 0}),
        ("slide", {"number": -1}),
        ("sheet", {"name": "   "}),
        ("range", {"start": "1A", "end": "B2"}),
        ("range", {"start": "A0", "end": "B2"}),
        ("unknown", {"number": 1}),
    ],
)
def test_format_location_rejects_invalid_inputs(location_type: str, parts: dict[str, object]) -> None:
    """Formatter raises actionable errors for invalid type/parts combinations."""
    with pytest.raises(ValueError, match="Como corrigir|invalido|vazio"):
        format_location(location_type, parts)


@pytest.mark.parametrize(
    ("location_type", "value"),
    [
        ("page", "page:0"),
        ("slide", "slide:-1"),
        ("sheet", "sheet:   "),
        ("range", "range:A0:D20"),
        ("range", "range:A1:20D"),
        ("unknown", "page:1"),
    ],
)
def test_parse_location_rejects_invalid_values(location_type: str, value: str) -> None:
    """Parser raises actionable errors when canonical format/domain is invalid."""
    with pytest.raises(ValueError, match="Como corrigir|invalido|vazio"):
        parse_location(location_type, value)

