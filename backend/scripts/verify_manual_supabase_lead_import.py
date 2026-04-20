"""Verify whether a manual Supabase lead import is present in the current DB target."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

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
    """Load `backend/.env` when available."""

    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        return
    load_dotenv()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Verifica se o CSV aceito já está refletido no public.lead atual."
    )
    parser.add_argument(
        "--accepted-csv",
        required=True,
        help="CSV full com todas as pipeline_accepted_rows.",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Manifesto JSON gerado pelo export manual.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Diretório onde os artefatos de verificação serão gravados.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the verification against the currently configured database target."""

    from app.db.database import build_worker_engine, set_internal_service_db_context
    from app.services.manual_supabase_lead_verification import verify_manual_supabase_lead_import

    args = parse_args(argv)
    load_environment()

    engine = build_worker_engine()
    with Session(engine) as session:
        set_internal_service_db_context(session)
        artifacts = verify_manual_supabase_lead_import(
            db=session,
            accepted_csv_path=Path(args.accepted_csv).resolve(),
            manifest_path=Path(args.manifest).resolve(),
            output_dir=Path(args.output_dir).resolve(),
        )

    print(f"status={artifacts.status}")
    print(f"verification_json={artifacts.verification_json_path}")
    print(f"missing_rows_csv={artifacts.missing_rows_csv_path}")
    print(f"database_lead_count={artifacts.summary['database_lead_count']}")
    print(f"accepted_rows_total={artifacts.summary['accepted_rows_total']}")
    print(f"accepted_rows_present_now={artifacts.summary['accepted_rows_present_now']}")
    print(f"accepted_rows_missing_now={artifacts.summary['accepted_rows_missing_now']}")
    print(
        "already_existing_pre_export_rows_present_now="
        f"{artifacts.summary['already_existing_pre_export_rows_present_now']}"
    )
    if artifacts.status == "ok":
        return 0
    if artifacts.status == "partial":
        return 2
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
