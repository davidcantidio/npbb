"""Validate contractual coherence around the shared lead ETL core."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _ensure_backend_on_path(project_root: Path) -> None:
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    backend_root = project_root / "backend"
    backend_str = str(backend_root)
    if backend_str not in sys.path:
        sys.path.insert(0, backend_str)


def _check_lead_row_contract() -> list[str]:
    from core.leads_etl.models import LEAD_ROW_EXCLUDED_FIELDS, LEAD_ROW_FIELDS, LeadRow
    from core.leads_etl.models._field_catalog import ETL_ALIAS_TO_LEAD_ROW_FIELD, LEGACY_COERCION_FIELDS

    violations: list[str] = []
    model_fields = tuple(LeadRow.model_fields.keys())
    catalog_fields = tuple(LEAD_ROW_FIELDS)

    if len(catalog_fields) != len(set(catalog_fields)):
        violations.append("LEAD_ROW_FIELDS contem campos duplicados.")

    if model_fields != catalog_fields:
        missing = [field for field in catalog_fields if field not in model_fields]
        extra = [field for field in model_fields if field not in catalog_fields]
        violations.append(
            "LeadRow diverge de LEAD_ROW_FIELDS "
            f"(missing={missing or '-'}, extra={extra or '-'})"
        )

    excluded = set(LEAD_ROW_EXCLUDED_FIELDS)
    overlap = sorted(set(catalog_fields).intersection(excluded))
    if overlap:
        violations.append(f"Campos excluidos aparecem no catalogo canonico: {overlap}")

    legacy_missing = sorted(set(LEGACY_COERCION_FIELDS) - set(catalog_fields))
    if legacy_missing:
        violations.append(f"LEGACY_COERCION_FIELDS referencia campos fora do catalogo: {legacy_missing}")

    alias_targets = sorted(
        {
            target
            for target in ETL_ALIAS_TO_LEAD_ROW_FIELD.values()
            if target not in set(catalog_fields)
        }
    )
    if alias_targets:
        violations.append(f"Alias ETL apontam para campos fora do catalogo canonico: {alias_targets}")

    return violations


def _check_backend_lead_alignment() -> list[str]:
    from app.models.models import Lead
    from app.schemas.lead_import_etl import ImportEtlCommitRequest
    from core.leads_etl.models import LEAD_ROW_EXCLUDED_FIELDS, LEAD_ROW_FIELDS

    violations: list[str] = []
    lead_fields = set(Lead.model_fields)
    catalog_fields = set(LEAD_ROW_FIELDS)
    excluded_fields = set(LEAD_ROW_EXCLUDED_FIELDS)

    if lead_fields != catalog_fields | excluded_fields:
        missing = sorted((catalog_fields | excluded_fields) - lead_fields)
        extra = sorted(lead_fields - (catalog_fields | excluded_fields))
        violations.append(
            "Lead.model_fields diverge do contrato canonico "
            f"(missing={missing or '-'}, extra={extra or '-'})"
        )

    commit_fields = set(ImportEtlCommitRequest.model_fields)
    for required in ("session_token", "evento_id", "force_warnings"):
        if required not in commit_fields:
            violations.append(f"ImportEtlCommitRequest nao expoe campo obrigatorio: {required}")

    return violations


def _check_router_and_frontend_contract(project_root: Path) -> list[str]:
    violations: list[str] = []

    router_path = project_root / "backend/app/routers/leads.py"
    router_text = router_path.read_text(encoding="utf-8")
    required_router_markers = ("force_warnings=payload.force_warnings",)
    for marker in required_router_markers:
        if marker not in router_text:
            violations.append(f"Router ETL commit nao propaga contrato esperado: {marker}")

    service_path = project_root / "frontend/src/services/leads_import.ts"
    service_text = service_path.read_text(encoding="utf-8-sig")
    required_service_markers = (
        "force_warnings: forceWarnings",
        "export async function commitLeadImportEtl(",
    )
    for marker in required_service_markers:
        if marker not in service_text:
            violations.append(f"Service ETL frontend nao propaga contrato esperado: {marker}")

    return violations


def collect_contract_violations(project_root: Path) -> list[str]:
    _ensure_backend_on_path(project_root)
    violations: list[str] = []
    violations.extend(_check_lead_row_contract())
    violations.extend(_check_backend_lead_alignment())
    violations.extend(_check_router_and_frontend_contract(project_root))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail when shared lead ETL contract drifts from canonical lead_row.py",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Repository root (defaults to parent directory of this script).",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    violations = collect_contract_violations(project_root)
    if violations:
        print("[lead-etl-contract] FAIL")
        for item in violations:
            print(f"- {item}")
        return 1

    print("[lead-etl-contract] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
