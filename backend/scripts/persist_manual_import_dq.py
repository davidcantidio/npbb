"""Persist manual Supabase import DQ snapshots from artifacts into `lead_batches`.

Examples (repo root):

  python backend/scripts/persist_manual_import_dq.py consolidated \\
    --report artifacts/manual_supabase_import_2026-04-20/_pipeline_output/manual_supabase_import_2026-04-20/report.json \\
    --manifest artifacts/manual_supabase_import_2026-04-20/supabase_public_lead_manifest_2026-04-20.json

  python backend/scripts/persist_manual_import_dq.py batch255 \\
    --manifest artifacts/manual_supabase_import_batch_255/supabase_public_lead_manifest_batch_255.json

Use ``--dry-run`` to list batches that would be updated without committing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = ROOT_DIR.parent
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DB_REQUIRE_SUPABASE_POOLER", "false")


def load_environment() -> None:
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return
    load_dotenv()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_cons = sub.add_parser("consolidated", help="Lote multi-arquivo (export manual consolidado).")
    p_cons.add_argument(
        "--report",
        required=True,
        type=Path,
        help="Caminho para report.json do pipeline (ex.: _pipeline_output/.../report.json).",
    )
    p_cons.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Caminho para supabase_public_lead_manifest_*.json.",
    )
    p_cons.add_argument(
        "--dry-run",
        action="store_true",
        help="Não grava no banco; apenas lista atualizações planejadas.",
    )

    p255 = sub.add_parser("batch255", help="Manifest sintético do batch 255.")
    p255.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Caminho para supabase_public_lead_manifest_batch_255.json.",
    )
    p255.add_argument(
        "--dry-run",
        action="store_true",
        help="Não grava no banco; apenas lista atualizações planejadas.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    from app.db.database import build_worker_engine, set_internal_service_db_context
    from app.services.manual_supabase_dq_persistence import (
        persist_batch255_manual_dq,
        persist_consolidated_manual_dq,
    )

    args = parse_args(argv)
    load_environment()

    engine = build_worker_engine()
    with Session(engine) as session:
        set_internal_service_db_context(session)
        if args.command == "consolidated":
            result = persist_consolidated_manual_dq(
                session,
                report_path=args.report.resolve(),
                manifest_path=args.manifest.resolve(),
                dry_run=args.dry_run,
            )
        elif args.command == "batch255":
            result = persist_batch255_manual_dq(
                session,
                manifest_path=args.manifest.resolve(),
                dry_run=args.dry_run,
            )
        else:
            raise SystemExit(2)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("errors"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
