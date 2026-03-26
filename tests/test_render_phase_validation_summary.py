from __future__ import annotations

import json
from pathlib import Path

from scripts.render_phase_validation_summary import build_summary


LEAD_FEATURE_DIRS = (
    "FEATURE-1-NUCLEO-ETL",
    "FEATURE-2-INTEGRACAO-BACKEND",
    "FEATURE-3-REFATORACAO-CLI",
    "FEATURE-4-UI-IMPORTACAO-AVANCADA",
)


def _write_feature(path: Path, *, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            (
                "---",
                f'doc_id: "{path.stem}"',
                'version: "1.0"',
                f'status: "{status}"',
                'owner: "PM"',
                'last_updated: "2026-03-03"',
                "---",
                "",
                f"# {path.stem}",
                "",
            )
        ),
        encoding="utf-8",
    )


def _write_gate(path: Path, gate: str, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "gate": gate,
        "status": status,
        "details": "",
        "generated_at": "2026-03-03T00:00:00+00:00",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_lead_project(root: Path, *, feature_status: str = "done") -> None:
    project_root = root / "PROJETOS" / "LEAD-ETL-FUSION" / "features"
    for index, feature_dir in enumerate(LEAD_FEATURE_DIRS, start=1):
        _write_feature(
            project_root / feature_dir / f"FEATURE-{index}-{feature_dir.split('-', 2)[2]}.md",
            status=feature_status,
        )


def test_build_summary_lead_project_promotes_when_gates_and_features_are_green(tmp_path: Path) -> None:
    _seed_lead_project(tmp_path, feature_status="done")
    _write_gate(tmp_path / "artifacts/phase-f4/evidence/eval-integrations.json", "eval-integrations", "PASS")
    _write_gate(tmp_path / "artifacts/phase-f4/evidence/ci-quality.json", "ci-quality", "PASS")

    output = tmp_path / "artifacts/phase-f4/validation-summary.md"
    rc = build_summary(
        tmp_path,
        env_file=tmp_path / "noop.env",
        output=output,
        project="LEAD-ETL-FUSION",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Decision atual: `promote`." in text
    assert "## Status das Features" in text
    assert "`make eval-integrations`: `PASS`." in text
    assert "`make ci-quality`: `PASS`." in text


def test_build_summary_lead_project_holds_when_gate_evidence_missing(tmp_path: Path) -> None:
    _seed_lead_project(tmp_path, feature_status="done")
    _write_gate(tmp_path / "artifacts/phase-f4/evidence/eval-integrations.json", "eval-integrations", "PASS")

    output = tmp_path / "artifacts/phase-f4/validation-summary.md"
    rc = build_summary(
        tmp_path,
        env_file=tmp_path / "noop.env",
        output=output,
        project="LEAD-ETL-FUSION",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    assert "Decision atual: `hold`." in text
    assert "Evidencia ausente para `ci-quality`." in text
