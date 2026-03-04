from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_collect_contract_violations():
    project_root = Path(__file__).resolve().parents[1]
    module_path = project_root / "scripts" / "check_lead_etl_contracts.py"
    spec = importlib.util.spec_from_file_location("check_lead_etl_contracts", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.collect_contract_violations


def test_lead_etl_contract_gate_passes_on_repo_contracts() -> None:
    project_root = Path(__file__).resolve().parents[1]
    collect_contract_violations = _load_collect_contract_violations()
    violations = collect_contract_violations(project_root)
    assert violations == []
