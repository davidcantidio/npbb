"""Dedicated worker for ETL preview/commit and Gold pipeline jobs."""

from __future__ import annotations

import asyncio
import logging
import os
import time

from sqlmodel import Session

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")

from app.db.database import build_worker_engine, set_internal_service_db_context
from app.modules.leads_publicidade.application.etl_import.job_service import (
    run_next_commit_job,
    run_next_preview_job,
)
from app.services.lead_pipeline_service import claim_next_gold_pipeline_batch, executar_pipeline_gold


logger = logging.getLogger("npbb.leads_worker")
WORKER_ENGINE = build_worker_engine()


def _idle_sleep_seconds() -> float:
    raw = os.getenv("LEADS_WORKER_IDLE_SLEEP_SECONDS", "2").strip()
    try:
        return max(float(raw), 0.2)
    except ValueError:
        return 2.0


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
    logger.info("leads worker started idle_sleep=%s", idle_sleep)
    while True:
        worked = False
        try:
            worked = run_next_preview_job() or worked
            worked = run_next_commit_job() or worked
            worked = _run_next_gold_pipeline_batch() or worked
        except Exception:  # noqa: BLE001
            logger.exception("leads worker iteration failed")
        if not worked:
            time.sleep(idle_sleep)


if __name__ == "__main__":
    main()
