"""Prometheus metrics for lead import (upload validation, ETL preview, Gold pipeline)."""

from __future__ import annotations

import logging
import os
import secrets

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.services.imports.file_reader import ImportFileError

logger = logging.getLogger(__name__)

# Closed label sets to avoid cardinality explosions
_GOLD_PIPELINE_STEPS = frozenset(
    {
        "queued",
        "silver_csv",
        "source_adapt",
        "event_taxonomy",
        "normalize_rows",
        "dedupe",
        "contract_check",
        "write_outputs",
        "insert_leads",
        "run_pipeline",
        "persist_result",
        "execution_total",
        "unknown",
    }
)

upload_rejected_total = Counter(
    "npbb_lead_import_upload_rejected_total",
    "Upload validation failures (inspect_upload / ImportFileError codes)",
    ("code",),
)

etl_preview_row_rejections_total = Counter(
    "npbb_lead_etl_preview_row_rejections_total",
    "ETL preview rows classified by primary rejection reason",
    ("reason",),
)

gold_pipeline_stage_duration_seconds = Histogram(
    "npbb_lead_gold_pipeline_stage_duration_seconds",
    "Wall time spent in Gold pipeline stages (seconds)",
    ("step",),
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300, 600, 3600.0),
)

gold_pipeline_reclaimed_stale_total = Counter(
    "npbb_lead_gold_pipeline_reclaimed_stale_total",
    "Gold pipeline dispatch reclaimed a stale pending lock",
)


def _normalize_gold_step(step: str | None) -> str:
    s = (step or "").strip() or "unknown"
    return s if s in _GOLD_PIPELINE_STEPS else "unknown"


def inc_upload_rejected(code: str) -> None:
    upload_rejected_total.labels(code=str(code or "UNKNOWN")[:64]).inc()


def inc_etl_preview_rejection(reason: str) -> None:
    etl_preview_row_rejections_total.labels(reason=str(reason or "other")[:64]).inc()


def observe_gold_stage_duration_seconds(step: str, duration_seconds: float) -> None:
    gold_pipeline_stage_duration_seconds.labels(step=_normalize_gold_step(step)).observe(
        max(0.0, float(duration_seconds))
    )


def inc_gold_reclaimed_stale() -> None:
    gold_pipeline_reclaimed_stale_total.inc()


def record_import_upload_rejection(exc: ImportFileError, *, filename_hint: str | None = None) -> None:
    inc_upload_rejected(exc.code)
    try:
        from app.observability.import_events import log_import_event  # noqa: PLC0415

        log_import_event(
            logger,
            "upload.inspect_rejected",
            level=logging.INFO,
            outcome="rejected",
            code=exc.code,
            field=exc.field,
            filename_hint=(filename_hint or "")[:200] if filename_hint else None,
        )
    except Exception:  # noqa: BLE001
        logger.exception("record_import_upload_rejection logging failed")


def metrics_response_body() -> tuple[bytes, str]:
    data = generate_latest()
    return data, CONTENT_TYPE_LATEST


def metrics_token_configured() -> str | None:
    raw = os.getenv("NPBB_METRICS_SCRAPE_TOKEN", "").strip()
    return raw or None


def metrics_token_valid(provided: str | None) -> bool:
    expected = metrics_token_configured()
    if not expected:
        return False
    if not provided:
        return False
    return secrets.compare_digest(str(provided), expected)
