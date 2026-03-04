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
    phase_dirs: tuple[tuple[str, str], ...]
    include_ops_evidence: bool


PROJECT_PROFILES: dict[str, ProjectProfile] = {
    "MIGRACAO-VPS-HOSTINGER": ProjectProfile(
        project_dir="MIGRACAO-VPS-HOSTINGER",
        phase_dirs=(
            ("F1", "F1-PREPARACAO-INFRA"),
            ("F2", "F2-MIGRACAO-BANCO"),
            ("F3", "F3-DEPLOY-BACKEND-FRONTEND"),
            ("F4", "F4-CICD-E-LIMPEZA"),
        ),
        include_ops_evidence=True,
    ),
    "LEAD-ETL-FUSION": ProjectProfile(
        project_dir="LEAD-ETL-FUSION",
        phase_dirs=(
            ("F1", "F1-NUCLEO-ETL"),
            ("F2", "F2-INTEGRACAO-BACKEND"),
            ("F3", "F3-REFATORACAO-CLI"),
            ("F4", "F4-UI-IMPORTACAO-AVANCADA"),
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


def collect_epic_statuses(
    project_root: Path,
    *,
    profile: ProjectProfile,
) -> tuple[list[dict[str, str]], list[str]]:
    records: list[dict[str, str]] = []
    blockers: list[str] = []
    projetos_root = project_root / "PROJETOS"
    project_dir = projetos_root / profile.project_dir
    feito_dir = project_dir / "feito"

    for phase_id, phase_dir_name in profile.phase_dirs:
        active_phase_dir = project_dir / phase_dir_name
        archived_phase_dir = feito_dir / phase_dir_name

        active_exists = active_phase_dir.exists()
        archived_exists = archived_phase_dir.exists()

        if active_exists and archived_exists:
            blockers.append(f"Fase duplicada em ativo e feito: {phase_dir_name}.")

        if active_exists:
            phase_dir = active_phase_dir
            phase_location = "active"
        elif archived_exists:
            phase_dir = archived_phase_dir
            phase_location = "archived"
        else:
            blockers.append(f"Diretorio de fase ausente em ativo e feito: {phase_dir_name}.")
            continue

        epic_files = sorted(phase_dir.glob("EPIC-*.md"))
        if not epic_files:
            blockers.append(f"Nenhum epico encontrado em {phase_dir_name} ({phase_location}).")
            continue

        for epic_file in epic_files:
            records.append(
                {
                    "phase": phase_id,
                    "epic_id": epic_file.stem,
                    "status": parse_frontmatter_status(epic_file),
                    "path": str(epic_file.relative_to(project_root)),
                    "phase_location": phase_location,
                }
            )

    for record in records:
        if record["status"] != "done":
            blockers.append(f"{record['epic_id']} permanece em status `{record['status']}`.")
        if record["phase_location"] == "archived" and record["status"] != "done":
            blockers.append(f"{record['epic_id']} esta em `feito/` sem status `done`.")

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

    epic_statuses, epic_blockers = collect_epic_statuses(project_root, profile=profile)
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
        "# Phase F4 Validation Summary",
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

    blockers.extend(epic_blockers)
    decision = "promote" if not blockers else "hold"
    output.parent.mkdir(parents=True, exist_ok=True)

    lines.extend(
        [
            f"Decision atual: `{decision}`.",
            "",
            f"Gerado em: `{datetime.now(timezone.utc).isoformat()}`.",
            "",
            "## Gate da Fase",
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
            "## Status dos Epicos",
            "",
            "| Fase | Epic ID | Status | Documento |",
            "|---|---|---|---|",
        ]
    )

    for record in epic_statuses:
        lines.append(
            f"| `{record['phase']}` | `{record['epic_id']}` | `{record['status']}` | `{record['path']}` |"
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
    parser = argparse.ArgumentParser(description="Render the phase F4 validation summary.")
    parser.add_argument("--project", default="MIGRACAO-VPS-HOSTINGER", choices=sorted(PROJECT_PROFILES))
    parser.add_argument("--env-file", default="Infra/production/.env.example")
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
