"""One-off: mapeamento sugerido + inferência + Gold para batch 240."""
from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")

from dotenv import load_dotenv
from lead_pipeline.constants import ALL_COLUMNS, HEADER_SYNONYMS
from lead_pipeline.normalization import canonicalize_header, normalize_header
from sqlmodel import Session

from app.db.database import build_worker_engine, set_internal_service_db_context
from app.models.lead_batch import LeadBatch
from app.services.lead_mapping import mapear_batch, suggest_column_mapping
from app.services.lead_pipeline_service import executar_pipeline_gold

CAN = frozenset(ALL_COLUMNS)
BATCH_ID = 240
USER_ID = 1


def _infer_field(header: str, campo_sugerido: str | None) -> str | None:
    if campo_sugerido and campo_sugerido in CAN:
        return campo_sugerido
    n = normalize_header(header)
    if n in CAN:
        return n
    c = canonicalize_header(header)
    if c in CAN:
        return c
    syn = HEADER_SYNONYMS.get(c)
    if syn and syn in CAN:
        return syn
    return None


def _build_mapeamento(batch_id: int, db: Session) -> tuple[dict[str, str], int]:
    suggestions = suggest_column_mapping(batch_id, db)
    mapeamento: dict[str, str] = {}
    used_targets: set[str] = set()
    for s in suggestions:
        if not s.coluna_original:
            continue
        target = _infer_field(s.coluna_original, s.campo_sugerido)
        if not target:
            continue
        if target in used_targets:
            continue
        used_targets.add(target)
        mapeamento[s.coluna_original] = target
    return mapeamento, len(mapeamento)


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    root = Path(__file__).resolve().parents[1]
    local_root = os.getenv("OBJECT_STORAGE_LOCAL_ROOT", "").strip()
    if not local_root or not Path(local_root).is_absolute():
        os.environ["OBJECT_STORAGE_LOCAL_ROOT"] = str(root / ".local-storage")

    engine = build_worker_engine()
    with Session(engine) as s:
        set_internal_service_db_context(s)
        batch = s.get(LeadBatch, BATCH_ID)
        if not batch:
            raise SystemExit(f"Lote {BATCH_ID} nao encontrado")
        evento_id = batch.evento_id
        if not evento_id:
            raise SystemExit("Lote sem evento_id; associe um evento antes do mapeamento.")

        mapeamento, n = _build_mapeamento(BATCH_ID, s)
        print(f"MAPEAMENTO ({n} colunas): {mapeamento}")
        if not mapeamento:
            raise SystemExit("Mapeamento vazio; revise cabecalhos ou storage Bronze.")

        result = mapear_batch(
            batch_id=BATCH_ID,
            evento_id=int(evento_id),
            mapeamento=mapeamento,
            user_id=USER_ID,
            db=s,
        )
        print(f"MAPEAR_OK silver_count={result.silver_count} stage={result.stage}")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    asyncio.run(executar_pipeline_gold(BATCH_ID))
    print("GOLD_PIPELINE_DONE")


if __name__ == "__main__":
    main()
