"""Guardrails for mart metric labeling and source-mix discipline.

This module enforces two critical rules for report marts:
1) every metric row must include explicit `metric_type`;
2) mixed-source metrics must include source labels for auditability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .definitions import MetricType


class MetricGuardrailError(ValueError):
    """Raised when one or more mart guardrails are violated."""


@dataclass(frozen=True)
class GuardrailFinding:
    """One guardrail validation finding.

    Args:
        code: Stable finding code.
        message: Actionable finding message.
        row_index: Zero-based row index where violation was detected.
        metric_key: Metric identifier associated with the finding, when present.
    """

    code: str
    message: str
    row_index: int
    metric_key: str | None = None


def _as_clean_str(value: object | None) -> str:
    """Normalize one value into stripped string."""

    return str(value or "").strip()


def validate_metric_type_required(
    rows: Sequence[Mapping[str, object]],
    *,
    metric_type_field: str = "metric_type",
    metric_key_field: str = "metric_key",
) -> list[GuardrailFinding]:
    """Validate explicit metric type labeling for each mart row.

    Args:
        rows: Mart-like rows represented as mappings.
        metric_type_field: Field expected to store metric type label.
        metric_key_field: Field expected to store metric key.

    Returns:
        List of findings for missing/invalid metric type labels.
    """

    findings: list[GuardrailFinding] = []
    allowed_values = {member.value for member in MetricType}

    for idx, row in enumerate(rows):
        metric_key = _as_clean_str(row.get(metric_key_field)) or None
        raw_metric_type = _as_clean_str(row.get(metric_type_field)).lower()
        if not raw_metric_type:
            findings.append(
                GuardrailFinding(
                    code="METRIC_TYPE_MISSING",
                    message=(
                        "Linha de mart sem metric_type. Como corrigir: preencher "
                        f"campo {metric_type_field!r} com dominio controlado."
                    ),
                    row_index=idx,
                    metric_key=metric_key,
                )
            )
            continue

        if raw_metric_type not in allowed_values:
            findings.append(
                GuardrailFinding(
                    code="METRIC_TYPE_INVALID",
                    message=(
                        f"metric_type '{raw_metric_type}' invalido. Como corrigir: "
                        f"usar um dos valores {sorted(allowed_values)}."
                    ),
                    row_index=idx,
                    metric_key=metric_key,
                )
            )
    return findings


def validate_mixed_sources_labeled(
    rows: Sequence[Mapping[str, object]],
    *,
    metric_key_field: str = "metric_key",
    source_field: str = "source_name",
    source_label_field: str = "source_label",
) -> list[GuardrailFinding]:
    """Validate source labeling when one metric mixes multiple sources.

    Args:
        rows: Mart-like rows represented as mappings.
        metric_key_field: Metric identifier field.
        source_field: Source identifier/name field.
        source_label_field: Human-readable source label field.

    Returns:
        List of findings for unlabeled mixed-source metric rows.
    """

    findings: list[GuardrailFinding] = []
    grouped: dict[str, list[tuple[int, Mapping[str, object]]]] = {}

    for idx, row in enumerate(rows):
        metric_key = _as_clean_str(row.get(metric_key_field))
        if not metric_key:
            findings.append(
                GuardrailFinding(
                    code="METRIC_KEY_MISSING",
                    message=(
                        "Linha sem metric_key. Como corrigir: informar chave de metrica "
                        "antes de validar mistura de fontes."
                    ),
                    row_index=idx,
                )
            )
            continue
        grouped.setdefault(metric_key, []).append((idx, row))

    for metric_key, indexed_rows in grouped.items():
        unique_sources = {
            _as_clean_str(row.get(source_field))
            for _, row in indexed_rows
            if _as_clean_str(row.get(source_field))
        }
        if len(unique_sources) <= 1:
            continue
        for idx, row in indexed_rows:
            if _as_clean_str(row.get(source_label_field)):
                continue
            findings.append(
                GuardrailFinding(
                    code="MIXED_SOURCES_WITHOUT_LABEL",
                    message=(
                        "Metrica mistura multiplas fontes sem source_label. "
                        "Como corrigir: preencher rotulo de fonte para auditoria."
                    ),
                    row_index=idx,
                    metric_key=metric_key,
                )
            )
    return findings


def validate_mart_metric_guardrails(
    rows: Sequence[Mapping[str, object]],
    *,
    metric_type_field: str = "metric_type",
    metric_key_field: str = "metric_key",
    source_field: str = "source_name",
    source_label_field: str = "source_label",
) -> list[GuardrailFinding]:
    """Run all mart metric guardrails and return findings.

    Args:
        rows: Mart-like rows represented as mappings.
        metric_type_field: Field expected to store metric type label.
        metric_key_field: Metric identifier field.
        source_field: Source identifier/name field.
        source_label_field: Human-readable source label field.

    Returns:
        Combined list of guardrail findings.
    """

    findings: list[GuardrailFinding] = []
    findings.extend(
        validate_metric_type_required(
            rows,
            metric_type_field=metric_type_field,
            metric_key_field=metric_key_field,
        )
    )
    findings.extend(
        validate_mixed_sources_labeled(
            rows,
            metric_key_field=metric_key_field,
            source_field=source_field,
            source_label_field=source_label_field,
        )
    )
    return findings


def enforce_mart_metric_guardrails(
    rows: Sequence[Mapping[str, object]],
    *,
    metric_type_field: str = "metric_type",
    metric_key_field: str = "metric_key",
    source_field: str = "source_name",
    source_label_field: str = "source_label",
) -> None:
    """Raise when one or more mart metric guardrails fail.

    Args:
        rows: Mart-like rows represented as mappings.
        metric_type_field: Field expected to store metric type label.
        metric_key_field: Metric identifier field.
        source_field: Source identifier/name field.
        source_label_field: Human-readable source label field.

    Returns:
        None.

    Raises:
        MetricGuardrailError: If at least one guardrail finding exists.
    """

    findings = validate_mart_metric_guardrails(
        rows,
        metric_type_field=metric_type_field,
        metric_key_field=metric_key_field,
        source_field=source_field,
        source_label_field=source_label_field,
    )
    if not findings:
        return

    summary = "; ".join(
        f"{finding.code}@row{finding.row_index}"
        + (f"[{finding.metric_key}]" if finding.metric_key else "")
        for finding in findings
    )
    raise MetricGuardrailError(
        "Guardrails de metricas violados. Como corrigir: revisar rotulagem de "
        f"metric_type/source_label. Findings: {summary}"
    )

