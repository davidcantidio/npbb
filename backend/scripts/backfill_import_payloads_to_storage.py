"""Move blobs legados (lead_batches.arquivo_bronze, lead_import_etl_job.file_blob) para object storage.

Idempotente: ignora linhas que ja tem ponteiro de storage preenchido.

Uso:
  python scripts/backfill_import_payloads_to_storage.py --dry-run
  python scripts/backfill_import_payloads_to_storage.py --limit 50
  python scripts/backfill_import_payloads_to_storage.py

Requer as mesmas variaveis de OBJECT_STORAGE_* que persist_batch_payload / persist_etl_job_payload.
Para producao: OBJECT_STORAGE_BACKEND=supabase e credenciais de Storage.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import and_, create_engine, func, or_
from sqlmodel import Session, col, select

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

for env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")

from app.db.database import get_worker_database_url  # noqa: E402
from app.models.lead_batch import LeadBatch  # noqa: E402
from app.models.lead_public_models import LeadImportEtlJob  # noqa: E402
from app.services.imports.payload_storage import (  # noqa: E402
    persist_batch_payload,
    persist_etl_job_payload,
)


def _engine():
    url = get_worker_database_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30"))},
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="So lista contagens e primeiros ids")
    parser.add_argument("--limit", type=int, default=0, help="Maximo de linhas por tabela (0 = sem limite)")
    args = parser.parse_args()

    engine = _engine()
    batch_filter = and_(
        LeadBatch.arquivo_bronze.is_not(None),
        or_(
            LeadBatch.bronze_storage_key.is_(None),
            LeadBatch.bronze_storage_key == "",
        ),
    )
    job_filter = and_(
        LeadImportEtlJob.file_blob.is_not(None),
        or_(
            LeadImportEtlJob.file_storage_key.is_(None),
            LeadImportEtlJob.file_storage_key == "",
        ),
    )

    with Session(engine) as session:
        n_batches = int(
            session.scalar(select(func.count()).select_from(LeadBatch).where(batch_filter)) or 0
        )
        n_jobs = int(
            session.scalar(select(func.count()).select_from(LeadImportEtlJob).where(job_filter)) or 0
        )
        print(f"lead_batches candidatos: {n_batches}")
        print(f"lead_import_etl_job candidatos: {n_jobs}")

        if args.dry_run:
            if n_batches:
                q_ids = select(LeadBatch.id).where(batch_filter).order_by(col(LeadBatch.id)).limit(10)
                ids = [row[0] for row in session.exec(q_ids).all()]
                print("primeiros batch_ids:", ids)
            if n_jobs:
                q_j = select(LeadImportEtlJob.job_id).where(job_filter).limit(10)
                jids = [row[0] for row in session.exec(q_j).all()]
                print("primeiros job_ids:", jids)
            return

        batch_q = select(LeadBatch).where(batch_filter).order_by(col(LeadBatch.id))
        job_q = select(LeadImportEtlJob).where(job_filter).order_by(col(LeadImportEtlJob.job_id))

        batches = session.exec(batch_q).all()
        jobs = session.exec(job_q).all()

        n_batch = 0
        for batch in batches:
            if args.limit and n_batch >= args.limit:
                break
            payload = batch.arquivo_bronze
            if not payload:
                continue
            persist_batch_payload(batch, payload, content_type=batch.bronze_content_type)
            session.add(batch)
            session.commit()
            n_batch += 1
            print(f"backfill lead_batches id={batch.id} bytes={len(payload)}")

        n_job = 0
        for job in jobs:
            if args.limit and n_job >= args.limit:
                break
            payload = job.file_blob
            if not payload:
                continue
            persist_etl_job_payload(job, payload, content_type=job.file_content_type)
            session.add(job)
            session.commit()
            n_job += 1
            print(f"backfill lead_import_etl_job job_id={job.job_id} bytes={len(payload)}")

        print(f"concluido: batches={n_batch} jobs={n_job}")


if __name__ == "__main__":
    main()
