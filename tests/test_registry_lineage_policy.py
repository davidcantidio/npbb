"""Unit tests for lineage policy evaluation in core registry package."""

from __future__ import annotations

import pytest

from core.registry import LineagePolicy, evaluate_lineage_policy


def test_lineage_policy_required_blocks_when_lineage_is_missing() -> None:
    """Required policy must block when any record does not provide lineage."""
    policy = LineagePolicy(
        dataset_name="stg_show_day_summary",
        requirement="required",
        missing_lineage_severity="partial",
    )
    records = [
        {"lineage_ref_id": 10},
        {"lineage_ref_id": None},
    ]

    result = evaluate_lineage_policy(records, policy=policy)
    assert result.should_block is True
    assert result.status_on_block == "partial"
    assert result.missing_records == 1
    assert result.missing_indices == (1,)
    assert "exige linhagem" in result.message


def test_lineage_policy_optional_never_blocks() -> None:
    """Optional policy allows records without lineage."""
    policy = LineagePolicy(dataset_name="stg_optin_events", requirement="optional")
    result = evaluate_lineage_policy([{"lineage_ref_id": None}], policy=policy)
    assert result.should_block is False
    assert result.status_on_block is None


def test_lineage_policy_required_passes_when_all_records_have_lineage() -> None:
    """Required policy should pass when all records include lineage reference."""
    policy = LineagePolicy(dataset_name="stg_access_control", requirement="required")
    result = evaluate_lineage_policy(
        [{"lineage_ref_id": 1}, {"lineage_ref_id": 2}],
        policy=policy,
    )
    assert result.should_block is False
    assert result.missing_records == 0
    assert "atendida" in result.message


def test_lineage_policy_rejects_invalid_configuration() -> None:
    """Invalid policy values raise actionable errors."""
    with pytest.raises(ValueError, match="requirement invalido"):
        LineagePolicy(dataset_name="x", requirement="mandatory")

    with pytest.raises(ValueError, match="missing_lineage_severity invalido"):
        LineagePolicy(dataset_name="x", requirement="required", missing_lineage_severity="warn")

    with pytest.raises(ValueError, match="dataset_name vazio"):
        LineagePolicy(dataset_name="   ")

