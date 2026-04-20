"""Dedicated worker for ETL preview/commit and Gold pipeline jobs."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")

from app.db.database import build_worker_engine, set_internal_service_db_context
from app.modules.leads_publicidade.application.etl_import.job_service import (
    run_next_commit_job,
    run_next_preview_job,
)
from app.observability.import_events import log_import_event
from app.services.lead_pipeline_service import claim_next_gold_pipeline_batch, executar_pipeline_gold


logger = logging.getLogger("npbb.leads_worker")
WORKER_ENGINE = build_worker_engine()


def _idle_sleep_seconds() -> float:
    raw = os.getenv("LEADS_WORKER_IDLE_SLEEP_SECONDS", "2").strip()
    try:
        return max(float(raw), 0.2)
    except ValueError:
        return 2.0


def _failure_sleep_seconds() -> float:
    raw = os.getenv("LEADS_WORKER_FAILURE_SLEEP_SECONDS", "5").strip()
    try:
        return max(float(raw), 0.2)
    except ValueError:
        return 5.0


def _worker_health_file() -> Path:
    raw = os.getenv("LEADS_WORKER_HEALTH_FILE", "").strip()
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parents[1] / ".runtime" / "leads_worker_health.json"


def _write_worker_health(*, status: str, worked: bool, error: str | None = None) -> None:
    path = _worker_health_file()
    payload = {
        "status": status,
        "worked": worked,
        "last_seen_at": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    if error:
        payload["last_error"] = error[:500]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    except Exception:  # noqa: BLE001
        logger.exception("leads worker health write failed path=%s", path)


def _run_next_gold_pipeline_batch() -> bool:
    with Session(WORKER_ENGINE) as session:
        set_internal_service_db_context(session)
        batch_id = claim_next_gold_pipeline_batch(session)
    if not batch_id:
        return False
    asyncio.run(executar_pipeline_gold(batch_id))
    return True


def main() -> None:
    logging.basicConfig(level=os.getenv("LEADS_WORKER_LOG_LEVEL", "INFO").upper())
    idle_sleep = _idle_sleep_seconds()
    failure_sleep = _failure_sleep_seconds()
    log_import_event(logger, "worker.started", idle_sleep=idle_sleep, failure_sleep=failure_sleep)
    _write_worker_health(status="started", worked=False)
    while True:
        worked = False
        try:
            worked = run_next_preview_job() or worked
            worked = run_next_commit_job() or worked
            worked = _run_next_gold_pipeline_batch() or worked
            _write_worker_health(status="ok", worked=worked)
            if worked:
                log_import_event(logger, "worker.iteration", outcome="worked")
        except Exception:  # noqa: BLE001
            logger.exception("leads worker iteration failed")
            _write_worker_health(status="error", worked=False, error="iteration_failed")
            log_import_event(logger, "worker.iteration_failed", level=logging.ERROR, outcome="failed")
            time.sleep(failure_sleep)
            continue
        if not worked:
            time.sleep(idle_sleep)


if __name__ == "__main__":
    main()
