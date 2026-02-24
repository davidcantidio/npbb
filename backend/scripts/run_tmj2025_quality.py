"""Run TMJ 2025 data quality checks and persist results.

Typical usage (local):
  Set-Location npbb\\backend
  $env:DATABASE_URL="sqlite:///./app.db"
  python -m scripts.run_tmj2025_quality --staging-dir \"..\\docs\\analises\\eventos\\tamo_junto_2025\\staging\"

The script:
- reads extractor evidence envelopes from the staging directory,
- links each evidence file to an ingestion run (by source_id + file_sha256),
- persists an evidence summary (layout signature) into `ingestion_evidence`,
- runs quality checks for the linked ingestion_id,
- optionally exits non-zero when the quality gate is blocked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlmodel import Session, select

from app.db.database import engine
from app.db.metadata import SQLModel
from app.models.models import IngestionRun
from app.services.data_quality import (
    quality_gate_blocked,
    quality_summary,
    run_quality_checks_for_ingestion,
    upsert_ingestion_evidence,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    first = (path.parts[0] if path.parts else "").lower()
    base = WORKSPACE_ROOT if first == "npbb" else Path.cwd()
    return (base / path).resolve()


def _find_ingestion_id(session: Session, *, source_id: str, file_sha256: str | None) -> int | None:
    if file_sha256:
        row = session.exec(
            select(IngestionRun)
            .where(IngestionRun.source_id == source_id)
            .where(IngestionRun.file_sha256 == file_sha256)
            .order_by(IngestionRun.started_at.desc())
            .limit(1)
        ).first()
        if row is not None:
            return int(row.id)

    row = session.exec(
        select(IngestionRun)
        .where(IngestionRun.source_id == source_id)
        .order_by(IngestionRun.started_at.desc())
        .limit(1)
    ).first()
    return int(row.id) if row is not None else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--staging-dir",
        default=str(
            Path(__file__).resolve().parents[2]
            / "docs"
            / "analises"
            / "eventos"
            / "tamo_junto_2025"
            / "staging"
        ),
    )
    ap.add_argument("--source-id", default="", help="Filtrar por source_id (opcional).")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--fail-on-error", action="store_true")
    args = ap.parse_args(argv)

    staging_dir = _resolve_path(Path(args.staging_dir))
    evidence_files = sorted(staging_dir.glob("evidence__*.json"))
    if args.source_id:
        evidence_files = [p for p in evidence_files if args.source_id.upper() in p.name.upper()]
    if args.limit and args.limit > 0:
        evidence_files = evidence_files[: int(args.limit)]

    if engine.url.drivername.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)

    blocked_any = False
    with Session(engine) as session:
        for ev_path in evidence_files:
            evidence = json.loads(ev_path.read_text(encoding="utf-8"))
            source_id = str(evidence.get("source_id") or "").strip()
            extractor = str(evidence.get("extractor") or "").strip()
            ev_status = str(evidence.get("status") or "").strip()
            stats = evidence.get("stats") if isinstance(evidence.get("stats"), dict) else {}
            file_sha = None
            fs = stats.get("file_snapshot") if isinstance(stats, dict) else None
            if isinstance(fs, dict):
                file_sha = fs.get("sha256")

            if not source_id or not extractor:
                continue

            ingestion_id = _find_ingestion_id(session, source_id=source_id, file_sha256=str(file_sha) if file_sha else None)
            if ingestion_id is None:
                # No ingestion run in DB yet.
                continue

            upsert_ingestion_evidence(
                session,
                ingestion_id=ingestion_id,
                source_id=source_id,
                extractor=extractor,
                evidence_status=ev_status,
                stats=stats,
                evidence_path=str(_resolve_path(ev_path)),
            )

            run_quality_checks_for_ingestion(session, ingestion_id=ingestion_id)
            gate = quality_gate_blocked(session, ingestion_id=ingestion_id)
            if gate:
                blocked_any = True

            counts = quality_summary(session, ingestion_id=ingestion_id)
            print(
                f"[DQ] source={source_id} ingestion={ingestion_id} blocked={gate} "
                f"error_fail={counts['error_fail']} warn_fail={counts['warn_fail']} total={counts['total']}"
            )

    if args.fail_on_error and blocked_any:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

