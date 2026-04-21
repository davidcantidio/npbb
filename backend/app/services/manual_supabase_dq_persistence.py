"""Persist manual Supabase import pipeline DQ snapshots into `lead_batches`.

Used to align artifact outputs (`report.json`, manifests) with indexed columns
`gold_dq_*` and `pipeline_report` without overwriting existing worker snapshots.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlmodel import Session

from app.models.lead_batch import LeadBatch
from app.services.manual_supabase_frozen_batches import FROZEN_BATCH_SPECS

MANUAL_DQ_META_KEY = "manual_import_dq_persistence"
BATCH255_BATCH_ID = 255

# Mirrors `lead_pipeline.constants` / `QualityMetrics` field names.
_WARNING_CIDADE_FORA_MAPEAMENTO = "CIDADE_FORA_MAPEAMENTO"
_WARNING_DATA_NASCIMENTO_AUSENTE = "DATA_NASCIMENTO_AUSENTE"
_WARNING_DATA_NASCIMENTO_INVALIDA = "DATA_NASCIMENTO_INVALIDA"
_WARNING_DUPLICIDADE_CPF_EVENTO = "DUPLICIDADE_CPF_EVENTO"
_WARNING_LOCALIDADE_INVALIDA = "LOCALIDADE_INVALIDA"


def _zero_quality_metrics() -> dict[str, int]:
    return {
        "cpf_invalid_discarded": 0,
        "telefone_invalid": 0,
        "data_evento_invalid": 0,
        "data_nascimento_invalid": 0,
        "data_nascimento_missing": 0,
        "duplicidades_cpf_evento": 0,
        "cidade_fora_mapeamento": 0,
        "localidade_invalida": 0,
        "localidade_nao_resolvida": 0,
        "localidade_fora_brasil": 0,
        "localidade_cidade_uf_inconsistente": 0,
    }


def gold_dq_snapshot_from_report(
    report_data: dict[str, Any],
) -> tuple[int | None, dict[str, int] | None, int | None]:
    """Same contract as `_gold_dq_snapshot_from_report` in `lead_pipeline_service`."""

    if not report_data:
        return None, None, None

    totals = report_data.get("totals") or {}
    discarded_raw = totals.get("discarded_rows")
    discarded: int | None
    if discarded_raw is None:
        discarded = None
    else:
        discarded = int(discarded_raw)

    qm = report_data.get("quality_metrics")
    parsed: dict[str, int] = {}
    if isinstance(qm, dict):
        for key, val in qm.items():
            if isinstance(val, bool):
                continue
            if isinstance(val, (int, float)):
                parsed[str(key)] = int(val)
    issue_counts: dict[str, int] | None = parsed

    inv = report_data.get("invalid_records")
    inv_total: int | None
    if isinstance(inv, list):
        inv_total = len(inv)
    else:
        inv_total = None

    return discarded, issue_counts, inv_total


def batch_has_existing_dq_snapshot(batch: LeadBatch) -> bool:
    """Return True if we should skip persisting (worker or prior manual write)."""

    if batch.pipeline_report is not None:
        return True
    if batch.gold_dq_discarded_rows is not None:
        return True
    if batch.gold_dq_issue_counts is not None:
        return True
    if batch.gold_dq_invalid_records_total is not None:
        return True
    return False


def _filter_by_source_file(rows: list[Any], source_file: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        if str(item.get("source_file") or "").strip() == source_file:
            out.append(item)
    return out


def _row_coord(item: dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(item.get("source_file") or "").strip(),
        str(item.get("source_sheet") or "").strip(),
        int(item.get("source_row") or 0),
    )


def _increment_metrics_from_motivo(motivo: str, metrics: dict[str, int]) -> None:
    """Map motivo_rejeicao text to QualityMetrics-like keys (one row can hit several)."""

    normalized = motivo.strip()
    if not normalized:
        return
    parts = [p.strip() for p in normalized.replace(",", ";").split(";") if p.strip()]
    if len(parts) <= 1 and ";" not in motivo:
        parts = [normalized]

    joined_upper = ";".join(parts).upper()
    if "CPF_INVALIDO_DESCARTADO" in joined_upper or "CPF_INVALIDO" in joined_upper:
        metrics["cpf_invalid_discarded"] += 1
    if "TELEFONE_INVALIDO" in joined_upper:
        metrics["telefone_invalid"] += 1
    if "DATA_EVENTO_INVALIDA" in joined_upper:
        metrics["data_evento_invalid"] += 1
    if _WARNING_DUPLICIDADE_CPF_EVENTO in motivo or "DUPLICIDADE_CPF_EVENTO" in joined_upper:
        metrics["duplicidades_cpf_evento"] += 1
        return

    if _WARNING_DATA_NASCIMENTO_AUSENTE in motivo:
        metrics["data_nascimento_missing"] += 1
    elif _WARNING_DATA_NASCIMENTO_INVALIDA in motivo:
        metrics["data_nascimento_invalid"] += 1

    if _WARNING_CIDADE_FORA_MAPEAMENTO in motivo:
        metrics["cidade_fora_mapeamento"] += 1
    if _WARNING_LOCALIDADE_INVALIDA in motivo:
        metrics["localidade_invalida"] += 1


def _locality_metrics_from_issue(issue: str | None, metrics: dict[str, int]) -> None:
    if not issue:
        return
    metrics["localidade_invalida"] += 1
    if issue == "non_br":
        metrics["localidade_fora_brasil"] += 1
    elif issue == "cidade_uf_mismatch":
        metrics["localidade_cidade_uf_inconsistente"] += 1
    else:
        metrics["localidade_nao_resolvida"] += 1


def build_quality_metrics_for_source_file(
    full_report: dict[str, Any],
    source_file: str,
) -> dict[str, int]:
    """Rebuild per-file quality metrics from filtered pipeline report fragments."""

    metrics = _zero_quality_metrics()

    invalid_for_file = _filter_by_source_file(list(full_report.get("invalid_records") or []), source_file)
    invalid_keys = {_row_coord(item) for item in invalid_for_file}

    for item in invalid_for_file:
        motivo = str(item.get("motivo_rejeicao") or "")
        _increment_metrics_from_motivo(motivo, metrics)

    for item in _filter_by_source_file(list(full_report.get("data_nascimento_controle") or []), source_file):
        if _row_coord(item) in invalid_keys:
            continue
        issue = str(item.get("issue") or "")
        if issue == "missing":
            metrics["data_nascimento_missing"] += 1
        else:
            metrics["data_nascimento_invalid"] += 1

    for item in _filter_by_source_file(list(full_report.get("localidade_controle") or []), source_file):
        if _row_coord(item) in invalid_keys:
            continue
        _locality_metrics_from_issue(str(item.get("issue") or "").strip() or None, metrics)

    for item in _filter_by_source_file(list(full_report.get("cidade_fora_mapeamento_controle") or []), source_file):
        if _row_coord(item) in invalid_keys:
            continue
        metrics["cidade_fora_mapeamento"] += 1

    return metrics


def build_sliced_pipeline_report_for_source_file(
    full_report: dict[str, Any],
    *,
    source_file: str,
    raw_rows: int,
) -> dict[str, Any]:
    """Construct a per-file report slice compatible with `gold_dq_snapshot_from_report`."""

    sliced = deepcopy(full_report)
    inv = _filter_by_source_file(list(full_report.get("invalid_records") or []), source_file)
    discarded = len(inv)
    valid_rows = max(0, int(raw_rows) - discarded)

    sliced["invalid_records"] = inv
    sliced["data_nascimento_controle"] = _filter_by_source_file(
        list(full_report.get("data_nascimento_controle") or []),
        source_file,
    )
    sliced["localidade_controle"] = _filter_by_source_file(
        list(full_report.get("localidade_controle") or []),
        source_file,
    )
    sliced["cidade_fora_mapeamento_controle"] = _filter_by_source_file(
        list(full_report.get("cidade_fora_mapeamento_controle") or []),
        source_file,
    )
    sliced["quality_metrics"] = build_quality_metrics_for_source_file(full_report, source_file)
    sliced["totals"] = {
        "raw_rows": int(raw_rows),
        "valid_rows": valid_rows,
        "discarded_rows": discarded,
    }
    meta = {
        "source_file": source_file,
        "persisted_at": datetime.now(timezone.utc).isoformat(),
        "kind": "consolidated_manual_import_slice",
    }
    sliced[MANUAL_DQ_META_KEY] = meta
    return sliced


def load_manifest_files_list(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the `files` array from a manual export manifest."""

    files = manifest.get("files")
    if not isinstance(files, list):
        return []
    return [f for f in files if isinstance(f, dict)]


def manifest_raw_rows_for_file(manifest: dict[str, Any], file_name: str) -> int | None:
    for entry in load_manifest_files_list(manifest):
        if str(entry.get("file_name") or "").strip() == file_name:
            raw = entry.get("raw_rows")
            if raw is None:
                return None
            return int(raw)
    return None


def apply_dq_snapshot_to_batch(
    batch: LeadBatch,
    *,
    pipeline_report: dict[str, Any],
    discarded: int | None,
    issue_counts: dict[str, int] | None,
    invalid_total: int | None,
) -> None:
    """Write pipeline_report and gold_dq_* on the in-memory batch (caller commits)."""

    batch.pipeline_report = pipeline_report
    batch.gold_dq_discarded_rows = discarded
    batch.gold_dq_issue_counts = issue_counts
    batch.gold_dq_invalid_records_total = invalid_total


def persist_consolidated_manual_dq(
    session: Session,
    *,
    report_path: Path,
    manifest_path: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Persist per-batch slices from consolidated manual import report + manifest."""

    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    results: dict[str, Any] = {
        "updated": [],
        "skipped": [],
        "errors": [],
    }

    for spec in FROZEN_BATCH_SPECS:
        batch = session.get(LeadBatch, spec.batch_id)
        if batch is None:
            results["errors"].append({"batch_id": spec.batch_id, "error": "batch_not_found"})
            continue

        if batch_has_existing_dq_snapshot(batch):
            results["skipped"].append(
                {"batch_id": spec.batch_id, "file_name": spec.file_name, "reason": "existing_dq_snapshot"}
            )
            continue

        raw_rows = manifest_raw_rows_for_file(manifest, spec.file_name)
        if raw_rows is None:
            results["errors"].append(
                {"batch_id": spec.batch_id, "file_name": spec.file_name, "error": "manifest_raw_rows_missing"}
            )
            continue

        sliced = build_sliced_pipeline_report_for_source_file(
            report_data,
            source_file=spec.file_name,
            raw_rows=raw_rows,
        )
        disc, issues, inv_n = gold_dq_snapshot_from_report(sliced)

        if dry_run:
            results["updated"].append(
                {
                    "batch_id": spec.batch_id,
                    "file_name": spec.file_name,
                    "gold_dq_discarded_rows": disc,
                    "gold_dq_invalid_records_total": inv_n,
                    "dry_run": True,
                }
            )
            continue

        apply_dq_snapshot_to_batch(
            batch,
            pipeline_report=sliced,
            discarded=disc,
            issue_counts=issues,
            invalid_total=inv_n,
        )
        session.add(batch)
        results["updated"].append(
            {
                "batch_id": spec.batch_id,
                "file_name": spec.file_name,
                "gold_dq_discarded_rows": disc,
                "gold_dq_invalid_records_total": inv_n,
            }
        )

    if not dry_run and results["updated"]:
        session.commit()
    return results


def build_batch255_synthetic_report(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build pipeline_report JSON from batch-255 manifest summary."""

    summary = manifest.get("summary") or {}
    raw_rows = int(summary.get("raw_rows") or 0)
    final_rows = int(summary.get("final_rows") or 0)
    discarded = max(0, raw_rows - final_rows)

    qm: dict[str, int] = {
        "document_blank": int(summary.get("document_blank") or 0),
        "document_over_11": int(summary.get("document_over_11") or 0),
        "phone_blank_scientific": int(summary.get("phone_blank_scientific") or 0),
        "birth_date_blank": int(summary.get("birth_date_blank") or 0),
        "internal_duplicates_skipped": int(summary.get("internal_duplicates_skipped") or 0),
        "existing_conflicts_skipped": int(summary.get("existing_conflicts_skipped") or 0),
    }

    return {
        MANUAL_DQ_META_KEY: {
            "kind": "batch255_manual_import_manifest",
            "batch_id": BATCH255_BATCH_ID,
            "persisted_at": datetime.now(timezone.utc).isoformat(),
        },
        "totals": {
            "raw_rows": raw_rows,
            "valid_rows": final_rows,
            "discarded_rows": discarded,
        },
        "quality_metrics": qm,
        "invalid_records": [],
        "gate": {"status": "SYNTHETIC", "decision": "manual_manifest", "fail_reasons": [], "warnings": []},
    }


def persist_batch255_manual_dq(
    session: Session,
    *,
    manifest_path: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Persist synthetic DQ from batch 255 manifest."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    batch = session.get(LeadBatch, BATCH255_BATCH_ID)
    result: dict[str, Any] = {"updated": [], "skipped": [], "errors": []}

    if batch is None:
        result["errors"].append({"batch_id": BATCH255_BATCH_ID, "error": "batch_not_found"})
        return result

    if batch_has_existing_dq_snapshot(batch):
        result["skipped"].append(
            {"batch_id": BATCH255_BATCH_ID, "reason": "existing_dq_snapshot"},
        )
        return result

    synthetic = build_batch255_synthetic_report(manifest)
    disc, issues, inv_n = gold_dq_snapshot_from_report(synthetic)
    if inv_n is None:
        inv_n = disc
    elif disc is not None and inv_n == 0 and disc > 0:
        inv_n = disc

    if dry_run:
        result["updated"].append(
            {
                "batch_id": BATCH255_BATCH_ID,
                "gold_dq_discarded_rows": disc,
                "gold_dq_invalid_records_total": inv_n,
                "dry_run": True,
            }
        )
        return result

    apply_dq_snapshot_to_batch(
        batch,
        pipeline_report=synthetic,
        discarded=disc,
        issue_counts=issues,
        invalid_total=inv_n,
    )
    session.add(batch)
    session.commit()
    result["updated"].append(
        {
            "batch_id": BATCH255_BATCH_ID,
            "gold_dq_discarded_rows": disc,
            "gold_dq_invalid_records_total": inv_n,
        }
    )
    return result
