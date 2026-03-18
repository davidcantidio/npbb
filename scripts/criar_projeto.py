#!/usr/bin/env python3
"""Cria um novo projeto em ``PROJETOS/`` seguindo a convencao do framework.

Usage:
    python3 scripts/criar_projeto.py <NOME_DO_PROJETO> [-v]

Example:
    python3 scripts/criar_projeto.py MEU-PROJETO -v
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


COMUM_DIR = Path("PROJETOS/COMUM")
PROJETOS_DIR = Path("PROJETOS")
SESSION_FILES = [
    "SESSION-PLANEJAR-PROJETO.md",
    "SESSION-IMPLEMENTAR-ISSUE.md",
    "SESSION-AUDITAR-FASE.md",
    "SESSION-REVISAR-ISSUE.md",
    "SESSION-CRIAR-PRD.md",
    "SESSION-CRIAR-INTAKE.md",
    "SESSION-REFATORAR-MONOLITO.md",
    "SESSION-REMEDIAR-HOLD.md",
    "SESSION-MAPA.md",
]


def validar_nome_projeto(nome_projeto: str) -> str:
    """Normaliza e valida o nome do projeto.

    O nome final usa maiusculas e aceita apenas letras, numeros, hifenes e
    sublinhados.
    """
    nome_normalizado = nome_projeto.strip().upper()
    if not nome_normalizado:
        raise ValueError("nome do projeto vazio")
    if not re.fullmatch(r"[A-Z0-9_-]+", nome_normalizado):
        raise ValueError(
            "O nome do projeto deve conter apenas letras, números, hífens e sublinhados"
        )
    return nome_normalizado


def _render_template(conteudo: str, nome_projeto: str, nome_arquivo: str) -> str:
    """Substitui placeholders canonicos no template pelo nome do projeto."""
    return (
        conteudo.replace('doc_id: "TEMPLATE-INTAKE"', f'doc_id: "{nome_arquivo}"')
        .replace('doc_id: "TEMPLATE-PRD"', f'doc_id: "{nome_arquivo}"')
        .replace("<PROJETO>", nome_projeto)
        .replace("INTAKE-<PROJETO>.md", f"INTAKE-{nome_projeto}.md")
        .replace("PRD-<PROJETO>.md", f"PRD-{nome_projeto}.md")
    )


def _escrever_template(origem: Path, destino: Path, nome_projeto: str) -> None:
    """Copia um template de texto aplicando substituicoes canonicas."""
    conteudo = origem.read_text(encoding="utf-8")
    destino.write_text(_render_template(conteudo, nome_projeto, destino.name), encoding="utf-8")


def _copiar_arquivo(origem: Path, destino: Path, nome_projeto: str) -> None:
    """Copia ou renderiza um arquivo do framework para o novo projeto."""
    if origem.name in {"TEMPLATE-INTAKE.md", "TEMPLATE-PRD.md"}:
        _escrever_template(origem, destino, nome_projeto)
        return
    shutil.copy2(origem, destino)


def criar_estrutura_minima(projeto_dir: Path) -> None:
    """Cria a arvore minima do projeto."""
    (projeto_dir / "feito").mkdir(parents=True, exist_ok=False)


def criar_arquivos_base(nome_projeto: str, projeto_dir: Path, verbose: bool = False) -> list[str]:
    """Cria os artefatos canonicos na raiz do projeto.

    Retorna a lista de caminhos relativos criados.
    """
    criados: list[str] = []
    mapa_arquivos = [
        (COMUM_DIR / "TEMPLATE-INTAKE.md", projeto_dir / f"INTAKE-{nome_projeto}.md"),
        (COMUM_DIR / "TEMPLATE-PRD.md", projeto_dir / f"PRD-{nome_projeto}.md"),
    ]

    for nome_session in SESSION_FILES:
        mapa_arquivos.append((COMUM_DIR / nome_session, projeto_dir / nome_session))

    for origem, destino in mapa_arquivos:
        if not origem.exists():
            raise FileNotFoundError(f"Arquivo base nao encontrado: {origem}")
        _copiar_arquivo(origem, destino, nome_projeto)
        criados.append(str(destino.relative_to(projeto_dir)))
        if verbose:
            print(f"  ✓ {origem.name} -> {destino.name}")

    audit_log = projeto_dir / "AUDIT-LOG.md"
    audit_log.write_text(
        "\n".join(
            [
                "---",
                'doc_id: "AUDIT-LOG.md"',
                'version: "1.0"',
                'status: "active"',
                'owner: "PM"',
                'last_updated: "YYYY-MM-DD"',
                "---",
                "",
                f"# AUDIT-LOG - {nome_projeto}",
                "",
                "## Politica",
                "",
                "- toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`",
                "- toda rodada deve registrar commit base, veredito e categoria dos achados materiais",
                "- auditoria `hold` abre follow-ups rastreaveis",
                "- follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`",
                "- auditoria `go` e pre-requisito para mover fase a `feito/`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    criados.append("AUDIT-LOG.md")

    return criados


def criar_projeto(nome_projeto: str, verbose: bool = False) -> list[str]:
    """Cria um novo projeto com a estrutura minima do framework."""
    projeto_dir = PROJETOS_DIR / nome_projeto
    if projeto_dir.exists():
        raise FileExistsError(f"Projeto '{nome_projeto}' já existe em {projeto_dir}")

    projeto_dir.mkdir(parents=True, exist_ok=False)
    criar_estrutura_minima(projeto_dir)

    if verbose:
        print(f"✓ Diretório criado: {projeto_dir}")
        print(f"✓ Estrutura criada: {projeto_dir / 'feito'}")

    criados = criar_arquivos_base(nome_projeto, projeto_dir, verbose=verbose)

    print("\n" + "=" * 60)
    print(f"PROJETO CRIADO: {nome_projeto}")
    print("=" * 60)
    print(f"Localização: {projeto_dir}")
    print(f"Arquivos criados: {len(criados)}")
    print("\nPróximo passo: preencha INTAKE-{0}.md e PRD-{0}.md".format(nome_projeto))

    return criados


def main() -> int:
    """Executa a interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Cria um novo projeto em PROJETOS/ com os arquivos base do framework"
    )
    parser.add_argument("nome_projeto", type=str, help="Nome do projeto a ser criado")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mostra detalhes da operação")

    args = parser.parse_args()

    try:
        nome_projeto = validar_nome_projeto(args.nome_projeto)
        criar_projeto(nome_projeto, verbose=args.verbose)
        return 0
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        print(f"Erro: {exc}")
        return 1
    except Exception as exc:
        print(f"Erro inesperado: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
