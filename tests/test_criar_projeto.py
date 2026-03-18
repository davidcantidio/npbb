"""Testes para o gerador de projetos do framework."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from scripts import criar_projeto as criar_projeto_mod


def test_validar_nome_projeto_normaliza_para_maiusculas() -> None:
    """O nome do projeto e normalizado e validado antes da criacao."""
    assert criar_projeto_mod.validar_nome_projeto(" meu-projeto ") == "MEU-PROJETO"


@pytest.mark.parametrize("nome_invalido", ["", "foo/bar", "nome com espaco", "abc!"])
def test_validar_nome_projeto_rejeita_nomes_invalidos(nome_invalido: str) -> None:
    """Nomes fora da convencao devem ser rejeitados."""
    with pytest.raises(ValueError):
        criar_projeto_mod.validar_nome_projeto(nome_invalido)


def test_criar_projeto_gera_estrutura_canonica(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A criacao do projeto usa os nomes canonicos do framework."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)
    monkeypatch.setattr(criar_projeto_mod, "COMUM_DIR", Path("PROJETOS/COMUM"))

    criados = criar_projeto_mod.criar_projeto("MEU-PROJETO")

    projeto_dir = tmp_path / "MEU-PROJETO"
    assert projeto_dir.exists()
    assert (projeto_dir / "feito").is_dir()
    assert (projeto_dir / "INTAKE-MEU-PROJETO.md").exists()
    assert (projeto_dir / "PRD-MEU-PROJETO.md").exists()
    assert (projeto_dir / "AUDIT-LOG.md").exists()
    assert (projeto_dir / "SESSION-PLANEJAR-PROJETO.md").exists()
    assert not any(path.startswith("MEU-PROJETO-SESSION-") for path in criados)
    assert "SESSION-PLANEJAR-PROJETO.md" in criados
    assert "INTAKE-MEU-PROJETO.md" in criados
    assert "PRD-MEU-PROJETO.md" in criados
    assert "AUDIT-LOG.md" in criados


def test_criar_projeto_preserva_placeholders_basicos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Os templates gerados devem substituir placeholders canonicos."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)
    monkeypatch.setattr(criar_projeto_mod, "COMUM_DIR", Path("PROJETOS/COMUM"))

    criar_projeto_mod.criar_projeto("ALFA")

    intake = (tmp_path / "ALFA" / "INTAKE-ALFA.md").read_text(encoding="utf-8")
    prd = (tmp_path / "ALFA" / "PRD-ALFA.md").read_text(encoding="utf-8")

    assert "INTAKE-ALFA.md" in intake
    assert 'doc_id: "INTAKE-ALFA.md"' in intake
    assert "<PROJETO>" not in intake
    assert 'doc_id: "PRD-ALFA.md"' in prd
    assert "<PROJETO>" not in prd


def test_criar_projeto_rejeita_projeto_existente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Uma pasta de projeto ja existente nao pode ser sobrescrita."""
    monkeypatch.setattr(criar_projeto_mod, "PROJETOS_DIR", tmp_path)
    monkeypatch.setattr(criar_projeto_mod, "COMUM_DIR", Path("PROJETOS/COMUM"))

    (tmp_path / "OMEGA").mkdir()

    with pytest.raises(FileExistsError):
        criar_projeto_mod.criar_projeto("OMEGA")


def test_public_functions_have_docstrings() -> None:
    """As funcoes publicas do script devem manter docstrings."""
    publicas = [
        criar_projeto_mod.validar_nome_projeto,
        criar_projeto_mod.criar_estrutura_minima,
        criar_projeto_mod.criar_arquivos_base,
        criar_projeto_mod.criar_projeto,
        criar_projeto_mod.main,
    ]
    for func in publicas:
        assert inspect.getdoc(func)
