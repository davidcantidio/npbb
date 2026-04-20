"""Verification helpers for manual Supabase lead import audits."""

from __future__ import annotations

from dataclasses import dataclass
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.lead_public_models import Lead
from app.services.manual_supabase_lead_export import (
    LEAD_IMPORT_COLUMNS,
    build_ticketing_key,
    iter_chunks,
    normalize_ticketing_value,
    write_csv,
)

VerificationStatus = Literal["ok", "partial", "wrong_target_or_empty"]


@dataclass(frozen=True)
class VerificationRow:
    """CSV row plus lookup keys used against `public.lead`."""

    csv_row: dict[str, str]
    id_salesforce: str | None
    dedupe_key: str | None


@dataclass(frozen=True)
class VerificationArtifacts:
    """Verification outputs for a post-import audit run."""

    output_dir: Path
    verification_json_path: Path
    missing_rows_csv_path: Path
    status: VerificationStatus
    summary: dict[str, Any]


class ManualSupabaseLeadVerificationError(RuntimeError):
    """Raised when the verification inputs are incomplete or invalid."""


def read_verification_rows(path: Path) -> list[VerificationRow]:
    """Read a CSV in `public.lead` schema and build lookup keys."""

    rows: list[VerificationRow] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for csv_row in reader:
            normalized_row = {
                column: str(csv_row.get(column) or "")
                for column in reader.fieldnames or csv_row.keys()
            }
            id_salesforce = normalize_ticketing_value(normalized_row.get("id_salesforce")) or None
            dedupe_key = build_ticketing_key(
                email=normalized_row.get("email"),
                cpf=normalized_row.get("cpf"),
                evento_nome=normalized_row.get("evento_nome"),
                sessao=normalized_row.get("sessao"),
            )
            rows.append(
                VerificationRow(
                    csv_row=normalized_row,
                    id_salesforce=id_salesforce,
                    dedupe_key=dedupe_key,
                )
            )
    return rows


def fetch_existing_lookup_sets(
    db: Session,
    *,
    rows: list[VerificationRow],
) -> tuple[int, set[str], set[str]]:
    """Fetch target-db lookup sets for all verification rows."""

    lead_count = int(db.exec(select(func.count()).select_from(Lead)).one())
    incoming_ids = [row.id_salesforce for row in rows if row.id_salesforce]
    incoming_cpfs = [
        normalize_ticketing_value(row.csv_row.get("cpf"))
        for row in rows
        if normalize_ticketing_value(row.csv_row.get("cpf"))
    ]

    existing_id_salesforce: set[str] = set()
    for chunk in iter_chunks(incoming_ids):
        stmt = select(Lead.id_salesforce).where(Lead.id_salesforce.in_(chunk))
        for value in db.exec(stmt):
            normalized = normalize_ticketing_value(value)
            if normalized:
                existing_id_salesforce.add(normalized)

    existing_ticketing_keys: set[str] = set()
    for chunk in iter_chunks(incoming_cpfs):
        stmt = (
            select(Lead.email, Lead.cpf, Lead.evento_nome, Lead.sessao)
            .where(Lead.cpf.in_(chunk))
        )
        for email, cpf, evento_nome, sessao in db.exec(stmt):
            key = build_ticketing_key(
                email=email,
                cpf=cpf,
                evento_nome=evento_nome,
                sessao=sessao,
            )
            if key is not None:
                existing_ticketing_keys.add(key)

    return lead_count, existing_id_salesforce, existing_ticketing_keys


def split_rows_by_presence(
    rows: list[VerificationRow],
    *,
    existing_id_salesforce: set[str],
    existing_ticketing_keys: set[str],
) -> tuple[list[VerificationRow], list[VerificationRow]]:
    """Split verification rows into present and missing groups."""

    present: list[VerificationRow] = []
    missing: list[VerificationRow] = []
    for row in rows:
        matched = False
        if row.id_salesforce and row.id_salesforce in existing_id_salesforce:
            matched = True
        if row.dedupe_key and row.dedupe_key in existing_ticketing_keys:
            matched = True
        if matched:
            present.append(row)
        else:
            missing.append(row)
    return present, missing


def load_optional_rows(path_value: str | None) -> list[VerificationRow]:
    """Read an optional CSV path from the manifest when present."""

    if not path_value:
        return []
    path = Path(path_value)
    if not path.exists():
        return []
    return read_verification_rows(path)


def build_missing_rows_payload(rows: list[VerificationRow]) -> list[dict[str, str]]:
    """Return CSV rows for accepted rows still absent from the current DB."""

    return [
        {"verification_reason": "missing_in_current_db", **{k: row.csv_row.get(k, "") for k in LEAD_IMPORT_COLUMNS}}
        for row in rows
    ]


def verify_manual_supabase_lead_import(
    *,
    db: Session,
    accepted_csv_path: Path,
    manifest_path: Path,
    output_dir: Path,
) -> VerificationArtifacts:
    """Verify whether accepted rows from a full CSV are present in the current DB target."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    export_date = str(manifest.get("export_date") or datetime.now(timezone.utc).date())
    accepted_rows = read_verification_rows(accepted_csv_path)
    artifacts = manifest.get("artifacts") or {}
    delta_rows = load_optional_rows(artifacts.get("import_csv_path"))
    already_existing_rows = load_optional_rows(artifacts.get("skipped_existing_csv_path"))

    lookup_rows = accepted_rows + delta_rows + already_existing_rows
    lead_count, existing_ids, existing_ticketing_keys = fetch_existing_lookup_sets(
        db,
        rows=lookup_rows,
    )

    accepted_present, accepted_missing = split_rows_by_presence(
        accepted_rows,
        existing_id_salesforce=existing_ids,
        existing_ticketing_keys=existing_ticketing_keys,
    )
    delta_present, delta_missing = split_rows_by_presence(
        delta_rows,
        existing_id_salesforce=existing_ids,
        existing_ticketing_keys=existing_ticketing_keys,
    )
    already_existing_present, already_existing_missing = split_rows_by_presence(
        already_existing_rows,
        existing_id_salesforce=existing_ids,
        existing_ticketing_keys=existing_ticketing_keys,
    )

    manifest_summary = manifest.get("summary") or {}
    expected_preexisting_rows = int(manifest_summary.get("already_existing_pre_export_rows") or 0)
    if lead_count == 0:
        status: VerificationStatus = "wrong_target_or_empty"
    elif expected_preexisting_rows > 0 and not already_existing_present:
        status = "wrong_target_or_empty"
    elif accepted_missing:
        status = "partial"
    else:
        status = "ok"

    output_dir.mkdir(parents=True, exist_ok=True)
    verification_json_path = (
        output_dir / f"supabase_public_lead_post_import_verification_{export_date}.json"
    )
    missing_rows_csv_path = output_dir / f"supabase_public_lead_missing_in_db_{export_date}.csv"

    write_csv(
        missing_rows_csv_path,
        fieldnames=["verification_reason", *LEAD_IMPORT_COLUMNS],
        rows=build_missing_rows_payload(accepted_missing),
    )

    summary = {
        "export_date": export_date,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "accepted_csv_path": str(accepted_csv_path),
        "manifest_path": str(manifest_path),
        "status": status,
        "database_lead_count": lead_count,
        "accepted_rows_total": len(accepted_rows),
        "accepted_rows_present_now": len(accepted_present),
        "accepted_rows_missing_now": len(accepted_missing),
        "delta_rows_total": len(delta_rows),
        "delta_rows_present_now": len(delta_present),
        "delta_rows_missing_now": len(delta_missing),
        "already_existing_pre_export_rows_total": len(already_existing_rows),
        "already_existing_pre_export_rows_present_now": len(already_existing_present),
        "already_existing_pre_export_rows_missing_now": len(already_existing_missing),
        "manifest_full_rows": int(manifest_summary.get("full_rows") or 0),
        "manifest_import_ready_rows": int(manifest_summary.get("import_ready_rows") or 0),
        "manifest_skipped_existing_rows": int(manifest_summary.get("skipped_existing_rows") or 0),
        "missing_rows_csv_path": str(missing_rows_csv_path),
    }
    verification_json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return VerificationArtifacts(
        output_dir=output_dir,
        verification_json_path=verification_json_path,
        missing_rows_csv_path=missing_rows_csv_path,
        status=status,
        summary=summary,
    )
