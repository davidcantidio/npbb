"""Unit tests for checklist-to-mapping coverage validation."""

from __future__ import annotations

import json

from core.spec.mapping_models import (
    MappingContract,
    MartContract,
    MartOutputField,
    RequirementMapping,
    SourceRef,
    ValidationRule,
)
from core.spec.mapping_validate import (
    render_findings_json,
    render_findings_markdown,
    validate_mapping_coverage,
)
from core.spec.spec_models import DocxChecklistRow


def _checklist_rows() -> list[DocxChecklistRow]:
    """Return checklist fixture with two DOCX items."""
    return [
        DocxChecklistRow(
            section="Publico do evento",
            expected_content="Entradas validadas",
            granularity="evento_dia_sessao",
            required_fields="attendance_access_control.entries_validated",
            source_in_docx="Secao Publico",
            status="GAP",
        ),
        DocxChecklistRow(
            section="Shows por dia (12/12, 13/12, 14/12)",
            expected_content="Cobertura por sessao",
            granularity="evento_dia_sessao",
            required_fields="mart_report_show_day_summary.coverage_status",
            source_in_docx="Secao Shows",
            status="GAP",
        ),
    ]


def _minimal_mapping(requirements: list[RequirementMapping]) -> MappingContract:
    """Build a minimal mapping contract with one mart reference."""
    return MappingContract(
        schema_version="1.0",
        spec_source="docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md",
        requirements=requirements,
        marts=[
            MartContract(
                mart_name="mart_report_show_day_summary",
                grain="evento_dia_sessao",
                description="Resumo de cobertura por sessao",
                requirement_ids=[requirements[0].requirement_id] if requirements else [],
                output_fields=[
                    MartOutputField(
                        field="coverage_status",
                        source="public.mart_report_show_day_summary.coverage_status",
                        rule="Consolidacao",
                    )
                ],
            )
        ],
    )


def test_validate_mapping_coverage_flags_missing_checklist_item_mapping() -> None:
    """Validator reports checklist items that do not have mapping entries."""
    mapping = _minimal_mapping(
        requirements=[
            RequirementMapping(
                requirement_id="REQ-001",
                item_docx="Publico do evento",
                target_field="public.attendance_access_control.entries_validated",
                calculation_rule="SUM(entries_validated)",
                sources=[SourceRef(source_id="pdf_01", location="pagina 1")],
                validations=[
                    ValidationRule(
                        rule_id="VAL-001",
                        rule_type="reconciliation",
                        severity="error",
                        expression="entries_validated >= 0",
                    )
                ],
            )
        ]
    )

    findings = validate_mapping_coverage(_checklist_rows(), mapping)

    assert any(f.code == "CHECKLIST_ITEM_WITHOUT_MAPPING" for f in findings)
    assert any("Shows por dia" in f.item_docx for f in findings)


def test_validate_mapping_coverage_flags_incomplete_mapping_fields() -> None:
    """Validator reports missing destination, rule, sources and derived validations."""
    mapping = _minimal_mapping(
        requirements=[
            RequirementMapping(
                requirement_id="REQ-002",
                item_docx="Publico do evento",
                target_field="",
                calculation_rule="SUM(entries_validated)",
                sources=[],
                validations=[],
            ),
            RequirementMapping(
                requirement_id="REQ-003",
                item_docx="Item fora do checklist",
                target_field="public.ticket_sales.total_sold",
                calculation_rule="",
                sources=[SourceRef(source_id="xlsx_01", location="aba vendas")],
                validations=[],
            ),
        ]
    )

    findings = validate_mapping_coverage(_checklist_rows(), mapping)
    codes = {f.code for f in findings}

    assert "MAPPING_TARGET_MISSING" in codes
    assert "MAPPING_SOURCES_MISSING" in codes
    assert "MAPPING_VALIDATIONS_MISSING_DERIVED" in codes
    assert "MAPPING_RULE_MISSING" in codes
    assert "MAPPING_ITEM_NOT_IN_CHECKLIST" in codes


def test_validate_mapping_coverage_outputs_json_and_markdown() -> None:
    """Finding outputs are consumable as JSON and markdown."""
    mapping = _minimal_mapping(
        requirements=[
            RequirementMapping(
                requirement_id="REQ-001",
                item_docx="Publico do evento",
                target_field="public.attendance_access_control.entries_validated",
                calculation_rule="SUM(entries_validated)",
                sources=[SourceRef(source_id="pdf_01", location="pagina 1")],
                validations=[
                    ValidationRule(
                        rule_id="VAL-001",
                        rule_type="reconciliation",
                        severity="error",
                        expression="entries_validated >= 0",
                    )
                ],
            )
        ]
    )
    findings = validate_mapping_coverage(_checklist_rows(), mapping)

    as_json = render_findings_json(findings)
    payload = json.loads(as_json)
    assert isinstance(payload, list)
    assert all("severity" in row and "item_docx" in row for row in payload)

    as_md = render_findings_markdown(findings)
    assert "| Severidade | Codigo | Item DOCX | Mensagem | Referencia |" in as_md
    assert "CHECKLIST_ITEM_WITHOUT_MAPPING" in as_md
