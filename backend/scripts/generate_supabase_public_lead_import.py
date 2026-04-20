"""Generate manual-import CSV artifacts for `public.lead` using frozen batches."""

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

    from app.services.manual_supabase_lead_export import (
        DEFAULT_EXPORT_DATE,
        DEFAULT_LOTE_ID,
        EXPORT_MODES,
    )

    parser = argparse.ArgumentParser(
        description="Gera artefatos CSV de auditoria/import para public.lead."
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_DIR / "artifacts" / f"manual_supabase_import_{DEFAULT_EXPORT_DATE}"),
        help="Diretório onde os artefatos finais serão gravados.",
    )
    parser.add_argument(
        "--export-date",
        default=DEFAULT_EXPORT_DATE,
        help="Data textual usada no nome dos artefatos.",
    )
    parser.add_argument(
        "--lote-id",
        default=DEFAULT_LOTE_ID,
        help="Identificador lógico usado no run_pipeline consolidado.",
    )
    parser.add_argument(
        "--mode",
        default="delta",
        choices=EXPORT_MODES,
        help="Artefato principal gerado: delta, full ou both.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the manual export end-to-end."""

    from app.db.database import build_worker_engine, set_internal_service_db_context
    from app.services.manual_supabase_lead_export import run_manual_supabase_lead_export

    args = parse_args(argv)
    load_environment()

    output_dir = Path(args.output_dir).resolve()
    engine = build_worker_engine()
    with Session(engine) as session:
        set_internal_service_db_context(session)
        artifacts = run_manual_supabase_lead_export(
            db=session,
            output_dir=output_dir,
            export_date=str(args.export_date),
            lote_id=str(args.lote_id),
            mode=str(args.mode),
        )

    print(f"mode={artifacts.mode}")
    print(f"export_created_at={artifacts.export_created_at.isoformat()}")
    print(f"import_csv={artifacts.import_csv_path}")
    print(f"full_import_csv={artifacts.full_import_csv_path}")
    print(f"skipped_existing_csv={artifacts.skipped_existing_csv_path}")
    print(f"reconciliation_csv={artifacts.reconciliation_csv_path}")
    print(f"rejected_rows_csv={artifacts.rejected_rows_csv_path}")
    print(f"manifest={artifacts.manifest_path}")
    print(f"pipeline_output_dir={artifacts.pipeline_result.output_dir}")
    print(f"pipeline_status={artifacts.pipeline_result.status}")
    print(f"pipeline_decision={artifacts.pipeline_result.decision}")
    print(f"pipeline_exit_code={artifacts.pipeline_result.exit_code}")
    print(f"full_rows={artifacts.summary['full_rows']}")
    print(f"import_ready_rows={artifacts.summary['import_ready_rows']}")
    print(f"skipped_existing_rows={artifacts.summary['skipped_existing_rows']}")
    print(f"pipeline_rejected_rows={artifacts.summary['pipeline_rejected_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
