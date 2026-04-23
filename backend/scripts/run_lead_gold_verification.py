from __future__ import annotations

import argparse
import json

from sqlmodel import Session

from app.db.database import build_worker_engine, set_internal_service_db_context
from app.services.lead_gold_verification_service import run_gold_verification


def main() -> None:
    parser = argparse.ArgumentParser(description="Reprocessa leads persistidos com a verificacao Gold em modo ELT.")
    parser.add_argument("--batch-id", action="append", dest="batch_ids", type=int, default=None)
    parser.add_argument("--exclude-null-batch", action="store_true")
    parser.add_argument("--requested-by", type=int, default=None)
    parser.add_argument("--idempotency-key", type=str, default=None)
    parser.add_argument("--force-new-run", action="store_true")
    args = parser.parse_args()

    engine = build_worker_engine()
    with Session(engine) as session:
        set_internal_service_db_context(session)
        result = run_gold_verification(
            batch_ids=args.batch_ids,
            include_null_batch=not args.exclude_null_batch,
            requested_by=args.requested_by,
            idempotency_key=args.idempotency_key,
            force_new_run=args.force_new_run,
            session=session,
        )

    print(
        json.dumps(
            {
                "run_id": result.run_id,
                "technical_batch_ids": result.technical_batch_ids,
                "analyzed_rows": result.analyzed_rows,
                "valid_rows": result.valid_rows,
                "invalid_rows": result.invalid_rows,
                "duplicate_rows": result.duplicate_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
