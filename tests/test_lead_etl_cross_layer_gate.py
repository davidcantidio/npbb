from __future__ import annotations

from pathlib import Path

from scripts.check_etl_cross_layer_coverage import collect_coverage_violations


def test_lead_etl_cross_layer_coverage_gate_passes_on_repo_matrix() -> None:
    project_root = Path(__file__).resolve().parents[1]
    violations = collect_coverage_violations(project_root)
    assert violations == []
