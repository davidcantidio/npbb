"""Aggregate ETL preview rejections into stable reason buckets."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from .contracts import EtlPreviewRow
from .validators import INVALID_CPF_REASON, MALFORMED_EMAIL_REASON, MISSING_CPF_REASON


def _primary_bucket_for_errors(errors: list[str]) -> str:
    if not errors:
        return "unknown"
    blob = " ".join(errors).lower()
    if any(
        needle in blob
        for needle in (
            "field required",
            "input should be",
            "value error",
            "type_error",
            "validation error",
        )
    ):
        return "pydantic_validation"
    if "leadrow" in blob or "adapter" in blob:
        return "adapter_error"
    for err in errors:
        el = err.lower()
        if MALFORMED_EMAIL_REASON.lower() in el or ("email" in el and "malform" in el):
            return "email_malformed"
    for err in errors:
        el = err.lower()
        if MISSING_CPF_REASON.lower() in el or ("cpf" in el and "ausente" in el):
            return "cpf_missing"
    for err in errors:
        el = err.lower()
        if INVALID_CPF_REASON.lower() in el or ("cpf" in el and "inválido" in el):
            return "cpf_invalid"
    return "other"


def aggregate_rejection_reason_counts(rejected_rows: Iterable[EtlPreviewRow]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rejected_rows:
        counts[_primary_bucket_for_errors(list(row.errors))] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def record_etl_preview_rejection_metrics(rejected_rows: Iterable[EtlPreviewRow]) -> None:
    from app.observability.prometheus_leads_import import inc_etl_preview_rejection  # noqa: PLC0415

    for row in rejected_rows:
        inc_etl_preview_rejection(_primary_bucket_for_errors(list(row.errors)))
