from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_DOC_SURFACES = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.MD",
    REPO_ROOT / "PROJETOS" / "NPBB",
)
REMOVED_OPENCLAW_BIN_WRAPPERS = (
    REPO_ROOT / "bin" / "apply-openclaw-projects-pg-schema.sh",
    REPO_ROOT / "bin" / "ensure-openclaw-projects-index-runtime.sh",
    REPO_ROOT / "bin" / "mirror-openclaw-projects-sqlite-to-pg.sh",
    REPO_ROOT / "bin" / "sync-openclaw-projects-db.sh",
)
FORBIDDEN_ACTIVE_REFERENCES = (
    ".openclaw/openclaw-projects.sqlite",
    "OPENCLAW_PROJECTS_DATABASE_URL",
    "openclaw_projects_index",
    "apply-openclaw-projects-pg-schema.sh",
    "scripts/fabrica_domain",
    "ensure-openclaw-projects-index-runtime.sh",
    "mirror-openclaw-projects-sqlite-to-pg.sh",
    "sync-openclaw-projects-db.sh",
    "tests/test_openclaw_projects_index.py",
)


def test_removed_local_runtime_surfaces_are_absent() -> None:
    assert not (REPO_ROOT / "scripts" / "openclaw_projects_index").exists()
    assert not (REPO_ROOT / "scripts" / "fabrica_domain").exists()
    for path in REMOVED_OPENCLAW_BIN_WRAPPERS:
        assert not path.exists()
    assert not (REPO_ROOT / "tests" / "test_openclaw_projects_index.py").exists()
    assert not (REPO_ROOT / "tests" / "test_index_derivation.py").exists()
    assert not (REPO_ROOT / "tests" / "test_fabrica_domain_gov_ids.py").exists()


def test_active_docs_do_not_reference_local_legacy_runtime() -> None:
    offenders: dict[str, list[str]] = {}
    for root in ACTIVE_DOC_SURFACES:
        if root.is_file():
            candidates = [root]
        else:
            candidates = [path for path in root.rglob("*.md") if path.is_file()]

        for path in candidates:
            text = path.read_text(encoding="utf-8", errors="ignore")
            matches = [token for token in FORBIDDEN_ACTIVE_REFERENCES if token in text]
            if matches:
                offenders[path.relative_to(REPO_ROOT).as_posix()] = matches

    assert offenders == {}


def test_local_openclaw_sqlite_is_gitignored() -> None:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8", errors="ignore")

    assert ".openclaw/*.sqlite" in text
