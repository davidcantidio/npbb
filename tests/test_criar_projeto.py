"""Scaffold-only tests for the local project generator."""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "criar_projeto.py"


def load_module():
    spec = importlib.util.spec_from_file_location("criar_projeto", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CriarProjetoTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def _criar_projeto_em_tmp(self) -> Path:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp_path = Path(tmp_dir.name)
        previous_cwd = Path.cwd()
        os.chdir(tmp_path)
        try:
            self.module.criar_projeto("TESTE")
        finally:
            os.chdir(previous_cwd)
        return tmp_path

    def test_scaffold_module_nao_depende_do_runtime_local_do_indice(self):
        source = SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertNotIn("openclaw_projects_index", source)
        self.assertNotIn("sync-openclaw-projects-db", source)
        self.assertNotIn("run_sync(", source)

    def test_scaffold_cria_arvore_feature_first(self):
        tmp_path = self._criar_projeto_em_tmp()
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
        tmp_path = self._criar_projeto_em_tmp()
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
        tmp_path = self._criar_projeto_em_tmp()
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

    def test_scaffold_gerado_nao_reintroduz_runtime_local_do_indice(self):
        tmp_path = self._criar_projeto_em_tmp()
        project_root = tmp_path / "PROJETOS" / "TESTE"
        forbidden_tokens = (
            "openclaw_projects_index",
            "sync-openclaw-projects-db",
            "OPENCLAW_PROJECTS_DATABASE_URL",
            ".openclaw/openclaw-projects.sqlite",
        )

        for md_path in sorted(project_root.rglob("*.md")):
            body = md_path.read_text(encoding="utf-8")
            for token in forbidden_tokens:
                self.assertNotIn(
                    token,
                    body,
                    msg=f"runtime local do indice reapareceu em {md_path.relative_to(tmp_path)}",
                )

if __name__ == "__main__":
    unittest.main()
