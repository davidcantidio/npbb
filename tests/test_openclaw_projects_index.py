import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "openclaw_projects_index" / "sync.py"
SYNC_WRAPPER_PATH = REPO_ROOT / "bin" / "sync-openclaw-projects-db.sh"
SCHEMA_PATH = REPO_ROOT / "scripts" / "openclaw_projects_index" / "schema.sql"
DOMAIN_PATH = REPO_ROOT / "scripts" / "openclaw_projects_index" / "domain.py"
MIGRATE_EMBEDDINGS_SCRIPT = (
    REPO_ROOT / "scripts" / "openclaw_projects_index" / "migrate_sqlite_embeddings_to_postgres.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("openclaw_projects_index_sync", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def build_repo_fixture(root: Path) -> None:
    projetos = root / "PROJETOS"
    project = projetos / "DEMO"
    feature_root = project / "features" / "FEATURE-1-FOUNDATION"
    user_story_root = feature_root / "user-stories" / "US-1-01-BOOTSTRAP"

    write_file(
        projetos / "COMUM" / "GOV-FRAMEWORK-MASTER.md",
        """
        ---
        doc_id: "GOV-FRAMEWORK-MASTER.md"
        version: "1.0"
        status: "active"
        owner: "PM"
        last_updated: "2026-03-25"
        ---

        # GOV-FRAMEWORK-MASTER
        """,
    )

    write_file(
        project / "INTAKE-DEMO.md",
        """
        ---
        doc_id: "INTAKE-DEMO"
        status: "draft"
        intake_kind: "new-capability"
        source_mode: "original"
        last_updated: "2026-03-25"
        ---

        # Intake DEMO
        """,
    )
    write_file(
        project / "PRD-DEMO.md",
        """
        ---
        doc_id: "PRD-DEMO"
        status: "active"
        intake_kind: "new-capability"
        source_mode: "original"
        last_updated: "2026-03-25"
        ---

        # PRD DEMO
        """,
    )
    write_file(
        project / "AUDIT-LOG.md",
        """
        ---
        doc_id: "AUDIT-LOG"
        status: "active"
        last_updated: "2026-03-25"
        ---

        # Audit Log DEMO
        """,
    )

    write_file(
        feature_root / "FEATURE-1-FOUNDATION.md",
        """
        ---
        doc_id: "FEATURE-1-FOUNDATION"
        status: "active"
        audit_gate: "pending"
        last_updated: "2026-03-25"
        ---

        # FEATURE-1-FOUNDATION
        """,
    )
    write_file(
        user_story_root / "README.md",
        """
        ---
        doc_id: "US-1-01-BOOTSTRAP"
        status: "ready_for_review"
        task_instruction_mode: "required"
        decision_refs:
          - "DEC-1"
        last_updated: "2026-03-25"
        ---

        # US-1-01-BOOTSTRAP
        """,
    )
    write_file(
        user_story_root / "TASK-1.md",
        """
        ---
        doc_id: "TASK-1"
        task_id: "T1"
        status: "done"
        tdd_aplicavel: true
        last_updated: "2026-03-25"
        ---

        # T1 - Bootstrap base
        """,
    )
    write_file(
        user_story_root / "TASK-2.md",
        """
        ---
        doc_id: "TASK-2"
        status: "todo"
        tdd_aplicavel: false
        last_updated: "2026-03-25"
        ---

        # T2 - Finalizar handoff
        """,
    )
    write_file(
        user_story_root / "SCOPE-LEARN.md",
        """
        ---
        doc_id: "SCOPE-LEARN"
        status: "aguardando_senior"
        last_updated: "2026-03-25"
        ---

        # SCOPE-LEARN
        """,
    )
    write_file(
        feature_root / "auditorias" / "RELATORIO-AUDITORIA-F1-R01.md",
        """
        ---
        doc_id: "RELATORIO-AUDITORIA-F1-R01"
        status: "planned"
        verdict: "hold"
        scope_type: "feature"
        scope_ref: "FEATURE-1-FOUNDATION"
        feature_id: "FEATURE-1-FOUNDATION"
        base_commit: "abc123"
        compares_to: "none"
        round: 1
        supersedes: "none"
        followup_destination: "same-feature"
        decision_refs: []
        last_updated: "2026-03-25"
        ---

        # RELATORIO-AUDITORIA-F1-R01
        """,
    )
    write_file(
        project / "encerramento" / "RELATORIO-ENCERRAMENTO.md",
        """
        ---
        doc_id: "RELATORIO-ENCERRAMENTO"
        status: "draft"
        project: "DEMO"
        last_updated: "2026-03-25"
        ---

        # RELATORIO-ENCERRAMENTO
        """,
    )

    write_file(
        project / "F2-LEGACY" / "issues" / "ISSUE-F2-01-001-LEGADO" / "README.md",
        """
        ---
        doc_id: "ISSUE-F2-01-001-LEGADO"
        status: "done"
        task_instruction_mode: "optional"
        last_updated: "2026-03-25"
        ---

        # ISSUE-F2-01-001-LEGADO
        """,
    )
    write_file(
        project / "F2-LEGACY" / "issues" / "ISSUE-F2-01-001-LEGADO" / "TASK-1.md",
        """
        ---
        doc_id: "TASK-1"
        task_id: "T1"
        status: "done"
        tdd_aplicavel: false
        last_updated: "2026-03-25"
        ---

        # T1 - Legado
        """,
    )
    write_file(
        project / "F2-LEGACY" / "auditorias" / "RELATORIO-AUDITORIA-F2-R01.md",
        """
        ---
        doc_id: "RELATORIO-AUDITORIA-F2-R01"
        status: "done"
        verdict: "go"
        last_updated: "2026-03-25"
        ---

        # RELATORIO-AUDITORIA-F2-R01
        """,
    )

    write_file(
        projetos / "_WORK-IGNORAR" / "INTAKE-_WORK-IGNORAR.md",
        """
        ---
        doc_id: "INTAKE-_WORK-IGNORAR"
        status: "draft"
        ---

        # Workdir
        """,
    )
    write_file(
        projetos / "NAO-CANONICO" / "README.md",
        """
        # Nao canonico
        """,
    )


def build_runtime_repo_fixture(root: Path) -> None:
    build_repo_fixture(root)

    files_to_copy = (
        ("bin", SYNC_WRAPPER_PATH),
        ("scripts/openclaw_projects_index", SCRIPT_PATH),
        ("scripts/openclaw_projects_index", SCHEMA_PATH),
        ("scripts/openclaw_projects_index", DOMAIN_PATH),
        ("scripts/openclaw_projects_index", REPO_ROOT / "scripts/openclaw_projects_index/postgres_schema_util.py"),
        ("scripts/openclaw_projects_index", REPO_ROOT / "scripts/openclaw_projects_index/schema_postgres.sql"),
    )

    for destination_dir, source_path in files_to_copy:
        destination = root / destination_dir / source_path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)


class OpenClawProjectsIndexTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_parse_front_matter_preserves_lists_booleans_and_integers(self):
        raw = textwrap.dedent(
            """
            ---
            decision_refs:
              - DEC-1
              - DEC-2
            tdd_aplicavel: true
            round: 7
            ---

            # Titulo
            """
        ).lstrip()

        meta, body = self.module.parse_front_matter(raw, source_name="fixture.md")

        self.assertEqual(meta["decision_refs"], ["DEC-1", "DEC-2"])
        self.assertIs(meta["tdd_aplicavel"], True)
        self.assertEqual(meta["round"], 7)
        self.assertEqual(body, "# Titulo\n")

    def test_json_text_serializes_dates_loaded_from_yaml(self):
        raw = textwrap.dedent(
            """
            ---
            last_updated: 2026-03-25
            nested:
              reviewed_at: 2026-03-24
            ---

            # Titulo
            """
        ).lstrip()

        meta, _ = self.module.parse_front_matter(raw, source_name="fixture.md")
        serialized = self.module.json_text(meta)

        self.assertEqual(
            json.loads(serialized),
            {
                "last_updated": "2026-03-25",
                "nested": {"reviewed_at": "2026-03-24"},
            },
        )

    def test_adapt_front_matter_postgres_normalizes_yaml_dates(self):
        raw = textwrap.dedent(
            """
            ---
            last_updated: 2026-03-25
            nested:
              reviewed_at: 2026-03-24
            ---

            # Titulo
            """
        ).lstrip()

        meta, _ = self.module.parse_front_matter(raw, source_name="fixture.md")
        adapted = self.module._adapt_front_matter("postgres", meta)

        self.assertEqual(
            adapted.obj,
            {
                "last_updated": "2026-03-25",
                "nested": {"reviewed_at": "2026-03-24"},
            },
        )

    def test_classify_md_recognizes_feature_first_layout_and_cuts_legacy_to_documents(self):
        feature_manifest = self.module.classify_md(
            "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/FEATURE-1-FOUNDATION.md"
        )
        user_story_readme = self.module.classify_md(
            "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md"
        )
        task_file = self.module.classify_md(
            "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/TASK-2.md"
        )
        user_story_other = self.module.classify_md(
            "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/SCOPE-LEARN.md"
        )
        feature_audit = self.module.classify_md(
            "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/auditorias/RELATORIO-AUDITORIA-F1-R01.md"
        )
        closing_report = self.module.classify_md(
            "PROJETOS/DEMO/encerramento/RELATORIO-ENCERRAMENTO.md"
        )
        legacy_issue = self.module.classify_md(
            "PROJETOS/DEMO/F2-LEGACY/issues/ISSUE-F2-01-001-LEGADO/README.md"
        )

        self.assertEqual(feature_manifest.kind, "feature_manifest")
        self.assertEqual(feature_manifest.feature_key, "FEATURE-1-FOUNDATION")

        self.assertEqual(user_story_readme.kind, "user_story_readme")
        self.assertEqual(user_story_readme.feature_key, "FEATURE-1-FOUNDATION")
        self.assertEqual(user_story_readme.user_story_key, "US-1-01-BOOTSTRAP")

        self.assertEqual(task_file.kind, "task_file")
        self.assertEqual(task_file.task_number, 2)

        self.assertEqual(user_story_other.kind, "user_story_other_md")
        self.assertEqual(feature_audit.kind, "feature_audit_file")
        self.assertEqual(feature_audit.report_key, "RELATORIO-AUDITORIA-F1-R01")
        self.assertEqual(closing_report.kind, "project_closing_report")

        self.assertEqual(legacy_issue.kind, "project_nested_other")
        self.assertEqual(legacy_issue.project_slug, "DEMO")

    def test_discover_project_slugs_ignores_workdirs_and_noncanonical_dirs(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            build_repo_fixture(root)

            projects = self.module.discover_project_slugs(root / "PROJETOS")

            self.assertEqual(projects, ["DEMO"])

    def test_default_db_path_uses_repo_local_dot_openclaw(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            db_path = self.module.default_db_path(root)

            self.assertEqual(
                db_path,
                (root / ".openclaw" / "openclaw-projects.sqlite").resolve(),
            )

    def test_run_sync_populates_v4_tables_and_keeps_legacy_only_in_documents(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            build_repo_fixture(root)
            db_path = root / "openclaw.sqlite"

            self.module.run_sync(root, db_path, dry_run=False)

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute("PRAGMA user_version")
            self.assertEqual(cur.fetchone()[0], 4)

            cur.execute("SELECT slug FROM projects ORDER BY slug")
            self.assertEqual([row["slug"] for row in cur.fetchall()], ["DEMO"])

            cur.execute(
                "SELECT feature_key, status, audit_gate, path_relative FROM features ORDER BY feature_key"
            )
            features = cur.fetchall()
            self.assertEqual(len(features), 1)
            self.assertEqual(features[0]["feature_key"], "FEATURE-1-FOUNDATION")
            self.assertEqual(features[0]["status"], "active")
            self.assertEqual(features[0]["audit_gate"], "pending")
            self.assertEqual(
                features[0]["path_relative"],
                "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION",
            )

            cur.execute(
                """
                SELECT user_story_key, status, task_instruction_mode, decision_refs_json, path_relative
                FROM user_stories
                ORDER BY user_story_key
                """
            )
            user_stories = cur.fetchall()
            self.assertEqual(len(user_stories), 1)
            self.assertEqual(user_stories[0]["user_story_key"], "US-1-01-BOOTSTRAP")
            self.assertEqual(user_stories[0]["status"], "ready_for_review")
            self.assertEqual(user_stories[0]["task_instruction_mode"], "required")
            self.assertEqual(json.loads(user_stories[0]["decision_refs_json"]), ["DEC-1"])
            self.assertEqual(
                user_stories[0]["path_relative"],
                "PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md",
            )

            cur.execute(
                """
                SELECT task_number, task_id, status, tdd_aplicavel, path_relative
                FROM tasks
                ORDER BY task_number
                """
            )
            tasks = cur.fetchall()
            self.assertEqual(
                [
                    (row["task_number"], row["task_id"], row["status"], row["tdd_aplicavel"])
                    for row in tasks
                ],
                [(1, "T1", "done", 1), (2, "T2", "todo", 0)],
            )

            cur.execute(
                """
                SELECT report_key, status, verdict, feature_code, round_number, followup_destination
                FROM feature_audits
                ORDER BY report_key
                """
            )
            audits = cur.fetchall()
            self.assertEqual(len(audits), 1)
            self.assertEqual(audits[0]["report_key"], "RELATORIO-AUDITORIA-F1-R01")
            self.assertEqual(audits[0]["status"], "planned")
            self.assertEqual(audits[0]["verdict"], "hold")
            self.assertEqual(audits[0]["feature_code"], "FEATURE-1-FOUNDATION")
            self.assertEqual(audits[0]["round_number"], 1)
            self.assertEqual(audits[0]["followup_destination"], "same-feature")

            cur.execute("SELECT doc_type FROM project_documents ORDER BY doc_type")
            self.assertEqual(
                [row["doc_type"] for row in cur.fetchall()],
                ["audit_log", "closing_report", "intake", "prd"],
            )

            cur.execute(
                """
                SELECT kind, user_story_id
                FROM documents
                WHERE path_relative = 'PROJETOS/DEMO/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/SCOPE-LEARN.md'
                """
            )
            scope_learn = cur.fetchone()
            self.assertEqual(scope_learn["kind"], "user_story_other")
            self.assertIsNotNone(scope_learn["user_story_id"])

            cur.execute(
                """
                SELECT kind, feature_id, user_story_id, task_id, feature_audit_id
                FROM documents
                WHERE path_relative = 'PROJETOS/DEMO/F2-LEGACY/issues/ISSUE-F2-01-001-LEGADO/README.md'
                """
            )
            legacy_doc = cur.fetchone()
            self.assertEqual(legacy_doc["kind"], "project_nested_other")
            self.assertIsNone(legacy_doc["feature_id"])
            self.assertIsNone(legacy_doc["user_story_id"])
            self.assertIsNone(legacy_doc["task_id"])
            self.assertIsNone(legacy_doc["feature_audit_id"])

            cur.execute("SELECT COUNT(*) FROM features")
            self.assertEqual(cur.fetchone()[0], 1)
            cur.execute("SELECT COUNT(*) FROM user_stories")
            self.assertEqual(cur.fetchone()[0], 1)
            cur.execute("SELECT COUNT(*) FROM tasks")
            self.assertEqual(cur.fetchone()[0], 2)
            cur.execute("SELECT COUNT(*) FROM feature_audits")
            self.assertEqual(cur.fetchone()[0], 1)

            cur.execute("SELECT value FROM sync_meta WHERE key = 'last_sync_at'")
            self.assertTrue(cur.fetchone()["value"])
            cur.execute("SELECT value FROM sync_meta WHERE key = 'repo_root'")
            self.assertEqual(cur.fetchone()["value"], str(root.resolve()))
            cur.execute("SELECT value FROM sync_meta WHERE key = 'schema_bundle_version'")
            self.assertEqual(cur.fetchone()["value"], "4")

            conn.close()

    def test_run_sync_recreates_schema_v4_from_legacy_database(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            build_repo_fixture(root)
            db_path = root / "openclaw.sqlite"

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.executescript(
                """
                CREATE TABLE phases (id INTEGER PRIMARY KEY);
                CREATE TABLE epics (id INTEGER PRIMARY KEY);
                CREATE TABLE issues (id INTEGER PRIMARY KEY);
                CREATE TABLE sprints (id INTEGER PRIMARY KEY);
                CREATE TABLE audit_reports (id INTEGER PRIMARY KEY);
                PRAGMA user_version = 3;
                """
            )
            conn.commit()
            conn.close()

            self.module.run_sync(root, db_path, dry_run=False)

            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA user_version")
            self.assertEqual(cur.fetchone()[0], 4)
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cur.fetchall()}
            self.assertIn("features", tables)
            self.assertIn("user_stories", tables)
            self.assertIn("tasks", tables)
            self.assertIn("feature_audits", tables)
            self.assertNotIn("phases", tables)
            self.assertNotIn("epics", tables)
            self.assertNotIn("issues", tables)
            self.assertNotIn("sprints", tables)
            self.assertNotIn("audit_reports", tables)
            conn.close()

    def test_sync_wrapper_creates_default_db_for_feature_first_repo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo_root = root / "repo"
            build_runtime_repo_fixture(repo_root)

            env = os.environ.copy()
            env["OPENCLAW_REPO_ROOT"] = str(repo_root)

            subprocess.run(
                ["./bin/sync-openclaw-projects-db.sh"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )

            db_path = repo_root / ".openclaw" / "openclaw-projects.sqlite"
            self.assertTrue(db_path.is_file())

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT value FROM sync_meta WHERE key = 'schema_bundle_version'")
            self.assertEqual(cur.fetchone()["value"], "4")
            cur.execute("SELECT COUNT(*) AS total FROM features")
            self.assertEqual(cur.fetchone()["total"], 1)
            cur.execute("SELECT COUNT(*) AS total FROM user_stories")
            self.assertEqual(cur.fetchone()["total"], 1)
            cur.execute("SELECT COUNT(*) AS total FROM tasks")
            self.assertEqual(cur.fetchone()["total"], 2)
            conn.close()

    def test_migrate_sqlite_embeddings_script_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            build_repo_fixture(root)
            db_path = root / "emb.sqlite"
            self.module.run_sync(root, db_path, dry_run=False)
            proc = subprocess.run(
                [sys.executable, str(MIGRATE_EMBEDDINGS_SCRIPT), "--sqlite-db", str(db_path), "--dry-run"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
            self.assertIn("dry-run", proc.stdout)

    @unittest.skipUnless(
        os.environ.get("OPENCLAW_PROJECTS_DATABASE_URL", "").strip(),
        "OPENCLAW_PROJECTS_DATABASE_URL not set",
    )
    def test_postgres_sync_row_counts_match_sqlite(self):
        """Paridade mínima SQLite vs Postgres (requer Postgres com extensão vector)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            build_repo_fixture(root)
            db_sqlite = root / "parity.sqlite"
            self.module.run_sync(root, db_sqlite, dry_run=False)
            self.module.run_sync(root, "postgres", None, dry_run=False)
            conn_sl = sqlite3.connect(str(db_sqlite))
            cur_sl = conn_sl.cursor()
            cur_sl.execute("SELECT COUNT(*) FROM documents")
            n_doc_sl = cur_sl.fetchone()[0]
            cur_sl.execute("SELECT COUNT(*) FROM projects")
            n_proj_sl = cur_sl.fetchone()[0]
            conn_sl.close()

            import psycopg

            with psycopg.connect(os.environ["OPENCLAW_PROJECTS_DATABASE_URL"].strip()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM documents")
                    n_doc_pg = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM projects")
                    n_proj_pg = cur.fetchone()[0]
            self.assertEqual(n_doc_pg, n_doc_sl)
            self.assertEqual(n_proj_pg, n_proj_sl)


if __name__ == "__main__":
    unittest.main()
