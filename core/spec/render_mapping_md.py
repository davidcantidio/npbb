"""Markdown renderer for requirement-to-schema mapping contracts.

This renderer documents what is actually present in the mapping YAML plus
checklist coverage, so implementation and documentation stay aligned.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

from .mapping_models import MappingSpec, RequirementMapping
from .spec_models import DocxChecklistRow


def _normalize_item_key(text: str) -> str:
    """Normalize checklist/mapping item keys for case-insensitive matching."""
    return " ".join((text or "").strip().casefold().split())


def _sources_as_text(requirement: RequirementMapping) -> str:
    """Render source lineage list as a compact string."""
    if not requirement.sources:
        return "-"
    return "; ".join(f"{src.source_id} ({src.location})" for src in requirement.sources)


def _validations_as_text(requirement: RequirementMapping) -> str:
    """Render validation rules as a compact string."""
    if not requirement.validations:
        return "-"
    return "; ".join(
        f"{rule.rule_id} [{rule.rule_type}/{rule.severity}] {rule.expression}"
        for rule in requirement.validations
    )


def _public_gauge_notes(requirement: RequirementMapping) -> str:
    """Infer public-gauge notes from mapping fields/rules without inventing data."""
    haystack = " | ".join(
        [
            requirement.item_docx,
            requirement.target_field,
            requirement.calculation_rule,
            " ".join(src.source_id for src in requirement.sources),
        ]
    ).casefold()

    notes: List[str] = []
    if any(token in haystack for token in ("entries_validated", "entrada validada", "catraca")):
        notes.append("Regua de publico: entradas validadas")
    if any(token in haystack for token in ("opt-in", "optin")):
        notes.append("Regua de publico: opt-in aceitos")
    if any(token in haystack for token in ("ticket_sales", "ingresso", "sold", "vendido", "vendas")):
        notes.append("Regua de publico: ingressos vendidos")
    if any(token in haystack for token in ("publico_unico", "cpf_unico", "deduplic", "unique")):
        notes.append("Regua de publico: publico unico")

    return "; ".join(notes) if notes else "-"


def _checklist_coverage(checklist: Sequence[DocxChecklistRow], mapping: MappingSpec) -> Dict[str, List[str]]:
    """Compute checklist item coverage against mapping entries."""
    mapped_keys = {_normalize_item_key(req.item_docx) for req in mapping.requirements}
    covered: List[str] = []
    missing: List[str] = []
    for row in checklist:
        if _normalize_item_key(row.section) in mapped_keys:
            covered.append(row.section)
            continue
        missing.append(row.section)
    return {"covered": covered, "missing": missing}


def render_mapping_md(checklist: Sequence[DocxChecklistRow], mapping: MappingSpec) -> str:
    """Render mapping documentation from checklist and typed mapping spec.

    Args:
        checklist: Checklist rows extracted from the DOCX spec.
        mapping: Typed mapping specification loaded from YAML.

    Returns:
        Markdown content for `03_requirements_to_schema_mapping.md`.

    Raises:
        ValueError: If checklist is empty.
    """
    if not checklist:
        raise ValueError("Checklist cannot be empty.")

    lines: List[str] = []
    lines.append("# Requirements to Schema Mapping")
    lines.append("")
    lines.append(
        "Documento gerado automaticamente a partir do checklist do DOCX e do mapping YAML. "
        "Nao inclui conteudo manual nem metricas inventadas."
    )
    lines.append("")
    lines.append(f"- `schema_version`: `{mapping.schema_version}`")
    lines.append(f"- `spec_source`: `{mapping.spec_source}`")
    lines.append("")
    lines.append("## Mapeamento Item -> Campo -> Regra")
    lines.append("")
    lines.append(
        "| Requirement ID | Item (DOCX) | Tabela.campo | Regra de calculo | Fonte(s) | Validacoes | "
        "Observacoes (regua de publico) |"
    )
    lines.append("|---|---|---|---|---|---|---|")

    for requirement in mapping.requirements:
        lines.append(
            "| "
            + " | ".join(
                [
                    requirement.requirement_id,
                    requirement.item_docx,
                    requirement.target_field,
                    requirement.calculation_rule,
                    _sources_as_text(requirement),
                    _validations_as_text(requirement),
                    _public_gauge_notes(requirement),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Cobertura do Checklist")
    lines.append("")
    coverage = _checklist_coverage(checklist, mapping)
    lines.append("| Item do checklist | Cobertura de mapping |")
    lines.append("|---|---|")
    for section in coverage["covered"]:
        lines.append(f"| {section} | OK |")
    for section in coverage["missing"]:
        lines.append(f"| {section} | GAP |")

    lines.append("")
    lines.append("## Contratos de Mart")
    lines.append("")
    lines.append("| Mart | Grain | Requirement IDs | Campos de saida |")
    lines.append("|---|---|---|---|")
    for mart in mapping.marts:
        req_ids = ", ".join(mart.requirement_ids) if mart.requirement_ids else "-"
        out_fields = ", ".join(field.field for field in mart.output_fields) if mart.output_fields else "-"
        lines.append(f"| {mart.mart_name} | {mart.grain} | {req_ids} | {out_fields} |")

    lines.append("")
    return "\n".join(lines)
