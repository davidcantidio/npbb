"""Unit tests for config-driven ticket-category segment mapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from etl.transform.segment_mapper import (
    Segment,
    SegmentMappingError,
    load_segment_mapping,
    map_ticket_category_to_segment,
    map_ticket_category_with_finding,
    normalize_ticket_category,
)


def test_load_segment_mapping_from_repo_config() -> None:
    """Default mapping config should load and expose known canonical entries."""

    mapping, default_segment = load_segment_mapping()
    assert default_segment == Segment.DESCONHECIDO
    assert normalize_ticket_category("funcionários bb") in mapping
    assert mapping[normalize_ticket_category("funcionários bb")] == Segment.FUNCIONARIO_BB


def test_map_ticket_category_to_segment_is_deterministic() -> None:
    """Same category input should always map to same canonical segment."""

    value = "  Funcionários   BB "
    first = map_ticket_category_to_segment(value)
    second = map_ticket_category_to_segment(value)
    assert first == Segment.FUNCIONARIO_BB
    assert first == second


def test_unknown_category_returns_default_with_finding() -> None:
    """Unknown categories should map to DESCONHECIDO and emit actionable finding."""

    result = map_ticket_category_with_finding("Categoria Inexistente XYZ")
    assert result.segment == Segment.DESCONHECIDO
    assert result.finding is not None
    assert result.finding.code == "SEGMENT_CATEGORY_UNKNOWN"
    assert "segment_mapping.yml" in result.finding.message


def test_known_category_returns_no_finding() -> None:
    """Known categories should map without findings."""

    result = map_ticket_category_with_finding("Inteira")
    assert result.segment == Segment.PUBLICO_GERAL
    assert result.finding is None


def test_load_segment_mapping_rejects_invalid_segment(tmp_path: Path) -> None:
    """Invalid segment labels in YAML config should fail fast."""

    cfg = tmp_path / "bad_segment_mapping.yml"
    cfg.write_text(
        "default_segment: DESCONHECIDO\nmappings:\n  INVALID_SEGMENT:\n    - CAT\n",
        encoding="utf-8",
    )

    with pytest.raises(SegmentMappingError, match="Segmento invalido"):
        load_segment_mapping(cfg)

