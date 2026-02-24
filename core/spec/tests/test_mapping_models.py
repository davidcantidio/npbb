"""Unit tests for DOCX mapping schema parser and validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.spec.mapping_models import MappingSchemaError, load_mapping_contract, parse_mapping_contract


def _valid_payload() -> dict:
    """Return a minimal valid mapping contract payload."""
    return {
        "schema_version": "1.0",
        "spec_source": "docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "item_docx": "Shows por dia (12/12, 13/12, 14/12)",
                "target_field": "mart_report_show_day_summary.coverage_status",
                "calculation_rule": "CASE WHEN x THEN 'OK' ELSE 'GAP' END",
                "sources": [{"source_id": "pdf_12_12", "location": "pagina 2 / tabela X"}],
                "validations": [
                    {
                        "rule_id": "VAL-001",
                        "rule_type": "reconciliation",
                        "severity": "error",
                        "expression": "coverage_status IS NOT NULL",
                    }
                ],
            }
        ],
        "marts": [
            {
                "mart_name": "mart_report_show_day_summary",
                "grain": "evento_dia_sessao",
                "description": "Resumo por dia/sessao.",
                "requirement_ids": ["REQ-001"],
                "output_fields": [
                    {
                        "field": "coverage_status",
                        "source": "attendance_access_control + ticket_sales",
                        "rule": "Regra de cobertura por sessao",
                    }
                ],
            }
        ],
    }


def test_load_mapping_contract_from_example_yaml() -> None:
    """Example YAML file can be loaded and parsed as a valid contract."""
    contract = load_mapping_contract(Path("core/spec/mapping_schema.yml"))

    assert contract.schema_version == "1.0"
    assert contract.requirements
    assert contract.marts
    assert any("Shows por dia" in req.item_docx for req in contract.requirements)
    assert any(req.target_field.startswith("public.") for req in contract.requirements)


def test_parse_mapping_contract_fails_with_missing_required_field() -> None:
    """Validation fails with clear path when required field is missing."""
    payload = _valid_payload()
    del payload["requirements"][0]["item_docx"]

    with pytest.raises(MappingSchemaError, match=r"\$\.requirements\[0\]\.item_docx: missing required field"):
        parse_mapping_contract(payload)


def test_parse_mapping_contract_fails_with_invalid_domain_value() -> None:
    """Validation fails when enum/domain values are outside allowed set."""
    payload = _valid_payload()
    payload["requirements"][0]["validations"][0]["severity"] = "critical"

    with pytest.raises(
        MappingSchemaError,
        match=r"\$\.requirements\[0\]\.validations\[0\]\.severity: invalid value 'critical'",
    ):
        parse_mapping_contract(payload)


def test_parse_mapping_contract_fails_with_unknown_requirement_reference() -> None:
    """Validation fails when mart requirement_ids reference unknown IDs."""
    payload = _valid_payload()
    payload["marts"][0]["requirement_ids"] = ["REQ-UNKNOWN"]

    with pytest.raises(
        MappingSchemaError,
        match=r"\$\.marts\[0\]\.requirement_ids: unknown requirement_id reference\(s\): REQ-UNKNOWN",
    ):
        parse_mapping_contract(payload)
