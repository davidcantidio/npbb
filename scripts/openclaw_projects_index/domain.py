"""
Lógica pura do índice OpenClaw: classificação de paths, parsing YAML, utilitários.
Usada por sync.py (SQLite e Postgres) sem dependência de driver SQL.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

PROJETOS = "PROJETOS"
SQLITE_SCHEMA_VERSION = "4"
POSTGRES_SCHEMA_BUNDLE = "pg-1"
EXPECTED_SQLITE_USER_VERSION = 4

YAML_FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.DOTALL)
FEATURE_FOLDER_RE = re.compile(r"^FEATURE-(\d+)(?:-|$)", re.IGNORECASE)
USER_STORY_FOLDER_RE = re.compile(r"^US-(\d+)-(\d+)(?:-|$)", re.IGNORECASE)
TASK_FILE_RE = re.compile(r"^TASK-(\d+)\.md$", re.IGNORECASE)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def require_yaml() -> None:
    if yaml is None:
        raise RuntimeError(
            "PyYAML não está instalado. Instale o módulo `yaml` para sincronizar o índice."
        )


def parse_front_matter(raw: str, source_name: str = "<string>") -> tuple[dict[str, Any], str]:
    match = YAML_FRONT_MATTER_RE.match(raw)
    if not match:
        return {}, raw

    require_yaml()
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError(f"Front matter de {source_name} deve ser um mapping YAML.")
    body = raw[match.end() :]
    if body.startswith("\r\n"):
        body = body[2:]
    elif body.startswith("\n"):
        body = body[1:]
    return meta, body


def first_markdown_title(body: str) -> Optional[str]:
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("#\t"):
            return line[2:].strip()
    return None


def posix_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def json_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=json_default)


def json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def scalar_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json_text(value)
    return str(value)


def int_value(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def bool_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return 1 if value else 0
    if isinstance(value, str):
        raw = value.strip().lower()
        if raw in {"1", "true", "yes", "y", "sim"}:
            return 1
        if raw in {"0", "false", "no", "n", ""}:
            return 0
    return default


def governance_kind_from_filename(name: str) -> str:
    upper = name.upper()
    if name == "boot-prompt.md":
        return "BOOT"
    if upper.startswith("GOV-"):
        return "GOV"
    if upper.startswith("SESSION-"):
        return "SESSION"
    if upper.startswith("TEMPLATE-"):
        return "TEMPLATE"
    if upper.startswith("SPEC-"):
        return "SPEC"
    if upper.startswith("PROMPT-"):
        return "PROMPT"
    return "COMUM_OTHER"


def feature_number_from_key(feature_key: str) -> Optional[int]:
    match = FEATURE_FOLDER_RE.match(feature_key)
    return int(match.group(1)) if match else None


def feature_root_relative(project_slug: str, feature_key: str) -> str:
    return "/".join([PROJETOS, project_slug, "features", feature_key])


def user_story_readme_relative(project_slug: str, feature_key: str, user_story_key: str) -> str:
    return "/".join(
        [
            feature_root_relative(project_slug, feature_key),
            "user-stories",
            user_story_key,
            "README.md",
        ]
    )


@dataclass
class Classified:
    kind: str
    project_slug: Optional[str] = None
    feature_key: Optional[str] = None
    user_story_key: Optional[str] = None
    task_number: Optional[int] = None
    report_key: Optional[str] = None
    doc_type: Optional[str] = None
    intake_slug: Optional[str] = None


def classify_md(rel_posix: str) -> Classified:
    parts = rel_posix.split("/")
    if len(parts) < 2 or parts[0] != PROJETOS:
        return Classified(kind="other")

    if parts[1] == "COMUM":
        return Classified(kind="governance")

    project_slug = parts[1]
    if len(parts) == 3 and parts[2].endswith(".md"):
        filename = parts[2]
        if filename.startswith("INTAKE-") and filename.endswith(".md"):
            slug = filename[len("INTAKE") : -len(".md")].lstrip("-") or None
            return Classified(
                kind="project_intake",
                project_slug=project_slug,
                doc_type="intake",
                intake_slug=slug,
            )
        if filename.startswith("PRD-") and filename.endswith(".md"):
            return Classified(kind="project_prd", project_slug=project_slug, doc_type="prd")
        if filename == "AUDIT-LOG.md":
            return Classified(kind="project_audit_log", project_slug=project_slug, doc_type="audit_log")
        if filename.startswith("SESSION-") and filename.endswith(".md"):
            return Classified(kind="project_session", project_slug=project_slug)
        if filename.startswith("DECISION-") and filename.endswith(".md"):
            return Classified(kind="project_other", project_slug=project_slug)
        return Classified(kind="project_root_md", project_slug=project_slug)

    if len(parts) == 4 and parts[2] == "encerramento" and parts[3] == "RELATORIO-ENCERRAMENTO.md":
        return Classified(kind="project_closing_report", project_slug=project_slug, doc_type="closing_report")

    if len(parts) >= 5 and parts[2] == "features" and FEATURE_FOLDER_RE.match(parts[3] or ""):
        feature_key = parts[3]
        rest = parts[4:]

        if len(rest) == 1 and rest[0].startswith("FEATURE-") and rest[0].endswith(".md"):
            return Classified(
                kind="feature_manifest",
                project_slug=project_slug,
                feature_key=feature_key,
            )

        if len(rest) >= 3 and rest[0] == "user-stories" and USER_STORY_FOLDER_RE.match(rest[1] or ""):
            user_story_key = rest[1]
            leaf = rest[-1]
            if len(rest) == 3 and leaf == "README.md":
                return Classified(
                    kind="user_story_readme",
                    project_slug=project_slug,
                    feature_key=feature_key,
                    user_story_key=user_story_key,
                )
            task_match = TASK_FILE_RE.match(leaf)
            if len(rest) == 3 and task_match:
                return Classified(
                    kind="task_file",
                    project_slug=project_slug,
                    feature_key=feature_key,
                    user_story_key=user_story_key,
                    task_number=int(task_match.group(1)),
                )
            return Classified(
                kind="user_story_other_md",
                project_slug=project_slug,
                feature_key=feature_key,
                user_story_key=user_story_key,
            )

        if (
            len(rest) == 2
            and rest[0] == "auditorias"
            and rest[1].startswith("RELATORIO-AUDITORIA-")
            and rest[1].endswith(".md")
        ):
            return Classified(
                kind="feature_audit_file",
                project_slug=project_slug,
                feature_key=feature_key,
                report_key=rest[1][: -len(".md")],
            )

        return Classified(
            kind="feature_other_md",
            project_slug=project_slug,
            feature_key=feature_key,
        )

    return Classified(kind="project_nested_other", project_slug=project_slug)


def default_db_path(repo_root: Path) -> Path:
    env = os.environ.get("OPENCLAW_PROJECTS_DB", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (repo_root / ".openclaw" / "openclaw-projects.sqlite").resolve()


def resolve_repo_root(cli: Optional[str]) -> Path:
    if cli:
        return Path(cli).expanduser().resolve()
    env = os.environ.get("OPENCLAW_REPO_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve().parent
    cand = here.parent.parent
    if (cand / PROJETOS).is_dir():
        return cand
    cwd = Path.cwd().resolve()
    if (cwd / PROJETOS).is_dir():
        return cwd
    raise SystemExit(
        "Não foi possível localizar PROJETOS/. Passe --repo-root ou defina OPENCLAW_REPO_ROOT."
    )


def is_canonical_project_dir(project_dir: Path) -> bool:
    slug = project_dir.name
    required = (
        project_dir / f"INTAKE-{slug}.md",
        project_dir / f"PRD-{slug}.md",
        project_dir / "AUDIT-LOG.md",
    )
    return all(path.is_file() for path in required)


def discover_project_slugs(projetos: Path) -> list[str]:
    out: list[str] = []
    if not projetos.is_dir():
        return out
    for path in sorted(projetos.iterdir()):
        if not path.is_dir():
            continue
        if path.name == "COMUM" or path.name.startswith(".") or path.name.startswith("_WORK-"):
            continue
        if is_canonical_project_dir(path):
            out.append(path.name)
    return out


def file_content_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def resolve_postgres_url() -> str:
    url = os.environ.get("OPENCLAW_PROJECTS_DATABASE_URL", "").strip()
    if not url:
        raise SystemExit(
            "Postgres: defina OPENCLAW_PROJECTS_DATABASE_URL (ex.: postgresql://user@localhost:5432/openclaw_projects)."
        )
    sslmode = os.environ.get("OPENCLAW_PGSSLMODE", "").strip()
    if sslmode and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode={sslmode}"
    return url


def git_head_sha(repo_root: Path) -> Optional[str]:
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None
