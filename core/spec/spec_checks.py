"""Completeness and consistency checks for extracted DOCX specs.

These checks are designed for template-governance gates, helping detect
accidental omissions or ambiguous section titles before downstream ETL/report
steps run.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Sequence

from .spec_models import (
    Finding,
    DocxSpec,
    SPEC_REQUIRED_SECTION_MISSING,
    SPEC_SECTION_AMBIGUOUS_TITLE,
    SPEC_SECTION_DUPLICATE_TITLE,
)


_LEADING_NUMBERING_RE = re.compile(r"^\s*\d+(?:\.\d+)*\s*[\).:-]?\s*")
_MULTISPACE_RE = re.compile(r"\s+")


def _normalize_title(title: str) -> str:
    """Normalize section titles for stable matching and ambiguity detection."""
    clean = (title or "").strip()
    clean = _LEADING_NUMBERING_RE.sub("", clean)
    clean = _MULTISPACE_RE.sub(" ", clean)
    clean = clean.strip(" -:;,.")
    return clean.casefold()


def check_required_sections(spec: DocxSpec, required_sections: Sequence[str]) -> List[Finding]:
    """Check whether required sections are present in extracted DOCX spec.

    Args:
        spec: Extracted DOCX specification.
        required_sections: Configurable list of required section titles.

    Returns:
        Findings list with one `error` per missing required section.
    """
    findings: List[Finding] = []
    normalized_existing = {_normalize_title(section.title) for section in spec.sections if section.title.strip()}

    for required in required_sections:
        required_clean = required.strip()
        if not required_clean:
            continue
        if _normalize_title(required_clean) in normalized_existing:
            continue
        findings.append(
            Finding(
                severity="error",
                code=SPEC_REQUIRED_SECTION_MISSING,
                item_docx=required_clean,
                message="Secao obrigatoria ausente no spec extraido.",
                reference=f"required_sections:{required_clean}",
            )
        )
    return findings


def check_duplicates(spec: DocxSpec) -> List[Finding]:
    """Detect duplicated and ambiguous section titles in extracted spec.

    Duplicate title:
    - same normalized title appears more than once with same canonical text.
    Ambiguous title:
    - same normalized title appears with different raw variants.

    Args:
        spec: Extracted DOCX specification.

    Returns:
        Findings list with `error` for duplicates and `warning` for ambiguities.
    """
    findings: List[Finding] = []
    by_normalized: Dict[str, List[str]] = defaultdict(list)
    for section in spec.sections:
        raw_title = (section.title or "").strip()
        if not raw_title:
            continue
        by_normalized[_normalize_title(raw_title)].append(raw_title)

    for normalized, raw_titles in by_normalized.items():
        if len(raw_titles) <= 1:
            continue

        canonical_titles = sorted({title.casefold() for title in raw_titles})
        if len(canonical_titles) == 1:
            findings.append(
                Finding(
                    severity="error",
                    code=SPEC_SECTION_DUPLICATE_TITLE,
                    item_docx=raw_titles[0],
                    message=f"Titulo repetido {len(raw_titles)} vezes no DOCX.",
                    reference=f"normalized={normalized}",
                )
            )
            continue

        variants = "; ".join(sorted(set(raw_titles)))
        findings.append(
            Finding(
                severity="warning",
                code=SPEC_SECTION_AMBIGUOUS_TITLE,
                item_docx=raw_titles[0],
                message="Titulos ambiguos detectados para o mesmo item normalizado.",
                reference=variants,
            )
        )

    return findings
