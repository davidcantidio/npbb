import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "criar_projeto.py"
SYNC_SCRIPT_PATH = REPO_ROOT / "scripts" / "openclaw_projects_index" / "sync.py"


def load_module():
    spec = importlib.util.spec_from_file_location("criar_projeto", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_sync_module():
    spec = importlib.util.spec_from_file_location("openclaw_projects_index_sync", SYNC_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CriarProjetoTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.sync_module = load_sync_module()

    def test_scaffold_cria_arvore_feature_first(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            previous_cwd = Path.cwd()
            os.chdir(tmp_path)
            try:
                self.module.criar_projeto("TESTE")
            finally:
                os.chdir(previous_cwd)

            project_root = tmp_path / "PROJETOS" / "TESTE"

            feature_root = (
                project_root / "features" / "FEATURE-1-FOUNDATION"
            )
            feature_manifest = feature_root / "FEATURE-1.md"
            user_story_readme = (
                feature_root
                / "user-stories"
                / "US-1-01-BOOTSTRAP"
                / "README.md"
            )
            task_file = user_story_readme.parent / "TASK-1.md"
            audit_report = feature_root / "auditorias" / "RELATORIO-AUDITORIA-F1-R01.md"
            closing_report = project_root / "encerramento" / "RELATORIO-ENCERRAMENTO.md"

            self.assertTrue(feature_manifest.exists())
            self.assertTrue(user_story_readme.exists())
            self.assertTrue(task_file.exists())
            self.assertTrue(audit_report.exists())
            self.assertTrue(closing_report.exists())

            self.assertFalse((project_root / "F1-FUNDACAO").exists())
            self.assertFalse((project_root / "issues").exists())
            self.assertFalse((project_root / "sprints").exists())

            feature_body = feature_manifest.read_text(encoding="utf-8")
            prd = (project_root / "PRD-TESTE.md").read_text(encoding="utf-8")

            self.assertIn("# FEATURE-1 - Foundation", feature_body)
            self.assertIn("| US-1-01 | Bootstrap do projeto | 3 | nenhuma | todo |", feature_body)
            self.assertIn("STATUS: PENDENTE - aguardando conclusao do Intake", prd)
            self.assertNotIn("## 12. Features do Projeto", prd)
            self.assertNotIn("### User Stories planejadas", prd)
            self.assertIn("Pos-PRD (nao faz parte deste arquivo)", prd)
            self.assertIn("SESSION-DECOMPOR-PRD-EM-FEATURES.md", prd)

    def test_wrappers_canonicos_nascem_genericos(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            previous_cwd = Path.cwd()
            os.chdir(tmp_path)
            try:
                self.module.criar_projeto("TESTE")
            finally:
                os.chdir(previous_cwd)

            project_root = tmp_path / "PROJETOS" / "TESTE"
            implement_wrapper = (project_root / "SESSION-IMPLEMENTAR-US.md").read_text(
                encoding="utf-8"
            )
            review_wrapper = (project_root / "SESSION-REVISAR-US.md").read_text(
                encoding="utf-8"
            )
            audit_wrapper = (project_root / "SESSION-AUDITAR-FEATURE.md").read_text(
                encoding="utf-8"
            )
            session_map = (project_root / "SESSION-MAPA.md").read_text(
                encoding="utf-8"
            )

            self.assertFalse((project_root / "SESSION-IMPLEMENTAR-ISSUE.md").exists())
            self.assertFalse((project_root / "SESSION-REVISAR-ISSUE.md").exists())
            self.assertFalse((project_root / "SESSION-AUDITAR-FASE.md").exists())

            self.assertIn("<resolver_na_user_story_elegivel_do_projeto>", implement_wrapper)
            self.assertIn("PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md", implement_wrapper)
            self.assertIn("REVIEW_MODE", review_wrapper)
            self.assertIn("<resolver_na_feature_pronta_para_gate>", audit_wrapper)
            self.assertIn(
                "wrappers de user story/revisao/auditoria nao devem congelar a fila na bootstrap",
                session_map,
            )

    def test_markdown_hrefs_sao_relativos_e_a_us_bootstrap_linka_prd_e_task(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            previous_cwd = Path.cwd()
            os.chdir(tmp_path)
            try:
                self.module.criar_projeto("TESTE")
            finally:
                os.chdir(previous_cwd)

            project_root = tmp_path / "PROJETOS" / "TESTE"
            for md_path in sorted(project_root.rglob("*.md")):
                body = md_path.read_text(encoding="utf-8")
                self.assertNotIn(
                    "](PROJETOS/",
                    body,
                    msg=f"href repo-relative invalido em {md_path.relative_to(project_root.parent)}",
                )

            user_story_readme = (
                project_root
                / "features"
                / "FEATURE-1-FOUNDATION"
                / "user-stories"
                / "US-1-01-BOOTSTRAP"
                / "README.md"
            ).read_text(encoding="utf-8")
            audit_report = (
                project_root
                / "features"
                / "FEATURE-1-FOUNDATION"
                / "auditorias"
                / "RELATORIO-AUDITORIA-F1-R01.md"
            ).read_text(encoding="utf-8")

            self.assertIn("[PRD do projeto](../../../../PRD-TESTE.md)", user_story_readme)
            self.assertRegex(user_story_readme, r"\[TASK-1\]\((\./)?TASK-1\.md\)")
            self.assertIn('scope_type: "feature"', audit_report)
            self.assertIn('followup_destination: "same-feature"', audit_report)

    def test_scaffold_popula_indice_sqlite_estruturado(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            previous_cwd = Path.cwd()
            os.chdir(tmp_path)
            try:
                self.module.criar_projeto("TESTE")
            finally:
                os.chdir(previous_cwd)

            db_path = tmp_path / "openclaw.sqlite"
            self.sync_module.run_sync(tmp_path, db_path, dry_run=False)

            import sqlite3

            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                "SELECT feature_key, path_relative FROM features ORDER BY feature_key"
            )
            feature = cur.fetchone()
            self.assertEqual(feature["feature_key"], "FEATURE-1-FOUNDATION")
            self.assertEqual(
                feature["path_relative"],
                "PROJETOS/TESTE/features/FEATURE-1-FOUNDATION",
            )

            cur.execute(
                "SELECT user_story_key, path_relative FROM user_stories ORDER BY user_story_key"
            )
            user_story = cur.fetchone()
            self.assertEqual(user_story["user_story_key"], "US-1-01-BOOTSTRAP")
            self.assertEqual(
                user_story["path_relative"],
                "PROJETOS/TESTE/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/README.md",
            )

            cur.execute("SELECT task_id, path_relative FROM tasks ORDER BY task_number")
            task = cur.fetchone()
            self.assertEqual(task["task_id"], "T1")
            self.assertEqual(
                task["path_relative"],
                "PROJETOS/TESTE/features/FEATURE-1-FOUNDATION/user-stories/US-1-01-BOOTSTRAP/TASK-1.md",
            )

            cur.execute(
                "SELECT report_key, feature_code FROM feature_audits ORDER BY report_key"
            )
            audit = cur.fetchone()
            self.assertEqual(audit["report_key"], "RELATORIO-AUDITORIA-F1-R01")
            self.assertEqual(audit["feature_code"], "FEATURE-1-FOUNDATION")

            conn.close()


if __name__ == "__main__":
    unittest.main()
