from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ProjectProfile:
    project_dir: str
    feature_dirs: tuple[tuple[str, str], ...]
    include_ops_evidence: bool


PROJECT_PROFILES: dict[str, ProjectProfile] = {
    "LEAD-ETL-FUSION": ProjectProfile(
        project_dir="LEAD-ETL-FUSION",
        feature_dirs=(
            ("FEATURE-1", "FEATURE-1-NUCLEO-ETL"),
            ("FEATURE-2", "FEATURE-2-INTEGRACAO-BACKEND"),
            ("FEATURE-3", "FEATURE-3-REFATORACAO-CLI"),
            ("FEATURE-4", "FEATURE-4-UI-IMPORTACAO-AVANCADA"),
        ),
        include_ops_evidence=False,
    ),
}


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def parse_frontmatter_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return "unknown"
    frontmatter = match.group(1)
    status_match = re.search(r'^status:\s*"?(.*?)"?$', frontmatter, flags=re.MULTILINE)
    if not status_match:
        return "unknown"
    return status_match.group(1).strip()


def collect_feature_statuses(
    project_root: Path,
    *,
    profile: ProjectProfile,
) -> tuple[list[dict[str, str]], list[str]]:
    records: list[dict[str, str]] = []
    blockers: list[str] = []
    feature_root = project_root / "PROJETOS" / profile.project_dir / "features"

    for feature_code, feature_dir_name in profile.feature_dirs:
        current_feature_dir = feature_root / feature_dir_name
        if not current_feature_dir.exists():
            blockers.append(f"Diretorio de feature ausente: {feature_dir_name}.")
            continue

        manifests = sorted(current_feature_dir.glob("FEATURE-*.md"))
        if not manifests:
            blockers.append(f"Nenhum manifesto de feature encontrado em {feature_dir_name}.")
            continue

        for manifest in manifests:
            records.append(
                {
                    "feature": feature_code,
                    "feature_id": manifest.stem,
                    "status": parse_frontmatter_status(manifest),
                    "path": str(manifest.relative_to(project_root)),
                }
            )

    for record in records:
        if record["status"] != "done":
            blockers.append(f"{record['feature_id']} permanece em status `{record['status']}`.")

    return records, blockers


def latest_dump(directory: Path, prefix: str) -> Path | None:
    if not directory.exists():
        return None
    dumps = sorted(directory.glob(f"{prefix}_*.dump"))
    if not dumps:
        return None
    return dumps[-1]


def describe_backup(env_values: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    blockers: list[str] = []
    prefix = env_values.get("BACKUP_FILE_PREFIX", "npbb")
    local_dir = Path(env_values.get("BACKUP_HOST_DIR", "/opt/npbb/backups/postgres")) / "daily"
    external_dir = Path(env_values.get("BACKUP_EXTERNAL_HOST_DIR", "/opt/npbb/backups/archive")) / "daily"
    local_dump = latest_dump(local_dir, prefix)
    external_dump = latest_dump(external_dir, prefix)

    if local_dump is None:
        blockers.append("Nao ha dump local diario disponivel.")
    if external_dump is None:
        blockers.append("Nao ha dump externo diario disponivel.")

    return (
        {
            "local_dump": str(local_dump) if local_dump else "ausente",
            "external_dump": str(external_dump) if external_dump else "ausente",
        },
        blockers,
    )


def build_summary(project_root: Path, env_file: Path, output: Path, *, project: str) -> int:
    profile = PROJECT_PROFILES[project]
    evidence_dir = project_root / "artifacts" / "phase-f4" / "evidence"
    env_values = parse_env_file(env_file)

    gate_eval = load_json(evidence_dir / "eval-integrations.json")
    gate_ci = load_json(evidence_dir / "ci-quality.json")
    deploy = load_json(evidence_dir / "deploy.json")
    health = load_json(evidence_dir / "health.json")
    smoke = load_json(evidence_dir / "smoke.json")
    backup_drill = load_json(evidence_dir / "backup-drill.json")

    feature_statuses, feature_blockers = collect_feature_statuses(project_root, profile=profile)
    backup_state, backup_blockers = describe_backup(env_values)

    blockers: list[str] = []

    def gate_status(name: str, payload: dict[str, object] | None) -> str:
        if payload is None:
            blockers.append(f"Evidencia ausente para `{name}`.")
            return "missing"
        status = str(payload.get("status", "missing"))
        if status != "PASS":
            blockers.append(f"Gate `{name}` nao passou (`{status}`).")
        return status

    eval_status = gate_status("eval-integrations", gate_eval)
    ci_status = gate_status("ci-quality", gate_ci)

    lines: list[str] = [
        "# Feature Validation Summary",
        "",
        "## Estado Atual",
        "",
    ]

    if profile.include_ops_evidence:
        deploy_status = gate_status("deploy", deploy)
        health_status = gate_status("health", health)
        smoke_status = gate_status("smoke", smoke)
        backup_drill_status = gate_status("backup-drill", backup_drill)
        blockers.extend(backup_blockers)

    blockers.extend(feature_blockers)
    decision = "promote" if not blockers else "hold"
    output.parent.mkdir(parents=True, exist_ok=True)

    lines.extend(
        [
            f"Decision atual: `{decision}`.",
            "",
            f"Gerado em: `{datetime.now(timezone.utc).isoformat()}`.",
            "",
            "## Gates",
            "",
            f"- `make eval-integrations`: `{eval_status}`.",
            f"- `make ci-quality`: `{ci_status}`.",
        ]
    )

    if profile.include_ops_evidence:
        lines.extend(
            [
                f"- Evidencia de deploy: `{deploy_status}`.",
                f"- Saude dos containers: `{health_status}`.",
                f"- Smoke HTTPS: `{smoke_status}`.",
                f"- Restore drill: `{backup_drill_status}`.",
                f"- Ultimo dump local: `{backup_state['local_dump']}`.",
                f"- Ultimo dump externo: `{backup_state['external_dump']}`.",
            ]
        )

    lines.extend(
        [
            "",
            "## Status das Features",
            "",
            "| Feature | Manifesto | Status | Documento |",
            "|---|---|---|---|",
        ]
    )

    for record in feature_statuses:
        lines.append(
            f"| `{record['feature']}` | `{record['feature_id']}` | `{record['status']}` | `{record['path']}` |"
        )

    lines.extend(["", "## Bloqueios", ""])
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- Nenhum bloqueio identificado.")

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the feature validation summary.")
    parser.add_argument("--project", default="LEAD-ETL-FUSION", choices=sorted(PROJECT_PROFILES))
    parser.add_argument("--env-file", default="backend/.env.example")
    parser.add_argument("--output", default="artifacts/phase-f4/validation-summary.md")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = project_root / env_file
    output = Path(args.output)
    if not output.is_absolute():
        output = project_root / output

    return build_summary(project_root, env_file, output, project=args.project)


if __name__ == "__main__":
    raise SystemExit(main())
