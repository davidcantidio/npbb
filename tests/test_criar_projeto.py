"""Testes para o gerador de projetos do framework."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from scripts import criar_projeto as criar_projeto_mod


def _project_root(base: Path, nome_projeto: str) -> Path:
    """Retorna a raiz do projeto criada dentro do ``tmp_path``."""
    return base / nome_projeto


def test_validar_nome_projeto_normaliza_para_maiusculas() -> None:
    """O nome do projeto deve ser normalizado antes da criacao."""
    assert criar_projeto_mod.validar_nome_projeto(" meu-projeto ") == "MEU-PROJETO"


@pytest.mark.parametrize("nome_invalido", ["", "foo/bar", "nome com espaco", "abc!"])
def test_validar_nome_projeto_rejeita_nomes_invalidos(nome_invalido: str) -> None:
    """Nomes fora da convencao devem ser rejeitados."""
    with pytest.raises(ValueError):
        criar_projeto_mod.validar_nome_projeto(nome_invalido)


def test_parse_args_preenche_defaults_e_flags() -> None:
    """A CLI deve expor defaults canonicos e aceitar flags customizadas."""
    opts = criar_projeto_mod.parse_args(
        [
            "meu-projeto",
            "--escopo",
            "apenas F<N>",
            "--profundidade",
            "fases+epicos+issues",
            "--task-mode",
            "por issue",
            "--observacoes",
            "validacao manual",
            "-v",
        ]
    )

    assert opts.nome_projeto == "MEU-PROJETO"
    assert opts.escopo == "apenas F<N>"
    assert opts.profundidade == "fases+epicos+issues"
    assert opts.task_mode == "por issue"
    assert opts.observacoes == "validacao manual"
    assert opts.verbose is True


def test_criar_estrutura_minima_gera_diretorios_canonicos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A estrutura minima deve criar raiz, feito e pastas da fase bootstrap."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)

    created = criar_projeto_mod.criar_estrutura_minima("MEU-PROJETO")

    root = _project_root(tmp_path, "MEU-PROJETO")
    assert root.is_dir()
    assert (root / "feito").is_dir()
    assert (root / "F1-FUNDACAO").is_dir()
    assert (root / "F1-FUNDACAO" / "issues").is_dir()
    assert (root / "F1-FUNDACAO" / "sprints").is_dir()
    assert (root / "F1-FUNDACAO" / "auditorias").is_dir()
    assert root in created


def test_criar_arquivos_base_preenche_scaffold_completo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Os arquivos base devem sair prontos, sem placeholders residuais."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)

    criar_projeto_mod.criar_estrutura_minima("MEU-PROJETO")
    created = criar_projeto_mod.criar_arquivos_base("MEU-PROJETO")

    root = _project_root(tmp_path, "MEU-PROJETO")
    issue_dir = root / "F1-FUNDACAO" / "issues" / "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"

    expected_files = [
        "INTAKE-MEU-PROJETO.md",
        "PRD-MEU-PROJETO.md",
        "AUDIT-LOG.md",
        "SESSION-PLANEJAR-PROJETO.md",
        "SESSION-CRIAR-INTAKE.md",
        "SESSION-CRIAR-PRD.md",
        "SESSION-IMPLEMENTAR-ISSUE.md",
        "SESSION-REVISAR-ISSUE.md",
        "SESSION-AUDITAR-FASE.md",
        "SESSION-REMEDIAR-HOLD.md",
        "SESSION-REFATORAR-MONOLITO.md",
        "SESSION-MAPA.md",
        "F1-FUNDACAO/F1_MEU-PROJETO_EPICS.md",
        "F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md",
        "F1-FUNDACAO/sprints/SPRINT-F1-01.md",
        "F1-FUNDACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md",
    ]
    for rel_path in expected_files:
        assert (root / rel_path).exists()
    assert (issue_dir / "README.md").exists()
    assert (issue_dir / "TASK-1.md").exists()
    assert len(created) == 18

    planner = (root / "SESSION-PLANEJAR-PROJETO.md").read_text(encoding="utf-8")
    assert "PROJETO:       MEU-PROJETO" in planner
    assert "PRD_PATH:      PROJETOS/MEU-PROJETO/PRD-MEU-PROJETO.md" in planner
    assert "ESCOPO:        projeto completo" in planner
    assert "PROFUNDIDADE:  completo" in planner
    assert "TASK_MODE:     required" in planner
    assert "OBSERVACOES:   nenhuma" in planner
    assert "<nome do projeto" not in planner

    intake = (root / "INTAKE-MEU-PROJETO.md").read_text(encoding="utf-8")
    prd = (root / "PRD-MEU-PROJETO.md").read_text(encoding="utf-8")
    assert 'doc_id: "INTAKE-MEU-PROJETO.md"' in intake
    assert 'project: "MEU-PROJETO"' in intake
    assert "<PROJETO>" not in intake
    assert 'doc_id: "PRD-MEU-PROJETO.md"' in prd
    assert "<PROJETO>" not in prd

    issue_readme = (issue_dir / "README.md").read_text(encoding="utf-8")
    task = (issue_dir / "TASK-1.md").read_text(encoding="utf-8")
    assert 'doc_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"' in issue_readme
    assert 'task_instruction_mode: "required"' in issue_readme
    assert 'issue_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"' in task
    assert "tdd_aplicavel: false" in task
    assert "<PROJETO>" not in issue_readme
    assert "<PROJETO>" not in task

    implement = (root / "SESSION-IMPLEMENTAR-ISSUE.md").read_text(encoding="utf-8")
    assert "ISSUE_ID:" in implement
    assert "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO" in implement
    assert "ISSUE_PATH:" in implement
    assert "PROJETOS/MEU-PROJETO/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO" in implement


def test_criar_projeto_rejeita_projeto_existente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Uma pasta de projeto ja existente nao pode ser sobrescrita."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)

    (tmp_path / "OMEGA").mkdir()

    with pytest.raises(FileExistsError):
        criar_projeto_mod.criar_projeto("OMEGA")


def test_main_smoke_creates_project_and_returns_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A CLI deve conseguir criar um projeto completo em modo verbose."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)

    exit_code = criar_projeto_mod.main(["MEU-PROJETO", "-v"])

    assert exit_code == 0
    assert (tmp_path / "MEU-PROJETO" / "SESSION-MAPA.md").exists()
    assert "PROJETO CRIADO: MEU-PROJETO" in capsys.readouterr().out


def test_public_functions_have_docstrings() -> None:
    """As funcoes publicas do script devem manter docstrings."""
    publicas = [
        criar_projeto_mod.validar_nome_projeto,
        criar_projeto_mod.build_argument_parser,
        criar_projeto_mod.parse_args,
        criar_projeto_mod.criar_estrutura_minima,
        criar_projeto_mod.criar_arquivos_base,
        criar_projeto_mod.criar_projeto,
        criar_projeto_mod.main,
    ]
    for func in publicas:
        assert inspect.getdoc(func)
