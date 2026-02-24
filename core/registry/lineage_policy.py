"""Lineage enforcement policy helpers for staging/canonical loaders.

This module centralizes policy evaluation to avoid datasets being loaded
without lineage when that is a hard requirement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence


LineageRequirement = Literal["required", "optional"]
LineageMissingSeverity = Literal["partial", "failed"]

LINEAGE_REQUIREMENTS: tuple[LineageRequirement, ...] = ("required", "optional")
LINEAGE_MISSING_SEVERITIES: tuple[LineageMissingSeverity, ...] = ("partial", "failed")


@dataclass(frozen=True)
class LineagePolicy:
    """Lineage validation policy bound to one dataset.

    Attributes:
        dataset_name: Human-readable dataset identifier (for error messages).
        requirement: Whether lineage is mandatory (`required`) or not (`optional`).
        missing_lineage_severity: Ingestion status to use when missing lineage is
            detected for required datasets.
        lineage_field: Field expected in records to carry lineage reference ID.
    """

    dataset_name: str
    requirement: LineageRequirement = "optional"
    missing_lineage_severity: LineageMissingSeverity = "partial"
    lineage_field: str = "lineage_ref_id"

    def __post_init__(self) -> None:
        """Validate policy values after initialization.

        Raises:
            ValueError: If any policy attribute has unsupported value.
        """

        if not (self.dataset_name or "").strip():
            raise ValueError("dataset_name vazio. Como corrigir: informar nome do dataset.")
        if self.requirement not in LINEAGE_REQUIREMENTS:
            raise ValueError(
                "requirement invalido. Como corrigir: usar requirement em {required, optional}."
            )
        if self.missing_lineage_severity not in LINEAGE_MISSING_SEVERITIES:
            raise ValueError(
                "missing_lineage_severity invalido. "
                "Como corrigir: usar severidade em {partial, failed}."
            )
        if not (self.lineage_field or "").strip():
            raise ValueError(
                "lineage_field vazio. Como corrigir: informar nome de campo valido."
            )


@dataclass(frozen=True)
class LineagePolicyResult:
    """Result of evaluating lineage coverage against one policy."""

    total_records: int
    missing_records: int
    missing_indices: tuple[int, ...]
    should_block: bool
    status_on_block: LineageMissingSeverity | None
    message: str


def _record_has_lineage(record: Any, lineage_field: str) -> bool:
    """Check whether a single record carries non-empty lineage reference.

    Args:
        record: Record instance (dict/object/pydantic-like).
        lineage_field: Name of the lineage field to inspect.

    Returns:
        True when record has lineage field with a positive integer-like value.
    """

    value = None
    if isinstance(record, dict):
        value = record.get(lineage_field)
    elif hasattr(record, lineage_field):
        value = getattr(record, lineage_field)
    elif hasattr(record, "model_dump"):
        dumped = record.model_dump()
        if isinstance(dumped, dict):
            value = dumped.get(lineage_field)

    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def evaluate_lineage_policy(records: Sequence[Any], *, policy: LineagePolicy) -> LineagePolicyResult:
    """Evaluate lineage coverage for a dataset according to one policy.

    Args:
        records: Sequence of staging/canonical records to evaluate.
        policy: Policy configuration for this dataset.

    Returns:
        `LineagePolicyResult` with missing counts, block decision and message.
    """

    missing_indices: list[int] = []
    for index, record in enumerate(records):
        if not _record_has_lineage(record, policy.lineage_field):
            missing_indices.append(index)

    total = len(records)
    missing = len(missing_indices)

    if policy.requirement == "optional":
        return LineagePolicyResult(
            total_records=total,
            missing_records=missing,
            missing_indices=tuple(missing_indices),
            should_block=False,
            status_on_block=None,
            message=(
                f"Linhagem opcional para dataset '{policy.dataset_name}'. "
                f"Registros sem linhagem: {missing}/{total}."
            ),
        )

    if missing == 0:
        return LineagePolicyResult(
            total_records=total,
            missing_records=0,
            missing_indices=tuple(),
            should_block=False,
            status_on_block=None,
            message=f"Linhagem obrigatoria atendida para dataset '{policy.dataset_name}'.",
        )

    return LineagePolicyResult(
        total_records=total,
        missing_records=missing,
        missing_indices=tuple(missing_indices),
        should_block=True,
        status_on_block=policy.missing_lineage_severity,
        message=(
            f"Dataset '{policy.dataset_name}' exige linhagem e possui "
            f"{missing}/{total} registros sem '{policy.lineage_field}'. "
            "Como corrigir: preencher lineage_ref_id para todos os registros "
            "antes do load, ou alterar a policy para optional quando permitido."
        ),
    )
