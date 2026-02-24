"""Spec gate orchestration for DOCX template governance.

This module centralizes gate logic that must run before ETL/report generation:
spec completeness checks and mapping coverage validation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .docx_figures_tables import extract_figures_from_docx, extract_tables_from_docx
from .docx_sections import DocxSectionExtractor
from .mapping_loader import load_mapping
from .mapping_validate import validate_mapping_coverage
from .policy import DEFAULT_REQUIRED_SECTIONS
from .render_markdown import build_initial_checklist_rows
from .spec_checks import check_duplicates, check_required_sections
from .spec_models import DocxSpec, Finding


_ACTION_BY_CODE = {
    "SPEC_REQUIRED_SECTION_MISSING": "Adicionar a secao no DOCX ou ajustar a lista de secoes obrigatorias.",
    "SPEC_SECTION_DUPLICATE_TITLE": "Remover/renomear titulos repetidos no template DOCX.",
    "SPEC_SECTION_AMBIGUOUS_TITLE": "Padronizar os titulos para uma nomenclatura unica.",
    "CHECKLIST_ITEM_WITHOUT_MAPPING": "Adicionar requirement no YAML de mapping para o item do checklist.",
    "MAPPING_TARGET_MISSING": "Preencher target_field com schema.table.field.",
    "MAPPING_TARGET_NOT_NORMALIZED": "Normalizar target_field para schema.table.field.",
    "MAPPING_RULE_MISSING": "Definir calculation_rule para a metrica.",
    "MAPPING_SOURCES_MISSING": "Adicionar pelo menos uma fonte com source_id e location.",
    "MAPPING_VALIDATIONS_MISSING_DERIVED": "Adicionar validacoes minimas para metrica derivada.",
    "MAPPING_ITEM_NOT_IN_CHECKLIST": "Remover mapping orfao ou adicionar item correspondente no DOCX.",
}


def _build_spec(docx_path: Path) -> DocxSpec:
    """Extract a `DocxSpec` from DOCX path."""
    extractor = DocxSectionExtractor()
    sections = extractor.extract_sections(docx_path)
    figures = extract_figures_from_docx(docx_path, sections)
    tables = extract_tables_from_docx(docx_path)
    return DocxSpec(
        source_path=str(docx_path),
        extracted_at=datetime.now(timezone.utc),
        sections=sections,
        figures=figures,
        tables=tables,
    )


def _severity_rank(severity: str) -> int:
    """Return sorting priority for finding severity."""
    if severity == "error":
        return 0
    if severity == "warning":
        return 1
    return 2


def _sorted_findings(findings: Iterable[Finding]) -> List[Finding]:
    """Sort findings by severity, code and item for deterministic outputs."""
    return sorted(
        findings,
        key=lambda finding: (
            _severity_rank(finding.severity),
            finding.code,
            finding.item_docx.casefold(),
        ),
    )


def evaluate_spec_gate(
    docx_path: str | Path,
    mapping_path: str | Path,
    *,
    required_sections: Sequence[str] | None = None,
    default_schema: str = "public",
) -> Tuple[int, List[Finding]]:
    """Evaluate spec gate and return exit code plus consolidated findings.

    Args:
        docx_path: Path to DOCX template.
        mapping_path: Path to mapping YAML file.
        required_sections: Optional required section list for completeness check.
        default_schema: Default schema for mapping normalization.

    Returns:
        Tuple `(exit_code, findings)` where exit code is:
        - `0` when no `error` findings exist.
        - `1` when at least one `error` finding exists.

    Raises:
        FileNotFoundError: If DOCX or mapping YAML paths do not exist.
        ValueError: If extracted checklist is empty.
        MappingSchemaError: If mapping YAML is invalid.
    """
    docx = Path(docx_path)
    if not docx.exists():
        raise FileNotFoundError(f"DOCX not found: {docx}")

    spec = _build_spec(docx)
    checklist = build_initial_checklist_rows(spec)
    mapping = load_mapping(mapping_path, default_schema=default_schema)

    findings: List[Finding] = []
    required = tuple(required_sections) if required_sections is not None else DEFAULT_REQUIRED_SECTIONS
    findings.extend(check_required_sections(spec, required))
    findings.extend(check_duplicates(spec))
    findings.extend(validate_mapping_coverage(checklist, mapping))
    findings = _sorted_findings(findings)

    has_error = any(finding.severity == "error" for finding in findings)
    return (1 if has_error else 0, findings)


def run_spec_gate(
    docx_path: str | Path,
    mapping_path: str | Path,
    *,
    required_sections: Sequence[str] | None = None,
    default_schema: str = "public",
) -> int:
    """Run spec gate and return process-like exit code."""
    exit_code, _ = evaluate_spec_gate(
        docx_path,
        mapping_path,
        required_sections=required_sections,
        default_schema=default_schema,
    )
    return exit_code


def render_spec_gate_summary(findings: Sequence[Finding]) -> str:
    """Render actionable summary for gate findings."""
    total = len(findings)
    n_error = sum(1 for finding in findings if finding.severity == "error")
    n_warning = sum(1 for finding in findings if finding.severity == "warning")
    n_info = sum(1 for finding in findings if finding.severity == "info")

    lines: List[str] = []
    lines.append("Spec Gate Summary")
    lines.append(f"- Total findings: {total}")
    lines.append(f"- Errors: {n_error}")
    lines.append(f"- Warnings: {n_warning}")
    lines.append(f"- Infos: {n_info}")
    lines.append("")

    if not findings:
        lines.append("Status: PASS")
        lines.append("Nenhum finding critico detectado.")
        return "\n".join(lines)

    lines.append("Status: FAIL" if n_error > 0 else "Status: PASS_WITH_WARNINGS")
    lines.append("Acoes recomendadas por finding:")
    for finding in findings:
        action = _ACTION_BY_CODE.get(finding.code, "Revisar item e ajustar spec/mapping conforme regra.")
        reference = f" | referencia: {finding.reference}" if finding.reference else ""
        lines.append(
            f"- [{finding.severity}] {finding.code} | item: {finding.item_docx} | "
            f"mensagem: {finding.message} | como corrigir: {action}{reference}"
        )
    return "\n".join(lines)
