"""Consolidated lineage tests for location format/parse and policy enforcement."""

from __future__ import annotations

import pytest

from core.registry import LineagePolicy, evaluate_lineage_policy, format_location, parse_location


@pytest.mark.parametrize(
    ("location_type", "parts", "expected_formatted", "expected_parsed"),
    [
        ("page", {"number": 12}, "page:12", {"number": 12}),
        ("slide", {"number": 3}, "slide:3", {"number": 3}),
        ("sheet", {"name": " Resumo Final "}, "sheet:resumo final", {"name": "resumo final"}),
        ("range", {"start": "a1", "end": "d20"}, "range:A1:D20", {"start": "A1", "end": "D20"}),
    ],
)
def test_lineage_location_roundtrip_by_type(
    location_type: str,
    parts: dict[str, object],
    expected_formatted: str,
    expected_parsed: dict[str, object],
) -> None:
    """Formatter and parser must be roundtrip-compatible for each location type."""
    formatted = format_location(location_type, parts)
    parsed = parse_location(location_type, formatted)
    assert formatted == expected_formatted
    assert parsed == expected_parsed


@pytest.mark.parametrize(
    ("location_type", "parts"),
    [
        ("page", {"number": 0}),
        ("slide", {"number": -1}),
        ("sheet", {"name": "   "}),
        ("range", {"start": "A0", "end": "D20"}),
        ("range", {"start": "1A", "end": "D20"}),
        ("invalid_type", {"number": 1}),
    ],
)
def test_lineage_location_format_rejects_invalid_values(
    location_type: str,
    parts: dict[str, object],
) -> None:
    """Invalid location formatting inputs must fail with actionable messages."""
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
        ("invalid_type", "page:1"),
    ],
)
def test_lineage_location_parse_rejects_invalid_values(
    location_type: str,
    value: str,
) -> None:
    """Invalid location parsing inputs must fail with actionable messages."""
    with pytest.raises(ValueError, match="Como corrigir|invalido|vazio"):
        parse_location(location_type, value)


def test_lineage_policy_required_missing_returns_partial_status() -> None:
    """Required policy with partial severity blocks and classifies as partial."""
    result = evaluate_lineage_policy(
        records=[{"lineage_ref_id": 1}, {"lineage_ref_id": None}],
        policy=LineagePolicy(
            dataset_name="stg_show_day_summary",
            requirement="required",
            missing_lineage_severity="partial",
        ),
    )
    assert result.should_block is True
    assert result.status_on_block == "partial"
    assert result.missing_records == 1
    assert result.missing_indices == (1,)
    assert "Como corrigir" in result.message


def test_lineage_policy_required_missing_returns_failed_status() -> None:
    """Required policy with failed severity blocks and classifies as failed."""
    result = evaluate_lineage_policy(
        records=[{"lineage_ref_id": None}],
        policy=LineagePolicy(
            dataset_name="stg_access_control",
            requirement="required",
            missing_lineage_severity="failed",
        ),
    )
    assert result.should_block is True
    assert result.status_on_block == "failed"
    assert result.missing_records == 1
    assert "exige linhagem" in result.message


def test_lineage_policy_optional_missing_does_not_block() -> None:
    """Optional policy never blocks when lineage is missing."""
    result = evaluate_lineage_policy(
        records=[{"lineage_ref_id": None}],
        policy=LineagePolicy(dataset_name="stg_optin_events", requirement="optional"),
    )
    assert result.should_block is False
    assert result.status_on_block is None
    assert "Linhagem opcional" in result.message


def test_lineage_policy_required_with_full_coverage_passes() -> None:
    """Required policy should pass when every record has lineage reference ID."""
    result = evaluate_lineage_policy(
        records=[{"lineage_ref_id": 10}, {"lineage_ref_id": 11}],
        policy=LineagePolicy(dataset_name="stg_ticket_sales", requirement="required"),
    )
    assert result.should_block is False
    assert result.missing_records == 0
    assert result.status_on_block is None


def test_lineage_policy_invalid_configuration_is_actionable() -> None:
    """Invalid policy configuration must fail with actionable error messages."""
    with pytest.raises(ValueError, match="Como corrigir|invalido"):
        LineagePolicy(dataset_name="x", requirement="invalid")
    with pytest.raises(ValueError, match="Como corrigir|invalido"):
        LineagePolicy(dataset_name="x", missing_lineage_severity="warn")
    with pytest.raises(ValueError, match="Como corrigir|vazio"):
        LineagePolicy(dataset_name="  ")

