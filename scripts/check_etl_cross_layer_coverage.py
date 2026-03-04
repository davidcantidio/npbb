"""Enforce minimum cross-layer ETL coverage required by F4 gate."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CoverageScenario:
    name: str
    path: str
    required_markers: tuple[str, ...]


REQUIRED_ANCHOR_FILES: tuple[str, ...] = (
    "backend/tests/test_lead_import_preview_xlsx.py",
    "backend/tests/test_leads_import_csv_smoke.py",
    "frontend/src/features/leads-import/__tests__/LeadImportPage.validation.test.tsx",
    "frontend/src/features/leads-import/hooks/__tests__/useLeadImportWorkflow.test.ts",
)


REQUIRED_SCENARIOS: tuple[CoverageScenario, ...] = (
    CoverageScenario(
        name="backend_etl_preview_endpoint",
        path="backend/tests/test_leads_import_etl_endpoint.py",
        required_markers=(
            "/leads/import/etl/preview",
            "ImportEtlPreviewResponse",
            "dq_report",
        ),
    ),
    CoverageScenario(
        name="backend_etl_commit_endpoint",
        path="backend/tests/test_leads_import_etl_endpoint.py",
        required_markers=(
            "/leads/import/etl/commit",
            "force_warnings",
            "ETL_COMMIT_BLOCKED",
        ),
    ),
    CoverageScenario(
        name="backend_usecase_extract_transform_validate_persist",
        path="backend/tests/test_leads_import_etl_usecases.py",
        required_markers=(
            "import_leads_with_etl",
            "commit_leads_with_etl",
            "select(Lead)",
        ),
    ),
    CoverageScenario(
        name="frontend_etl_service_contract",
        path="frontend/src/services/__tests__/leads_import_etl.test.ts",
        required_markers=(
            "previewLeadImportEtl",
            "commitLeadImportEtl",
            "force_warnings",
        ),
    ),
)


def collect_coverage_violations(project_root: Path) -> list[str]:
    violations: list[str] = []

    for relative_path in REQUIRED_ANCHOR_FILES:
        path = project_root / relative_path
        if not path.exists():
            violations.append(f"Arquivo-ancora ausente para cobertura cross-camada: {relative_path}")

    for scenario in REQUIRED_SCENARIOS:
        path = project_root / scenario.path
        if not path.exists():
            violations.append(f"Cenario {scenario.name} sem arquivo de teste: {scenario.path}")
            continue
        text = path.read_text(encoding="utf-8-sig")
        missing_markers = [marker for marker in scenario.required_markers if marker not in text]
        if missing_markers:
            violations.append(
                f"Cenario {scenario.name} sem marcadores obrigatorios em {scenario.path}: {missing_markers}"
            )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail if ETL cross-layer minimum coverage matrix is incomplete.",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Repository root (defaults to parent directory of this script).",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    violations = collect_coverage_violations(project_root)
    if violations:
        print("[etl-cross-layer-coverage] FAIL")
        for item in violations:
            print(f"- {item}")
        return 1

    print("[etl-cross-layer-coverage] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
