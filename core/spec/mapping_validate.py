"""Coverage validator for checklist-vs-mapping contracts.

This module checks whether every DOCX checklist item has at least one mapping
and whether each mapping contains the minimum contract elements required by the
data gate.
"""

from __future__ import annotations

import json
import re
from typing import Dict, Iterable, List, Sequence

from .mapping_models import MappingSpec, RequirementMapping
from .spec_models import DocxChecklistRow, Finding


_DERIVED_EXPR_RE = re.compile(
    r"(\b(sum|count|avg|min|max|case|when|then|else|ratio|percent)\b|[+\-/*])",
    flags=re.IGNORECASE,
)


def _normalize_item_key(text: str) -> str:
    """Normalize DOCX item strings for matching."""
    return " ".join((text or "").strip().casefold().split())


def _is_derived_rule(calculation_rule: str) -> bool:
    """Return True when the calculation rule suggests a derived metric."""
    clean = (calculation_rule or "").strip()
    if not clean:
        return False
    return bool(_DERIVED_EXPR_RE.search(clean))


def _index_mappings_by_item(mappings: Sequence[RequirementMapping]) -> Dict[str, List[RequirementMapping]]:
    """Group requirement mappings by normalized DOCX item."""
    grouped: Dict[str, List[RequirementMapping]] = {}
    for mapping in mappings:
        key = _normalize_item_key(mapping.item_docx)
        grouped.setdefault(key, []).append(mapping)
    return grouped


def _validate_minimum_mapping_rules(mapping: RequirementMapping) -> List[Finding]:
    """Validate minimum required fields for a single requirement mapping."""
    findings: List[Finding] = []
    item = mapping.item_docx or "<sem item_docx>"
    ref = f"requirement_id={mapping.requirement_id}"

    if not (mapping.target_field or "").strip():
        findings.append(
            Finding(
                severity="error",
                code="MAPPING_TARGET_MISSING",
                item_docx=item,
                message="Mapping sem destino (target_field).",
                reference=ref,
            )
        )
    elif len([p for p in mapping.target_field.split(".") if p.strip()]) != 3:
        findings.append(
            Finding(
                severity="warning",
                code="MAPPING_TARGET_NOT_NORMALIZED",
                item_docx=item,
                message="target_field nao esta normalizado como schema.table.field.",
                reference=f"{ref} target_field={mapping.target_field}",
            )
        )

    if not (mapping.calculation_rule or "").strip():
        findings.append(
            Finding(
                severity="error",
                code="MAPPING_RULE_MISSING",
                item_docx=item,
                message="Mapping sem regra de calculo.",
                reference=ref,
            )
        )

    if not mapping.sources:
        findings.append(
            Finding(
                severity="error",
                code="MAPPING_SOURCES_MISSING",
                item_docx=item,
                message="Mapping sem fontes de linhagem.",
                reference=ref,
            )
        )

    if _is_derived_rule(mapping.calculation_rule) and not mapping.validations:
        findings.append(
            Finding(
                severity="error",
                code="MAPPING_VALIDATIONS_MISSING_DERIVED",
                item_docx=item,
                message="Metrica derivada exige validacoes minimas.",
                reference=ref,
            )
        )
    return findings


def validate_mapping_coverage(
    checklist: Sequence[DocxChecklistRow],
    mapping: MappingSpec,
) -> List[Finding]:
    """Validate checklist coverage and mapping completeness.

    Args:
        checklist: Checklist items extracted from DOCX spec.
        mapping: Typed mapping specification loaded from YAML.

    Returns:
        List of findings with severity, code and DOCX item reference.

    Raises:
        ValueError: If checklist is empty.
    """
    if not checklist:
        raise ValueError("Checklist cannot be empty.")

    findings: List[Finding] = []
    mappings_by_item = _index_mappings_by_item(mapping.requirements)
    checklist_by_item = {_normalize_item_key(row.section): row for row in checklist}

    for req in mapping.requirements:
        findings.extend(_validate_minimum_mapping_rules(req))

    for key, row in checklist_by_item.items():
        matched = mappings_by_item.get(key, [])
        if not matched:
            findings.append(
                Finding(
                    severity="error",
                    code="CHECKLIST_ITEM_WITHOUT_MAPPING",
                    item_docx=row.section,
                    message="Item do checklist nao possui mapping associado.",
                    reference=row.source_in_docx,
                )
            )
            continue

    for req in mapping.requirements:
        key = _normalize_item_key(req.item_docx)
        if key not in checklist_by_item:
            findings.append(
                Finding(
                    severity="warning",
                    code="MAPPING_ITEM_NOT_IN_CHECKLIST",
                    item_docx=req.item_docx,
                    message="Mapping referencia item que nao existe no checklist atual.",
                    reference=f"requirement_id={req.requirement_id}",
                )
            )

    return findings


def render_findings_json(findings: Iterable[Finding]) -> str:
    """Render findings as a JSON string for gate consumption."""
    return json.dumps([finding.model_dump() for finding in findings], ensure_ascii=False, indent=2)


def render_findings_markdown(findings: Sequence[Finding]) -> str:
    """Render findings as markdown table for human review."""
    lines: List[str] = []
    lines.append("# Mapping Coverage Findings")
    lines.append("")
    lines.append("| Severidade | Codigo | Item DOCX | Mensagem | Referencia |")
    lines.append("|---|---|---|---|---|")

    if not findings:
        lines.append("| info | NO_FINDINGS | - | Nenhum finding de cobertura. | - |")
        return "\n".join(lines)

    for finding in findings:
        reference = finding.reference or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    finding.severity,
                    finding.code,
                    finding.item_docx,
                    finding.message,
                    reference,
                ]
            )
            + " |"
        )
    return "\n".join(lines)
