"""Core metric definitions for audience ruler and report contracts."""

from .calculators import (
    BB_SEGMENT_KEYS,
    MetricCalculationError,
    compute_comparecimento,
    compute_share_bb,
    safe_percent,
    validate_percent_bounds,
)
from .definitions import (
    AUDIENCE_MEASURE_USAGE,
    DERIVED_METRIC_TYPES,
    AudienceMeasure,
    MetricDefinitionError,
    MetricLabelContract,
    MetricType,
    audience_measure_usage_note,
)
from .guardrails import (
    GuardrailFinding,
    MetricGuardrailError,
    enforce_mart_metric_guardrails,
    validate_mart_metric_guardrails,
    validate_metric_type_required,
    validate_mixed_sources_labeled,
)

__all__ = [
    "MetricCalculationError",
    "safe_percent",
    "validate_percent_bounds",
    "compute_comparecimento",
    "BB_SEGMENT_KEYS",
    "compute_share_bb",
    "MetricType",
    "AudienceMeasure",
    "MetricLabelContract",
    "MetricDefinitionError",
    "DERIVED_METRIC_TYPES",
    "AUDIENCE_MEASURE_USAGE",
    "audience_measure_usage_note",
    "MetricGuardrailError",
    "GuardrailFinding",
    "validate_metric_type_required",
    "validate_mixed_sources_labeled",
    "validate_mart_metric_guardrails",
    "enforce_mart_metric_guardrails",
]
