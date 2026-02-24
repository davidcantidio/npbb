"""Load TMJ 2025 staging artifacts into canonical tables (backend DB).

This script bridges local/offline extractors (npbb/etl/...) with the backend DB:
- reads evidence envelopes from the staging folder,
- registers the raw source in `source` (with file snapshot),
- creates an ingestion run,
- loads canonical tables for supported sources.

It does NOT generate the final Word report. The goal is to populate canonical + marts.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from sqlmodel import Session

from app.db.database import engine
from app.db.metadata import SQLModel
from app.models.models import IngestionStatus, SourceKind
from app.services.data_quality import upsert_ingestion_evidence
from app.services.ingestion_registry import FileSnapshot, finish_ingestion, register_source, start_ingestion
from app.services.tmj_canonical_load import (
    LoadResult,
    load_access_control_from_template_csv,
    load_festival_leads_from_staging_csv,
    load_optin_transactions_from_staging_csv,
)

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def _kind_from_path(path: Path) -> SourceKind:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return SourceKind.PDF
    if ext == ".xlsx":
        return SourceKind.XLSX
    if ext == ".pptx":
        return SourceKind.PPTX
    if ext == ".docx":
        return SourceKind.DOCX
    if ext == ".csv":
        return SourceKind.CSV
    return SourceKind.OTHER


def _snapshot_from_evidence(stats: dict) -> FileSnapshot | None:
    fs = (stats or {}).get("file_snapshot") or None
    if not isinstance(fs, dict):
        return None
    sha = fs.get("sha256")
    size = fs.get("size_bytes")
    mtime = fs.get("mtime_utc")
    if not (sha and size and mtime):
        return None
    return FileSnapshot(
        sha256=str(sha),
        size_bytes=int(size),
        mtime_utc=datetime.fromisoformat(str(mtime)),
    )


def _resolve_artifact_path(evidence: dict) -> Path | None:
    extractor = evidence.get("extractor") or ""
    stats = evidence.get("stats") or {}

    if extractor == "extract_xlsx_optin_aceitos":
        outputs = (stats.get("outputs") or {}) if isinstance(stats, dict) else {}
        csv_path = outputs.get("csv")
        return Path(str(csv_path)) if csv_path else None

    if extractor == "extract_xlsx_leads_festival":
        outputs = (stats.get("outputs") or {}) if isinstance(stats, dict) else {}
        csv_path = outputs.get("csv")
        return Path(str(csv_path)) if csv_path else None

    if extractor == "extract_pdf_assisted":
        artifact = stats.get("artifact")
        return Path(str(artifact)) if artifact else None

    return None


def _resolve_path(path: Path) -> Path:
    """Resolve a path that may be relative to:
    - workspace root (when it starts with 'npbb/'),
    - or current working directory (for local relative args like '..\\docs\\...').
    """
    if path.is_absolute():
        return path
    first = (path.parts[0] if path.parts else "").lower()
    base = WORKSPACE_ROOT if first == "npbb" else Path.cwd()
    return (base / path).resolve()


def _load_one(session: Session, *, evidence: dict, event_id: int | None) -> LoadResult:
    extractor = evidence.get("extractor") or ""
    source_id = evidence.get("source_id") or ""
    artifact = _resolve_artifact_path(evidence)
    if artifact is None:
        return LoadResult(rows_loaded=0, rows_skipped=0)

    if extractor == "extract_xlsx_optin_aceitos":
        return load_optin_transactions_from_staging_csv(
            session,
            csv_path=artifact,
            source_id=source_id,
            ingestion_id=None,  # patched by caller after ingestion is created
            event_id=event_id,
        )

    if extractor == "extract_xlsx_leads_festival":
        return load_festival_leads_from_staging_csv(
            session,
            csv_path=artifact,
            source_id=source_id,
            ingestion_id=None,  # patched by caller after ingestion is created
            event_id=event_id,
        )

    if extractor == "extract_pdf_assisted":
        # Only the access_control template is supported at this stage.
        template = (evidence.get("stats") or {}).get("template")
        if template != "access_control":
            return LoadResult(rows_loaded=0, rows_skipped=0)
        return load_access_control_from_template_csv(
            session,
            csv_path=artifact,
            source_id=source_id,
            ingestion_id=None,  # patched by caller after ingestion is created
            event_id=event_id,
        )

    return LoadResult(rows_loaded=0, rows_skipped=0)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--staging-dir",
        default=str(Path(__file__).resolve().parents[2] / "docs" / "analises" / "eventos" / "tamo_junto_2025" / "staging"),
    )
    ap.add_argument("--event-id", type=int, default=None, help="FK para evento.id (opcional).")
    ap.add_argument("--limit", type=int, default=0, help="Processar apenas N evidencias (debug).")
    args = ap.parse_args(argv)

    staging_dir = _resolve_path(Path(args.staging_dir))
    evidence_files = sorted(staging_dir.glob("evidence__*.json"))
    if args.limit and args.limit > 0:
        evidence_files = evidence_files[: int(args.limit)]

    if engine.url.drivername.startswith("sqlite"):
        SQLModel.metadata.create_all(engine)

    for ev_path in evidence_files:
        evidence = json.loads(ev_path.read_text(encoding="utf-8"))
        source_id = str(evidence.get("source_id") or "").strip()
        extractor = str(evidence.get("extractor") or "").strip()
        evidence_status = str(evidence.get("status") or "").strip()
        stats = evidence.get("stats") if isinstance(evidence.get("stats"), dict) else {}
        source_path_raw = Path(str(evidence.get("source_path") or ""))
        source_path = _resolve_path(source_path_raw)

        if not source_id or not source_path.exists():
            continue

        kind = _kind_from_path(source_path)
        snap = _snapshot_from_evidence(stats or {})

        with Session(engine) as session:
            register_source(
                session,
                source_id=source_id,
                kind=kind,
                uri=str(source_path),
                display_name=source_path.name,
                snapshot=snap,
            )

            run = start_ingestion(
                session,
                source_id=source_id,
                pipeline="tmj2025:canonical_load",
                snapshot=snap,
            )

            if extractor:
                upsert_ingestion_evidence(
                    session,
                    ingestion_id=run.id,
                    source_id=source_id,
                    extractor=extractor,
                    evidence_status=evidence_status,
                    stats=stats,
                    evidence_path=str(_resolve_path(ev_path)),
                )

            try:
                # Load canonical using the same session, now with ingestion_id set.
                artifact = _resolve_artifact_path(evidence)
                artifact = _resolve_path(artifact) if artifact else None

                if extractor == "extract_xlsx_optin_aceitos" and artifact:
                    res = load_optin_transactions_from_staging_csv(
                        session,
                        csv_path=artifact,
                        source_id=source_id,
                        ingestion_id=run.id,
                        event_id=args.event_id,
                    )
                elif extractor == "extract_xlsx_leads_festival" and artifact:
                    res = load_festival_leads_from_staging_csv(
                        session,
                        csv_path=artifact,
                        source_id=source_id,
                        ingestion_id=run.id,
                        event_id=args.event_id,
                    )
                elif extractor == "extract_pdf_assisted" and artifact:
                    template = (evidence.get("stats") or {}).get("template")
                    if template == "access_control":
                        res = load_access_control_from_template_csv(
                            session,
                            csv_path=artifact,
                            source_id=source_id,
                            ingestion_id=run.id,
                            event_id=args.event_id,
                        )
                    else:
                        res = LoadResult(rows_loaded=0, rows_skipped=0)
                else:
                    res = LoadResult(rows_loaded=0, rows_skipped=0)

                status = IngestionStatus.SUCCEEDED if res.rows_loaded >= 0 else IngestionStatus.SKIPPED
                finish_ingestion(
                    session,
                    ingestion_id=run.id,
                    status=status,
                    log_text=f"loaded={res.rows_loaded} skipped={res.rows_skipped}",
                )
            except Exception as exc:
                session.rollback()
                finish_ingestion(
                    session,
                    ingestion_id=run.id,
                    status=IngestionStatus.FAILED,
                    error_message=str(exc),
                )
                raise

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
