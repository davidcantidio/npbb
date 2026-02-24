"""Tests for mapping loader, coverage validator and markdown renderer.

This suite validates the anti-omission flow for DOCX mapping contracts:
loading YAML, checking checklist coverage, and generating mapping docs.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.spec.mapping_loader import load_mapping
from core.spec.mapping_models import (
    MappingContract,
    MappingSchemaError,
    MartContract,
    MartOutputField,
    RequirementMapping,
    SourceRef,
    ValidationRule,
)
from core.spec.mapping_validate import validate_mapping_coverage
from core.spec.render_mapping_md import render_mapping_md
from core.spec.spec_models import DocxChecklistRow


def _mapping_fixture_path() -> Path:
    """Return path of the minimal valid mapping fixture."""
    return Path("tests/fixtures/spec/mapping_min.yml")


def _checklist_rows() -> list[DocxChecklistRow]:
    """Build checklist rows used across validator and renderer tests."""
    return [
        DocxChecklistRow(
            section="Publico do evento (controle de acesso - entradas validadas)",
            expected_content="Entradas validadas",
            granularity="evento_dia_sessao",
            required_fields="attendance_access_control.entries_validated",
            source_in_docx='Secao "Publico"',
            status="GAP",
        ),
        DocxChecklistRow(
            section="Dinamica de vendas (pre-venda) - shows (Opt-in aceitos)",
            expected_content="Opt-in aceitos",
            granularity="evento_dia_sessao",
            required_fields="optin_transactions.optin_accepted",
            source_in_docx='Secao "Pre-venda"',
            status="GAP",
        ),
        DocxChecklistRow(
            section="Publico unico deduplicado",
            expected_content="Publico unico",
            granularity="evento_dia_sessao",
            required_fields="audience_metrics.unique_public",
            source_in_docx='Secao "Publico"',
            status="GAP",
        ),
    ]


def _mapping_with_single_requirement(*, rule: str, with_validations: bool) -> MappingContract:
    """Build mapping contract used for validation edge-case tests."""
    validations: list[ValidationRule] = []
    if with_validations:
        validations = [
            ValidationRule(
                rule_id="VAL-001",
                rule_type="reconciliation",
                severity="error",
                expression="entries_validated >= 0",
            )
        ]

    requirement = RequirementMapping(
        requirement_id="REQ-001",
        item_docx="Publico do evento (controle de acesso - entradas validadas)",
        target_field="public.attendance_access_control.entries_validated",
        calculation_rule=rule,
        sources=[SourceRef(source_id="pdf_access_control_12_13", location="pagina 1 / tabela Presencas")],
        validations=validations,
    )
    return MappingContract(
        schema_version="1.0",
        spec_source="docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md",
        requirements=[requirement],
        marts=[
            MartContract(
                mart_name="mart_report_show_day_summary",
                grain="evento_dia_sessao",
                description="Resumo por sessao de show",
                requirement_ids=["REQ-001"],
                output_fields=[
                    MartOutputField(
                        field="entries_validated",
                        source="public.attendance_access_control.entries_validated",
                        rule="Soma por sessao",
                    )
                ],
            )
        ],
    )


def test_load_mapping_success_from_fixture() -> None:
    """Load minimal YAML fixture and ensure normalized typed output."""
    mapping = load_mapping(_mapping_fixture_path())

    assert mapping.schema_version == "1.0"
    assert len(mapping.requirements) == 2
    assert mapping.requirements[0].target_field.startswith("public.")
    assert mapping.marts[0].mart_name == "mart_report_show_day_summary"


def test_load_mapping_fails_when_required_field_is_missing(tmp_path: Path) -> None:
    """Loader fails with clear error path when required YAML field is missing."""
    payload = yaml.safe_load(_mapping_fixture_path().read_text(encoding="utf-8"))
    del payload["requirements"][0]["item_docx"]
    invalid_path = tmp_path / "mapping_invalid_missing.yml"
    invalid_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(MappingSchemaError, match=r"\$\.requirements\[0\]\.item_docx: missing required field"):
        load_mapping(invalid_path)


def test_validate_mapping_coverage_flags_item_without_mapping() -> None:
    """Validator identifies checklist item that has no corresponding mapping."""
    mapping = load_mapping(_mapping_fixture_path())

    findings = validate_mapping_coverage(_checklist_rows(), mapping)

    assert any(f.code == "CHECKLIST_ITEM_WITHOUT_MAPPING" for f in findings)
    assert any(f.item_docx == "Publico unico deduplicado" for f in findings)


def test_validate_mapping_coverage_flags_missing_calculation_rule() -> None:
    """Validator raises finding when a mapping entry has no calculation rule."""
    mapping = _mapping_with_single_requirement(rule="", with_validations=True)

    findings = validate_mapping_coverage(_checklist_rows(), mapping)

    assert any(f.code == "MAPPING_RULE_MISSING" for f in findings)


def test_validate_mapping_coverage_flags_derived_without_validations() -> None:
    """Validator raises finding when derived metric has no validation rules."""
    mapping = _mapping_with_single_requirement(rule="SUM(entries_validated)", with_validations=False)

    findings = validate_mapping_coverage(_checklist_rows(), mapping)

    assert any(f.code == "MAPPING_VALIDATIONS_MISSING_DERIVED" for f in findings)


def test_render_mapping_md_includes_required_columns_and_rows() -> None:
    """Render output includes required columns and key fixture mappings."""
    mapping = load_mapping(_mapping_fixture_path())
    markdown = render_mapping_md(_checklist_rows(), mapping)

    assert "| Requirement ID | Item (DOCX) | Tabela.campo | Regra de calculo | Fonte(s) | Validacoes | Observacoes (regua de publico) |" in markdown
    assert "| REQ-PUBLICO-001 | Publico do evento (controle de acesso - entradas validadas) | public.attendance_access_control.entries_validated | SUM(entries_validated) por evento_dia_sessao |" in markdown
    assert "| REQ-OPTIN-001 | Dinamica de vendas (pre-venda) - shows (Opt-in aceitos) | public.optin_transactions.optin_accepted | SUM(optin_accepted) por evento_dia_sessao |" in markdown
    assert "| Publico unico deduplicado | GAP |" in markdown
