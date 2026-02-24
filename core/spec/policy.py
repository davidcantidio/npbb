"""Versioning policy for DOCX template/spec governance.

This module defines:
- minimum supported schema versions,
- compatibility rules between template/spec versions,
- standard artifact paths used by the TMJ DOCX-as-spec workflow.

Compatibility rule:
- major version must match the minimum supported major,
- minor version must be greater than or equal to the minimum supported minor.
"""

from __future__ import annotations

import re
from typing import Tuple


SPEC_POLICY_VERSION = "1.0"
MIN_SUPPORTED_SPEC_SCHEMA_VERSION = "1.0"
MIN_SUPPORTED_MAPPING_SCHEMA_VERSION = "1.0"

DOCX_SPEC_ARTIFACT_PATH = "docs/analises/eventos/tamo_junto_2025/planning/00_docx_as_spec.md"
REQUIREMENTS_MAPPING_ARTIFACT_PATH = (
    "docs/analises/eventos/tamo_junto_2025/planning/03_requirements_to_schema_mapping.md"
)
SPEC_DIFF_MD_ARTIFACT_PATH = "docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.md"
SPEC_DIFF_JSON_ARTIFACT_PATH = "docs/analises/eventos/tamo_junto_2025/planning/00_spec_diff.json"
MAPPING_YAML_DEFAULT_PATH = "core/spec/mapping_schema.yml"

DEFAULT_REQUIRED_SECTIONS = (
    "Contexto do evento",
    "Objetivo do relatorio",
    "Publico do evento (controle de acesso - entradas validadas)",
    "Shows por dia (12/12, 13/12, 14/12)",
)

_VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)$")


def parse_major_minor(version: str) -> Tuple[int, int]:
    """Parse a `major.minor` version string.

    Args:
        version: Version string in `major.minor` format.

    Returns:
        Tuple `(major, minor)` as integers.

    Raises:
        ValueError: If version does not match `major.minor`.
    """
    value = (version or "").strip()
    match = _VERSION_RE.fullmatch(value)
    if not match:
        raise ValueError(f"Invalid version format '{version}'. Expected 'major.minor'.")
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    return major, minor


def is_spec_schema_version_supported(
    schema_version: str,
    *,
    min_supported: str = MIN_SUPPORTED_SPEC_SCHEMA_VERSION,
) -> bool:
    """Check whether a schema version is supported by policy.

    Args:
        schema_version: Candidate schema version (`major.minor`).
        min_supported: Minimum supported schema version (`major.minor`).

    Returns:
        True when schema version is compatible with policy, else False.

    Raises:
        ValueError: If either version is malformed.
    """
    major, minor = parse_major_minor(schema_version)
    min_major, min_minor = parse_major_minor(min_supported)
    if major != min_major:
        return False
    return minor >= min_minor


def change_process_steps() -> Tuple[str, ...]:
    """Return standard process steps for template/spec changes.

    Returns:
        Ordered tuple of operational steps used by maintainers.
    """
    return (
        "Atualizar o template DOCX candidato e manter a versao baseline para comparacao.",
        (
            "Executar spec:diff para gerar os artefatos "
            f"`{SPEC_DIFF_MD_ARTIFACT_PATH}` e `{SPEC_DIFF_JSON_ARTIFACT_PATH}`."
        ),
        (
            "Executar spec:extract para atualizar "
            f"`{DOCX_SPEC_ARTIFACT_PATH}`."
        ),
        (
            "Atualizar o YAML de mapping em "
            f"`{MAPPING_YAML_DEFAULT_PATH}` e revisar impactos de cobertura."
        ),
        (
            "Executar spec:render-mapping para atualizar "
            f"`{REQUIREMENTS_MAPPING_ARTIFACT_PATH}`."
        ),
        "Executar spec:gate e bloquear promocao quando houver findings de severidade error.",
    )
