#!/usr/bin/env python3
"""Cria um novo projeto em ``PROJETOS/`` com scaffold canonico preenchido."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import Callable, Sequence


DEFAULT_ESCOPO = "projeto completo"
DEFAULT_PROFUNDIDADE = "completo"
DEFAULT_TASK_MODE = "required"
DEFAULT_OBSERVACOES = "nenhuma"

PROJETOS_DIR = Path("PROJETOS")

BOOTSTRAP_PHASE_DIR = "F1-FUNDACAO"
BOOTSTRAP_PHASE_ID = "F1"
BOOTSTRAP_PHASE_LABEL = "Fundacao do projeto"
BOOTSTRAP_FEATURE_ID = "Feature 1"
BOOTSTRAP_EPIC_ID = "EPIC-F1-01"
BOOTSTRAP_EPIC_LABEL = "Fundacao do projeto"
BOOTSTRAP_ISSUE_ID = "ISSUE-F1-01-001"
BOOTSTRAP_ISSUE_SLUG = "ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
BOOTSTRAP_ISSUE_DOC_ID = f"{BOOTSTRAP_ISSUE_ID}-{BOOTSTRAP_ISSUE_SLUG}"
BOOTSTRAP_ISSUE_TITLE = "Estabilizar scaffold inicial do projeto"
BOOTSTRAP_EPIC_SLUG = "FUNDACAO-DO-PROJETO"
BOOTSTRAP_EPIC_FILENAME = f"{BOOTSTRAP_EPIC_ID}-{BOOTSTRAP_EPIC_SLUG}.md"
BOOTSTRAP_TASK_ID = "T1"
BOOTSTRAP_ROUND = "R01"
BOOTSTRAP_SPRINT_ID = "SPRINT-F1-01"
BOOTSTRAP_AUDIT_REPORT = f"RELATORIO-AUDITORIA-{BOOTSTRAP_PHASE_ID}-{BOOTSTRAP_ROUND}.md"


@dataclass(frozen=True)
class ScaffoldOptions:
    """Opcao de CLI normalizada para a criacao do projeto."""

    nome_projeto: str
    escopo: str = DEFAULT_ESCOPO
    profundidade: str = DEFAULT_PROFUNDIDADE
    task_mode: str = DEFAULT_TASK_MODE
    observacoes: str = DEFAULT_OBSERVACOES
    verbose: bool = False


@dataclass(frozen=True)
class ProjectPaths:
    """Agrupa caminhos fisicos e referenciais do projeto gerado."""

    filesystem_root: Path
    project_ref: Path
    feito_dir: Path
    phase_dir: Path
    issues_dir: Path
    sprints_dir: Path
    auditorias_dir: Path
    intake_path: Path
    prd_path: Path
    audit_log_path: Path
    phase_manifest_path: Path
    epic_manifest_path: Path
    issue_dir: Path
    issue_readme_path: Path
    task1_path: Path
    sprint_path: Path
    audit_report_path: Path
    session_plan_path: Path
    session_create_intake_path: Path
    session_create_prd_path: Path
    session_implement_issue_path: Path
    session_review_issue_path: Path
    session_audit_phase_path: Path
    session_remediate_hold_path: Path
    session_refactor_monolith_path: Path
    session_map_path: Path


@dataclass(frozen=True)
class ProjectContext:
    """Contexto derivado usado pelos renderizadores de artefato."""

    options: ScaffoldOptions
    paths: ProjectPaths
    today: str

    def rel(self, *parts: str) -> str:
        """Retorna caminho repo-relative dentro de ``PROJETOS/<PROJETO>``."""
        return self.paths.project_ref.joinpath(*parts).as_posix()


@dataclass(frozen=True)
class ScaffoldItem:
    """Representa um artefato a criar, arquivo ou diretorio."""

    path: Path
    kind: str
    renderer: Callable[[ProjectContext], str] | None = None


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
            "O nome do projeto deve conter apenas letras, numeros, hifenes e sublinhados"
        )
    return nome_normalizado


def build_argument_parser() -> argparse.ArgumentParser:
    """Cria o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        description="Cria um novo projeto em PROJETOS/ com o scaffold canonico preenchido"
    )
    parser.add_argument("nome_projeto", type=str, help="Nome do projeto a ser criado")
    parser.add_argument(
        "--escopo",
        default=DEFAULT_ESCOPO,
        choices=["projeto completo", "apenas F<N>", "apenas EPIC-F<N>-<NN>"],
        help="Escopo predefinido para SESSION-PLANEJAR-PROJETO",
    )
    parser.add_argument(
        "--profundidade",
        default=DEFAULT_PROFUNDIDADE,
        choices=["fases", "fases+epicos", "fases+epicos+issues", "completo"],
        help="Profundidade predefinida para SESSION-PLANEJAR-PROJETO",
    )
    parser.add_argument(
        "--task-mode",
        default=DEFAULT_TASK_MODE,
        choices=["optional", "required", "por issue"],
        help="Modo de task predefinido para SESSION-PLANEJAR-PROJETO",
    )
    parser.add_argument(
        "--observacoes",
        default=DEFAULT_OBSERVACOES,
        help="Observacoes predefinidas para os wrappers gerados",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mostra detalhes da operacao",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> ScaffoldOptions:
    """Parseia argumentos de CLI e devolve uma configuracao normalizada."""
    namespace = build_argument_parser().parse_args(argv)
    return ScaffoldOptions(
        nome_projeto=validar_nome_projeto(namespace.nome_projeto),
        escopo=namespace.escopo,
        profundidade=namespace.profundidade,
        task_mode=namespace.task_mode,
        observacoes=namespace.observacoes,
        verbose=namespace.verbose,
    )


def _today() -> str:
    """Retorna a data corrente no formato ISO."""
    return date.today().isoformat()


def _ensure_dir(path: Path) -> None:
    """Cria diretorio, falhando se o caminho ja existir como arquivo."""
    if path.exists() and not path.is_dir():
        raise FileExistsError(f"Caminho ja existe como arquivo: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, content: str) -> None:
    """Escreve texto UTF-8 e garante newline final."""
    path.write_text(_normalize_document_text(content), encoding="utf-8")


def _yaml_scalar(value: str) -> str:
    """Formata um escalar YAML simples com aspas duplas."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _frontmatter(entries: Sequence[tuple[str, object]]) -> str:
    """Renderiza frontmatter YAML com ordem explicitamente declarada."""
    lines = ["---"]
    for key, value in entries:
        if isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key}: {value}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {_yaml_scalar(str(item))}")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {_yaml_scalar(str(value))}")
    lines.append("---")
    return "\n".join(lines)


def _normalize_document_text(text: str) -> str:
    """Remove a indentacao residual produzida pelos templates de renderizacao."""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""

    if lines[0].strip() != "---":
        return dedent("\n".join(lines)).strip() + "\n"

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return dedent("\n".join(lines)).strip() + "\n"

    frontmatter_lines = lines[: closing_index + 1]
    middle_lines = frontmatter_lines[1:-1]
    leading_spaces = [
        len(line) - len(line.lstrip(" "))
        for line in middle_lines
        if line.strip()
    ]
    indent = min(leading_spaces) if leading_spaces else 0

    normalized_frontmatter = [frontmatter_lines[0]]
    for line in middle_lines:
        if indent and line.startswith(" " * indent):
            normalized_frontmatter.append(line[indent:])
        else:
            normalized_frontmatter.append(line.lstrip())
    normalized_frontmatter.append(frontmatter_lines[-1])

    body_lines = lines[closing_index + 1 :]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    normalized_body_lines = [
        line[8:] if line.startswith("        ") else line for line in body_lines
    ]
    body = "\n".join(normalized_body_lines).strip()
    if body:
        return "\n".join(normalized_frontmatter) + "\n\n" + body + "\n"
    return "\n".join(normalized_frontmatter) + "\n"


def _code_block(lines: Sequence[str], language: str = "text") -> str:
    """Renderiza um bloco de codigo simples."""
    return "```" + language + "\n" + "\n".join(lines) + "\n```"


def _bullet_list(items: Sequence[str]) -> str:
    """Renderiza uma lista de bullets."""
    return "\n".join(f"- {item}" for item in items)


def _table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Renderiza tabela markdown."""
    def _cell(value: str) -> str:
        return value.replace("|", "\\|")

    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(_cell(str(item)) for item in row) + " |")
    return "\n".join(lines)


def _build_paths(options: ScaffoldOptions) -> ProjectPaths:
    """Deriva caminhos fisicos e referencias do scaffold."""
    filesystem_root = PROJETOS_DIR / options.nome_projeto
    project_ref = Path("PROJETOS") / options.nome_projeto
    phase_dir = filesystem_root / BOOTSTRAP_PHASE_DIR
    issues_dir = phase_dir / "issues"
    issue_dir = issues_dir / BOOTSTRAP_ISSUE_DOC_ID
    auditorias_dir = phase_dir / "auditorias"
    sprints_dir = phase_dir / "sprints"

    return ProjectPaths(
        filesystem_root=filesystem_root,
        project_ref=project_ref,
        feito_dir=filesystem_root / "feito",
        phase_dir=phase_dir,
        issues_dir=issues_dir,
        sprints_dir=sprints_dir,
        auditorias_dir=auditorias_dir,
        intake_path=filesystem_root / f"INTAKE-{options.nome_projeto}.md",
        prd_path=filesystem_root / f"PRD-{options.nome_projeto}.md",
        audit_log_path=filesystem_root / "AUDIT-LOG.md",
        phase_manifest_path=phase_dir / f"F1_{options.nome_projeto}_EPICS.md",
        epic_manifest_path=phase_dir / BOOTSTRAP_EPIC_FILENAME,
        issue_dir=issue_dir,
        issue_readme_path=issue_dir / "README.md",
        task1_path=issue_dir / "TASK-1.md",
        sprint_path=sprints_dir / f"{BOOTSTRAP_SPRINT_ID}.md",
        audit_report_path=auditorias_dir / BOOTSTRAP_AUDIT_REPORT,
        session_plan_path=filesystem_root / "SESSION-PLANEJAR-PROJETO.md",
        session_create_intake_path=filesystem_root / "SESSION-CRIAR-INTAKE.md",
        session_create_prd_path=filesystem_root / "SESSION-CRIAR-PRD.md",
        session_implement_issue_path=filesystem_root / "SESSION-IMPLEMENTAR-ISSUE.md",
        session_review_issue_path=filesystem_root / "SESSION-REVISAR-ISSUE.md",
        session_audit_phase_path=filesystem_root / "SESSION-AUDITAR-FASE.md",
        session_remediate_hold_path=filesystem_root / "SESSION-REMEDIAR-HOLD.md",
        session_refactor_monolith_path=filesystem_root / "SESSION-REFATORAR-MONOLITO.md",
        session_map_path=filesystem_root / "SESSION-MAPA.md",
    )


def _build_context(options: ScaffoldOptions) -> ProjectContext:
    """Constrói o contexto completo do scaffold."""
    return ProjectContext(options=options, paths=_build_paths(options), today=_today())


def _coerce_options(options: ScaffoldOptions | str) -> ScaffoldOptions:
    """Normaliza entradas aceitando ``ScaffoldOptions`` ou nome bruto."""
    if isinstance(options, ScaffoldOptions):
        return options
    return ScaffoldOptions(nome_projeto=validar_nome_projeto(options))


def _render_intake(context: ProjectContext) -> str:
    """Renderiza o intake inicial do projeto."""
    project = context.options.nome_projeto
    rel = context.rel
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", f"INTAKE-{project}.md"),
            ("version", "1.0"),
            ("status", "draft"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
            ("intake_kind", "new-product"),
            ("source_mode", "original"),
            ("origin_project", "nao_aplicavel"),
            ("origin_phase", "nao_aplicavel"),
            ("origin_audit_id", "nao_aplicavel"),
            ("origin_report_path", "nao_aplicavel"),
            ("product_type", "platform-capability"),
            ("delivery_surface", "docs-governance"),
            ("business_domain", "governanca"),
            ("criticality", "media"),
            ("data_sensitivity", "interna"),
            ("integrations", ["PROJETOS/COMUM"]),
            ("change_type", "nova-capacidade"),
            ("audit_rigor", "standard"),
        ])}

        # INTAKE - {project}

        > Scaffold inicial do projeto {project} para que intake, PRD, wrappers e
        > bootstrap de fase sejam criados sem preenchimento manual repetitivo.

        ## 0. Rastreabilidade de Origem

        - projeto de origem: nao_aplicavel
        - fase de origem: nao_aplicavel
        - auditoria de origem: nao_aplicavel
        - relatorio de origem: nao_aplicavel
        - motivo da abertura deste intake: gerar um projeto novo com scaffold canônico e wrappers prontos para uso

        ## 1. Resumo Executivo

        - nome curto da iniciativa: scaffold canônico do projeto
        - tese em 1 frase: criar um projeto pronto para planejamento e execucao sem preencher manualmente os cabecalhos principais
        - valor esperado em 3 linhas:
          - intake, PRD, audit log e wrappers locais prontos
          - primeira fase, epico e issue bootstrap gerados
          - menos drift e menor tempo de arranque para o projeto

        ## 2. Problema ou Oportunidade

        - problema atual: iniciar um projeto manualmente cria inconsistencias de nomes, caminhos e metadados
        - evidencia do problema: os artefatos de projeto exigem varios campos repetidos e faceis de esquecer
        - custo de nao agir: o primeiro ciclo do projeto comeca com drift documental e retrabalho
        - por que agora: o scaffold foi solicitado como ponto de partida oficial do novo projeto

        ## 3. Publico e Operadores

        - usuario principal: PM e engenheiro que vao planejar o projeto
        - usuario secundario: revisor ou auditor do fluxo de projeto
        - operador interno: script `scripts/criar_projeto.py`
        - quem aprova ou patrocina: PM

        ## 4. Jobs to be Done

        - job principal: criar um projeto novo pronto para planejamento e execucao
        - jobs secundarios: preencher cabecalhos comuns, evitar drift de nomes e publicar o bootstrap inicial
        - tarefa atual que sera substituida: montar a estrutura do projeto manualmente

        ## 5. Fluxo Principal Desejado

        Descreva o fluxo ponta a ponta em etapas curtas:

        1. Informar o nome do projeto e os defaults de planejamento.
        2. Gerar intake, PRD, audit log e wrappers locais com caminhos repo-relative.
        3. Criar a fase F1-FUNDACAO com epico, issue granularizada e task.
        4. Deixar o projeto pronto para planejamento, implementacao e auditoria.

        ## 6. Escopo Inicial

        ### Dentro

        - scaffold inicial do projeto
        - wrappers de sessao prontos para uso
        - fase bootstrap com issue granularizada

        ### Fora

        - features de negocio reais do projeto
        - implementacao de codigo de produto
        - deploy ou integrações externas

        ## 7. Resultado de Negocio e Metricas

        - objetivo principal: reduzir o custo de arranque de novos projetos
        - metricas leading: numero de campos prefillados; numero de placeholders manuais restantes
        - metricas lagging: tempo para iniciar o planejamento; numero de ajustes de drift no bootstrap
        - criterio minimo para considerar sucesso: o projeto nasce com docs e wrappers prontos para uso

        ## 8. Restricoes e Guardrails

        - restricoes tecnicas: manter nomes canônicos e caminhos repo-relative
        - restricoes operacionais: nao exigir preenchimento manual dos cabecalhos principais
        - restricoes legais ou compliance: nenhuma
        - restricoes de prazo: nenhuma
        - restricoes de design ou marca: nenhuma

        ## 9. Dependencias e Integracoes

        - sistemas internos impactados: `PROJETOS/COMUM` e o proprio scaffold do projeto
        - sistemas externos impactados: nao aplicavel
        - dados de entrada necessarios: nome do projeto e defaults de planejamento
        - dados de saida esperados: docs preenchidos, wrappers prontos e bootstrap inicial

        ## 10. Arquitetura Afetada

        - backend: nao aplicavel
        - frontend: nao aplicavel
        - banco/migracoes: nao aplicavel
        - observabilidade: audit log e relatorio base de fase
        - autorizacao/autenticacao: nao aplicavel
        - rollout: uso local do scaffold gerado

        ## 11. Riscos Relevantes

        - risco de produto: baixo, porque o objetivo e estrutural
        - risco tecnico: drift entre nome do arquivo, doc_id e caminhos
        - risco operacional: wrappers ainda exigirem ajustes manuais se a geracao falhar
        - risco de dados: nenhum
        - risco de adocao: o PM ainda pode preferir um bootstrap sem defaults

        ## 12. Nao-Objetivos

        - nao definir features de negocio reais
        - nao implementar codigo de aplicacao
        - nao executar deploy

        ## 13. Contexto Especifico para Problema ou Refatoracao

        - sintoma observado: projeto novo sem estrutura canônica
        - impacto operacional: necessidade de preencher manualmente sessoes e docs
        - evidencia tecnica: o gerador precisa criar wrappers, phase bootstrap e artefatos base
        - componente(s) afetado(s): `scripts/criar_projeto.py`, `PROJETOS/COMUM` e os novos arquivos do projeto
        - riscos de nao agir: cada novo projeto diverge do padrao e aumenta retrabalho

        ## 14. Lacunas Conhecidas

        - nenhuma no nivel de scaffold
        """
    ).strip() + "\n"


def _render_prd(context: ProjectContext) -> str:
    """Renderiza o PRD inicial do projeto."""
    project = context.options.nome_projeto
    rel = context.rel

    feature_criteria = _bullet_list(
        [
            "intake, PRD, audit log e wrappers locais sao gerados com caminhos repo-relative",
            "fase F1-FUNDACAO, epic e issue bootstrap existem e apontam para Feature 1",
            "nao existem placeholders de frontmatter nem drifts entre doc_id e nome do arquivo",
        ]
    )

    feature_table = _table(
        ["Task ID", "Descricao", "SP", "Depende de"],
        [
            ["T1", "Gerar docs base e metadados do projeto", "2", "-"],
            ["T2", "Gerar wrappers locais e bootstrap F1", "3", "T1"],
            ["T3", "Validar tree final, links e doc_ids", "2", "T2"],
        ],
    )

    phase_table = _table(
        ["Epico", "Feature(s)", "Status", "SP Total"],
        [["EPIC-F1-01", "Feature 1", "todo", "7"]],
    )

    issue_table = _table(
        ["Issue ID", "Nome", "SP", "Status", "Feature"],
        [[BOOTSTRAP_ISSUE_DOC_ID, BOOTSTRAP_ISSUE_TITLE, "3", "todo", "Feature 1"]],
    )

    dependency_table = _table(
        ["Dependencia", "Tipo", "Origem", "Impacto", "Status"],
        [["PROJETOS/COMUM", "docs-governance", "framework", "fonte canônica do scaffold", "active"]],
    )

    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", f"PRD-{project}.md"),
            ("version", "1.0"),
            ("status", "draft"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
            ("intake_kind", "new-product"),
            ("source_mode", "original"),
            ("origin_project", "nao_aplicavel"),
            ("origin_phase", "nao_aplicavel"),
            ("origin_audit_id", "nao_aplicavel"),
            ("origin_report_path", "nao_aplicavel"),
            ("product_type", "platform-capability"),
            ("delivery_surface", "docs-governance"),
            ("business_domain", "governanca"),
            ("criticality", "media"),
            ("data_sensitivity", "interna"),
            ("integrations", ["PROJETOS/COMUM"]),
            ("change_type", "nova-capacidade"),
            ("audit_rigor", "standard"),
        ])}

        # PRD - {project}

        > Origem: [INTAKE-{project}.md]({rel(f"INTAKE-{project}.md")})
        >
        > Este PRD descreve o scaffold canônico do projeto, nao um produto de negocio
        > final. A intencao e deixar o projeto pronto para planejamento e execucao.

        ## 0. Rastreabilidade

        - **Intake de origem**: [INTAKE-{project}.md]({rel(f"INTAKE-{project}.md")})
        - **Versao do intake**: 1.0
        - **Data de criacao**: {context.today}
        - **PRD derivado**: nao aplicavel

        ## 1. Resumo Executivo

        - **Nome do projeto**: {project}
        - **Tese em 1 frase**: criar um projeto pronto para planejamento e execucao sem preenchimento manual dos cabecalhos principais
        - **Valor esperado em 3 linhas**:
          - intake, PRD, audit log e wrappers locais prontos
          - primeira fase, epico e issue bootstrap gerados
          - menos drift e menor tempo de arranque para o projeto

        ## 2. Problema ou Oportunidade

        - **Problema atual**: iniciar um projeto manualmente cria inconsistencias de nomes, caminhos e metadados
        - **Evidencia do problema**: os artefatos de projeto exigem varios campos repetidos e faceis de esquecer
        - **Custo de nao agir**: o primeiro ciclo do projeto comeca com drift documental e retrabalho
        - **Por que agora**: o scaffold foi solicitado como ponto de partida oficial do novo projeto

        ## 3. Publico e Operadores

        - **Usuario principal**: PM e engenheiro que vao planejar o projeto
        - **Usuario secundario**: revisor ou auditor do fluxo de projeto
        - **Operador interno**: script `scripts/criar_projeto.py`
        - **Quem aprova ou patrocina**: PM

        ## 4. Jobs to be Done

        - **Job principal**: criar um projeto novo pronto para planejamento e execucao
        - **Jobs secundarios**: preencher cabecalhos comuns, evitar drift de nomes e publicar o bootstrap inicial
        - **Tarefa atual que sera substituida**: montar a estrutura do projeto manualmente

        ## 5. Escopo

        ### Dentro

        - scaffold inicial do projeto
        - wrappers de sessao prontos para uso
        - fase bootstrap com issue granularizada

        ### Fora

        - features de negocio reais do projeto
        - implementacao de codigo de produto
        - deploy ou integrações externas

        ## 6. Resultado de Negocio e Metricas

        - **Objetivo principal**: reduzir o custo de arranque de novos projetos
        - **Metricas leading**: numero de campos prefillados; numero de placeholders manuais restantes
        - **Metricas lagging**: tempo para iniciar o planejamento; numero de ajustes de drift no bootstrap
        - **Criterio minimo para considerar sucesso**: o projeto nasce com docs e wrappers prontos para uso

        ## 7. Restricoes e Guardrails

        - **Restricoes tecnicas**: manter nomes canônicos e caminhos repo-relative
        - **Restricoes operacionais**: nao exigir preenchimento manual dos cabecalhos principais
        - **Restricoes legais ou compliance**: nenhuma
        - **Restricoes de prazo**: nenhuma
        - **Restricoes de design ou marca**: nenhuma

        ## 8. Dependencias e Integracoes

        - **Sistemas internos impactados**: `PROJETOS/COMUM` e o proprio scaffold do projeto
        - **Sistemas externos impactados**: nao aplicavel
        - **Dados de entrada necessarios**: nome do projeto e defaults de planejamento
        - **Dados de saida esperados**: docs preenchidos, wrappers prontos e bootstrap inicial

        ## 9. Arquitetura Geral do Projeto

        > Visao geral de impacto arquitetural (detalhes por feature na secao Features)

        - **Backend**: nao aplicavel
        - **Frontend**: nao aplicavel
        - **Banco/migracoes**: nao aplicavel
        - **Observabilidade**: audit log e relatorio base de fase
        - **Autorizacao/autenticacao**: nao aplicavel
        - **Rollout**: uso local do scaffold gerado

        ## 10. Riscos Globais

        - **Risco de produto**: baixo, porque o objetivo e estrutural
        - **Risco tecnico**: drift entre nome do arquivo, doc_id e caminhos
        - **Risco operacional**: wrappers ainda exigirem ajustes manuais se a geracao falhar
        - **Risco de dados**: nenhum
        - **Risco de adocao**: o PM ainda pode preferir um bootstrap sem defaults

        ## 11. Nao-Objetivos

        - nao definir features de negocio reais
        - nao implementar codigo de aplicacao
        - nao executar deploy

        ## 12. Features do Projeto

        ### Feature 1: Fundacao do projeto

        #### Objetivo de Negocio

        Entregar um scaffold canônico do projeto que reduza o arranque manual e deixe os artefatos de base prontos para uso.

        #### Comportamento Esperado

        O PM cria um projeto novo, abre os wrappers locais e segue o fluxo sem preencher manualmente os cabecalhos principais.

        #### Criterios de Aceite

        {feature_criteria}

        #### Dependencias com Outras Features

        - nenhuma

        #### Riscos Especificos

        - drift de nomes e caminhos se a geracao nao for testada

        #### Fases de Implementacao

        1. Modelagem e scaffold: gerar docs e metadados.
        2. Wrappers de sessao: preencher caminhos e defaults.
        3. Issue bootstrap: criar issue granularizada e task.
        4. Testes: validar tree, nomes e doc_ids.

        #### Impacts

        { _table(["Camada", "Impacto", "Detalhamento"], [
            ["Banco", "nao aplicavel", "nenhuma migracao"],
            ["Backend", "scripts/criar_projeto.py", "gerador local do scaffold"],
            ["Frontend", "nao aplicavel", "nenhum impacto"],
            ["Testes", "tests/test_criar_projeto.py", "cobertura do scaffold e dos wrappers"],
        ])}

        #### Tasks da Feature

        {feature_table}

        ## 13. Estrutura de Fases

        ## Fase 1: {BOOTSTRAP_PHASE_DIR}

        - **Objetivo**: consolidar o scaffold inicial do projeto.
        - **Features incluídas**: Feature 1
        - **Gate de saída**: o projeto novo esta pronto para planejamento e execucao sem drift documental.
        - **Critérios de aceite**:
          - intake, PRD, audit log e wrappers locais existem
          - a fase bootstrap possui epico, issue e task
          - os caminhos sao repo-relative

        ### Épicos da Fase 1

        {phase_table}

        ## 14. Epicos

        ### Épico: {BOOTSTRAP_EPIC_LABEL}

        - **ID**: {BOOTSTRAP_EPIC_ID}
        - **Fase**: {BOOTSTRAP_PHASE_ID}
        - **Feature de Origem**: Feature 1
        - **Objetivo**: entregar o scaffold inicial e validar os artefatos de base.
        - **Resultado de Negócio Mensurável**: o projeto pode iniciar planejamento e execucao sem preenchimento manual dos cabecalhos principais.
        - **Contexto Arquitetural**: raiz do projeto pronta para fases futuras; wrappers locais apontando para caminhos repo-relative.
        - **Definition of Done**:
          - [ ] intake e PRD existem com frontmatter preenchido
          - [ ] wrappers de sessao estao completos
          - [ ] fase F1, epico, issue e task existem
          - [ ] audit log aponta para o bootstrap inicial

        ### Issues do Epico

        {issue_table}

        ## 15. Dependencias Externas

        {dependency_table}

        ## 16. Rollout e Comunicacao

        - **Estratégia de deploy**: uso local do scaffold gerado
        - **Comunicação de mudanças**: o PM recebe os wrappers prontos e os caminhos canônicos
        - **Treinamento necessário**: nenhum
        - **Suporte pós-launch**: ajuste do scaffold caso o projeto real exija novas fases

        ## 17. Revisões e Auditorias

        - **Auditorias planejadas**: {BOOTSTRAP_PHASE_ID}-R01
        - **Critérios de auditoria**: aderencia ao scaffold, rastreabilidade e ausencia de drift
        - **Threshold anti-monolito**: nao aplicavel; o artefato e documental

        ## 18. Checklist de Prontidão

        - [x] Intake referenciado e versao confirmada
        - [x] Features definidas com criterios de aceite verificaveis
        - [x] Cada feature com impacts por camada preenchidos
        - [x] Rastreabilidade explicita `Feature -> Fase -> Epico -> Issue`
        - [x] Épicos criados e vinculados a features
        - [x] Fases definidas com gates de saída
        - [x] Dependências externas mapeadas
        - [x] Riscos identificados e mitigacoes planejadas
        - [x] Rollout planejado

        ## 19. Anexos e Referências

        - [Intake]({rel(f"INTAKE-{project}.md")})
        - [Audit Log]({rel("AUDIT-LOG.md")})
        - [Fase]({rel(BOOTSTRAP_PHASE_DIR, f"F1_{project}_EPICS.md")})
        - [Epic]({rel(BOOTSTRAP_PHASE_DIR, BOOTSTRAP_EPIC_FILENAME)})
        - [Issue bootstrap]({rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)})
        - [Relatorio de auditoria]({rel(BOOTSTRAP_PHASE_DIR, "auditorias", BOOTSTRAP_AUDIT_REPORT)})

        > Frase Guia: "Feature organiza, Task executa, Teste valida"
        """
    ).strip() + "\n"


def _render_audit_log(context: ProjectContext) -> str:
    """Renderiza o AUDIT-LOG inicial do projeto."""
    project = context.options.nome_projeto
    phase_rel = context.rel(BOOTSTRAP_PHASE_DIR)
    report_rel = context.rel(BOOTSTRAP_PHASE_DIR, "auditorias", BOOTSTRAP_AUDIT_REPORT)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "AUDIT-LOG.md"),
            ("version", "1.4"),
            ("status", "active"),
            ("owner", "PM"),
            ("last_updated", context.today),
        ])}

        # AUDIT-LOG - {project}

        ## Politica

        - toda auditoria formal deve gerar relatorio versionado por fase em `auditorias/`
        - toda rodada deve registrar commit base, veredito e categoria dos achados materiais
        - auditoria `hold` abre follow-ups rastreaveis
        - follow-up pode ter destino `issue-local`, `new-intake` ou `cancelled`
        - auditoria `go` e pre-requisito para mover fase a `feito/`
        - cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

        ## Gate Atual por Fase

        | Fase | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
        |---|---|---|---|---|
        | {BOOTSTRAP_PHASE_DIR} | not_ready | nao_aplicavel | [{BOOTSTRAP_AUDIT_REPORT}]({report_rel}) | scaffold inicial gerado |

        ## Resolucoes de Follow-ups

        | Data | Audit ID de Origem | Fase | Follow-up | Destino Final | Resumo | Ref | Observacoes |
        |---|---|---|---|---|---|---|---|
        | nenhum | - | - | - | - | - | - | - |

        ## Rodadas

        | Audit ID | Fase | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
        |---|---|---|---|---|---|---|---|---|---|---|---|---|
        | nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
        """
    ).strip() + "\n"


def _render_phase_manifest(context: ProjectContext) -> str:
    """Renderiza o manifesto da fase F1."""
    project = context.options.nome_projeto
    issue_rel = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    epic_rel = context.rel(BOOTSTRAP_PHASE_DIR, BOOTSTRAP_EPIC_FILENAME)
    report_rel = context.rel(BOOTSTRAP_PHASE_DIR, "auditorias", BOOTSTRAP_AUDIT_REPORT)
    log_rel = context.rel("AUDIT-LOG.md")
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", f"F1_{project}_EPICS.md"),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("audit_gate", "not_ready"),
        ])}

        # Epicos - {project} / F1 - {BOOTSTRAP_PHASE_LABEL}

        ## Objetivo da Fase

        Consolidar o scaffold inicial do projeto com intake, PRD, wrappers de sessao e primeiro issue-first bootstrap.

        ## Gate de Saida da Fase

        O projeto tem intake, PRD, wrappers locais preenchidos, fase F1, epico F1-01, issue granularizada com task e artefatos de auditoria prontos para uso.

        ## Estado do Gate de Auditoria

        - gate_atual: `not_ready`
        - ultima_auditoria: `nao_aplicavel`
        - veredito_atual: `nao_aplicavel`
        - relatorio_mais_recente: `{report_rel}`
        - log_do_projeto: [{log_rel}]({log_rel})

        ## Checklist de Transicao de Gate

        > A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

        ### `not_ready -> pending`
        - [ ] todos os epicos estao `done`
        - [ ] todas as issues filhas estao `done`
        - [ ] DoD da fase foi revisado

        ### `pending -> hold`
        - [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
        - [ ] `AUDIT-LOG.md` foi atualizado
        - [ ] o veredito da auditoria e `hold`
        - [ ] o estado do gate foi atualizado para `hold`

        ### `pending -> approved`
        - [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
        - [ ] `AUDIT-LOG.md` foi atualizado
        - [ ] o veredito da auditoria e `go`
        - [ ] o estado do gate foi atualizado para `approved`

        ## Epicos

        | ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
        |---|---|---|---|---|---|---|
        | {BOOTSTRAP_EPIC_ID} | {BOOTSTRAP_EPIC_LABEL} | Entregar o scaffold inicial e validar os artefatos de base. | {BOOTSTRAP_FEATURE_ID} | nenhuma | todo | [EPIC-{BOOTSTRAP_EPIC_ID} - {BOOTSTRAP_EPIC_LABEL}](./{BOOTSTRAP_EPIC_FILENAME}) |

        ## Dependencias entre Epicos

        - `{BOOTSTRAP_EPIC_ID}`: nenhuma

        ## Escopo desta Fase

        ### Dentro
        - intake e PRD prefillados
        - wrappers locais
        - bootstrap F1 com issue granularizada

        ### Fora
        - features de negocio reais
        - implementacao de codigo de produto
        - deploy ou integracoes externas

        ## Definition of Done da Fase
        - [ ] intake e PRD existem com frontmatter preenchido
        - [ ] wrappers de sessao estao completos
        - [ ] fase F1, epico, issue e task existem
        - [ ] audit log aponta para o bootstrap inicial
        - [ ] relatorio base de auditoria existe em `auditorias/`
        """
    ).strip() + "\n"


def _render_epic_manifest(context: ProjectContext) -> str:
    """Renderiza o manifesto do epico inicial."""
    project = context.options.nome_projeto
    issue_rel = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    phase_rel = context.rel(BOOTSTRAP_PHASE_DIR, f"F1_{project}_EPICS.md")
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", BOOTSTRAP_EPIC_FILENAME),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
        ])}

        # EPIC-{BOOTSTRAP_EPIC_ID} - {BOOTSTRAP_EPIC_LABEL}

        ## Objetivo

        Estabilizar o projeto novo com docs canônicos, wrappers e um primeiro issue granularizado.

        ## Resultado de Negocio Mensuravel

        O PM consegue iniciar planejamento e execucao sem preencher manualmente os cabecalhos principais.

        ## Feature de Origem

        - **Feature**: {BOOTSTRAP_FEATURE_ID}
        - **Comportamento coberto**: scaffold inicial do projeto com intake, PRD, wrappers e bootstrap operacional.

        ## Contexto Arquitetural

        - raiz do projeto pronta para fases futuras
        - wrappers locais apontando para caminhos repo-relative
        - issue granularizada inicial para validar o bootstrap

        ## Definition of Done do Epico

        - [ ] intake e PRD existem com frontmatter preenchido
        - [ ] wrappers de sessao estao completos
        - [ ] fase F1, epico, issue e task existem
        - [ ] audit log aponta para o bootstrap inicial

        ## Issues do Epico

        | Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
        |---|---|---|---|---|---|---|
        | {BOOTSTRAP_ISSUE_DOC_ID} | {BOOTSTRAP_ISSUE_TITLE} | Validar e ajustar o bootstrap canonico do projeto. | 3 | todo | [{BOOTSTRAP_ISSUE_DOC_ID}]({issue_rel}) | {BOOTSTRAP_FEATURE_ID} |

        ## Artifact Minimo do Epico

        - `README.md` da issue bootstrap
        - `TASK-1.md`
        - `F1_{project}_EPICS.md`

        ## Dependencias

        - [Intake]({context.rel(f"INTAKE-{project}.md")})
        - [PRD]({context.rel(f"PRD-{project}.md")})
        - [Fase]({phase_rel})
        """
    ).strip() + "\n"


def _render_issue_readme(context: ProjectContext) -> str:
    """Renderiza o manifesto da issue bootstrap."""
    project = context.options.nome_projeto
    task_instruction_mode = "required"
    task_rel = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID, "TASK-1.md")
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", BOOTSTRAP_ISSUE_DOC_ID),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("task_instruction_mode", task_instruction_mode),
            ("decision_refs", []),
        ])}

        # {BOOTSTRAP_ISSUE_ID} - {BOOTSTRAP_ISSUE_TITLE}

        ## User Story

        Como PM, quero validar o scaffold inicial do projeto para que intake, PRD, sessoes e estrutura issue-first fiquem prontos sem preenchimento manual.

        ## Feature de Origem

        - **Feature**: {BOOTSTRAP_FEATURE_ID}
        - **Comportamento coberto**: scaffold inicial do projeto com documentos e wrappers preenchidos.

        ## Contexto Tecnico

        O script `scripts/criar_projeto.py` gera a raiz do projeto, os docs canônicos, os wrappers locais, a fase F1-FUNDACAO, o epic inicial, a issue granularizada e o primeiro task file.

        ## Plano TDD

        - Red: revisar a árvore gerada e identificar placeholders ou caminhos incorretos
        - Green: corrigir qualquer drift de nomes, frontmatter ou links
        - Refactor: simplificar os artefatos para manter o bootstrap enxuto e legível

        ## Criterios de Aceitacao

        - [ ] intake e PRD existem com `doc_id` e `project` preenchidos
        - [ ] wrappers locais apontam para caminhos repo-relative do projeto
        - [ ] fase F1, epic e issue bootstrap existem
        - [ ] `SESSION-PLANEJAR-PROJETO.md` traz `escopo`, `profundidade`, `task_mode` e `observacoes` preenchidos
        - [ ] issue bootstrap possui `TASK-1.md` completa

        ## Definition of Done da Issue

        - [ ] intake e PRD existem com `doc_id` e `project` preenchidos
        - [ ] wrappers locais apontam para caminhos repo-relative do projeto
        - [ ] fase F1, epic e issue bootstrap existem
        - [ ] `SESSION-PLANEJAR-PROJETO.md` traz `escopo`, `profundidade`, `task_mode` e `observacoes` preenchidos
        - [ ] issue bootstrap possui `TASK-1.md` completa

        ## Tasks

        - [T1 - Validar o scaffold inicial](./TASK-1.md)

        ## Arquivos Reais Envolvidos

        - `INTAKE-{project}.md`
        - `PRD-{project}.md`
        - `SESSION-PLANEJAR-PROJETO.md`
        - `SESSION-CRIAR-INTAKE.md`
        - `SESSION-CRIAR-PRD.md`
        - `SESSION-IMPLEMENTAR-ISSUE.md`
        - `SESSION-REVISAR-ISSUE.md`
        - `SESSION-AUDITAR-FASE.md`
        - `SESSION-REMEDIAR-HOLD.md`
        - `SESSION-REFATORAR-MONOLITO.md`
        - `F1-FUNDACAO/...`

        ## Artifact Minimo

        - `README.md`
        - `TASK-1.md`

        ## Dependencias

        - [Epic]({context.rel(BOOTSTRAP_PHASE_DIR, BOOTSTRAP_EPIC_FILENAME)})
        - [Fase]({context.rel(BOOTSTRAP_PHASE_DIR, f"F1_{project}_EPICS.md")})
        - [PRD]({context.rel(f"PRD-{project}.md")})

        ## Navegacao Rapida

        - [TASK-1]({task_rel})
        """
    ).strip() + "\n"


def _render_task(context: ProjectContext) -> str:
    """Renderiza a task bootstrap."""
    project = context.options.nome_projeto
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "TASK-1.md"),
            ("issue_id", BOOTSTRAP_ISSUE_DOC_ID),
            ("task_id", BOOTSTRAP_TASK_ID),
            ("version", "1.1"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("tdd_aplicavel", False),
        ])}

        # T1 - Validar o scaffold inicial

        ## objetivo

        Conferir se o scaffold gerado pelo script esta completo e sem drift de nomes ou caminhos.

        ## precondicoes

        - projeto novo gerado
        - intake, PRD, wrappers e bootstrap F1 presentes

        ## arquivos_a_ler_ou_tocar

        - `PROJETOS/{project}/INTAKE-{project}.md`
        - `PROJETOS/{project}/PRD-{project}.md`
        - `PROJETOS/{project}/SESSION-PLANEJAR-PROJETO.md`
        - `PROJETOS/{project}/F1-FUNDACAO/F1_{project}_EPICS.md`
        - `PROJETOS/{project}/F1-FUNDACAO/issues/{BOOTSTRAP_ISSUE_DOC_ID}/README.md`
        - `PROJETOS/{project}/F1-FUNDACAO/issues/{BOOTSTRAP_ISSUE_DOC_ID}/TASK-1.md`

        ## passos_atomicos

        1. revisar a arvore do projeto
        2. validar os cabecalhos preenchidos
        3. confirmar links e caminhos dos wrappers
        4. corrigir placeholders residuais se houver
        5. confirmar que a fase F1 e o bootstrap inicial existem

        ## comandos_permitidos

        - `find PROJETOS/{project} -maxdepth 3 -type f | sort`
        - `rg -n "SESSION-PLANEJAR-PROJETO|INTAKE-{project}|PRD-{project}" PROJETOS/{project}`
        - `git status --short`

        ## resultado_esperado

        Scaffold inicial pronto para planejamento e execucao.

        ## testes_ou_validacoes_obrigatorias

        - checar que nao ha placeholders em `SESSION-PLANEJAR-PROJETO.md`
        - checar que o bootstrap F1 existe
        - checar que os caminhos sao repo-relative

        ## stop_conditions

        - parar se algum arquivo esperado nao existir
        - parar se houver drift entre nome do arquivo e doc_id
        """
    ).strip() + "\n"


def _render_sprint(context: ProjectContext) -> str:
    """Renderiza a sprint bootstrap."""
    project = context.options.nome_projeto
    issue_rel = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", f"{BOOTSTRAP_SPRINT_ID}.md"),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
        ])}

        # {BOOTSTRAP_SPRINT_ID} - Fundacao do projeto

        ## Objetivo da Sprint

        Consolidar o bootstrap inicial e deixar a fase F1 pronta para planejamento formal.

        ## Capacidade e Foco

        - capacidade estimada: baixa
        - foco: validar o scaffold e ajustar eventual drift estrutural

        ## Issues Selecionadas

        | Issue ID | Nome | SP | Status | Feature | Documento |
        |---|---|---|---|---|---|
        | {BOOTSTRAP_ISSUE_DOC_ID} | {BOOTSTRAP_ISSUE_TITLE} | 3 | todo | {BOOTSTRAP_FEATURE_ID} | [{BOOTSTRAP_ISSUE_DOC_ID}]({issue_rel}) |

        ## Riscos

        - drift de nomes ou caminhos
        - wrappers incompletos se a geracao for interrompida

        ## Definition of Done

        - [ ] o bootstrap F1 existe
        - [ ] a issue granularizada esta linkada na sprint
        - [ ] o audit log aponta para a fase F1-FUNDACAO
        """
    ).strip() + "\n"


def _render_audit_report(context: ProjectContext) -> str:
    """Renderiza um relatorio base de auditoria para a primeira rodada."""
    project = context.options.nome_projeto
    phase_rel = context.rel(BOOTSTRAP_PHASE_DIR)
    issue_rel = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    log_rel = context.rel("AUDIT-LOG.md")
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", f"RELATORIO-AUDITORIA-{BOOTSTRAP_PHASE_ID}-{BOOTSTRAP_ROUND}.md"),
            ("version", "2.2"),
            ("status", "planned"),
            ("verdict", "hold"),
            ("scope_type", "phase"),
            ("scope_ref", BOOTSTRAP_PHASE_DIR),
            ("phase", BOOTSTRAP_PHASE_ID),
            ("reviewer_model", "nao_aplicavel"),
            ("base_commit", "HEAD"),
            ("compares_to", "none"),
            ("round", 1),
            ("supersedes", "none"),
            ("followup_destination", "issue-local"),
            ("decision_refs", []),
            ("last_updated", context.today),
        ])}

        # RELATORIO-AUDITORIA - {project} / {BOOTSTRAP_PHASE_DIR} / {BOOTSTRAP_ROUND}

        ## Resumo Executivo

        Relatorio base reservado para a primeira auditoria da fase bootstrap.

        ## Escopo Auditado e Evidencias

        - intake: [INTAKE-{project}.md]({context.rel(f"INTAKE-{project}.md")})
        - prd: [PRD-{project}.md]({context.rel(f"PRD-{project}.md")})
        - fase: [Fase]({phase_rel})
        - epicos: [Epic bootstrap]({context.rel(BOOTSTRAP_PHASE_DIR, BOOTSTRAP_EPIC_FILENAME)})
        - issues: [Issue bootstrap]({issue_rel})
        - testes: `tests/test_criar_projeto.py`
        - diff/commit: nao aplicavel ainda

        ## Conformidades

        - scaffold inicial presente
        - wrappers locais preenchidos
        - audit log e fase inicial linkados

        ## Nao Conformidades

        - nenhuma nesta rodada base

        ## Verificacao de Decisoes Registradas

        | Decision Ref | Resultado | Evidencia | Observacoes |
        |---|---|---|---|
        | nenhum | aderente | nao aplicavel | scaffold inicial |

        ## Analise de Complexidade Estrutural

        | ID | Componente | Tipo | Linguagem | Metricas observadas | Threshold de referencia | Tendencia vs rodada anterior | Bloqueante? | Destino sugerido |
        |---|---|---|---|---|---|---|---|---|
        | M-01 | scripts/criar_projeto.py | documentation-scaffold | python | estrutura modular e declarativa | nao aplicavel | inicial | nao | issue-local |

        ## Bugs e Riscos Antecipados

        | ID | Categoria | Severidade | Descricao | Evidencia | Correcao sugerida | Bloqueante? |
        |---|---|---|---|---|---|---|
        | A-01 | test-gap | low | primeira rodada ainda nao possui auditoria real do projeto gerado | `tests/test_criar_projeto.py` | executar auditoria real quando o projeto for usado | nao |

        ## Cobertura de Testes

        | Funcionalidade | Teste existe? | Tipo | Observacao |
        |---|---|---|---|
        | scaffold do projeto | sim | unit | cobre tree, wrappers e doc_ids |

        ## Decisao

        - veredito: hold
        - justificativa: relatorio base/planned para a primeira rodada do bootstrap
        - gate_da_fase: not_ready
        - follow_up_destino_padrao: issue-local

        ## Handoff para Novo Intake

        > Preencher apenas quando houver remediacao estrutural ou sistemica com destino `new-intake`.

        - nome_sugerido_do_intake: nao aplicavel
        - intake_kind_recomendado: nao aplicavel
        - problema_resumido: scaffold base apenas
        - evidencias: nao aplicavel
        - impacto: nao aplicavel
        - escopo_presumido: nao aplicavel

        ## Follow-ups Bloqueantes

        1. nenhum

        ## Follow-ups Nao Bloqueantes

        1. nenhum
        """
    ).strip() + "\n"


def _render_session_planner(context: ProjectContext) -> str:
    """Renderiza o wrapper local de planejamento."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-PLANEJAR-PROJETO.md",
        title="SESSION-PLANEJAR-PROJETO - Planejamento de Projeto em Sessao de Chat",
        objective="Planejar o projeto novo a partir do PRD gerado e do bootstrap inicial da fase F1-FUNDACAO.",
        canonical_ref="PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md",
        params=[
            ("PROJETO", project),
            ("PRD_PATH", context.rel(f"PRD-{project}.md")),
            ("ESCOPO", context.options.escopo),
            ("PROFUNDIDADE", context.options.profundidade),
            ("TASK_MODE", context.options.task_mode),
            ("OBSERVACOES", context.options.observacoes),
        ],
        local_note=dedent(
            f"""
            - use o PRD gerado pelo scaffold como ponto de partida
            - a fase inicial do projeto e `{BOOTSTRAP_PHASE_DIR}`
            - em caso de conflito, `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md` prevalece
            """
        ).strip(),
    )


def _render_session_create_intake(context: ProjectContext) -> str:
    """Renderiza o wrapper local de criacao de intake."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-CRIAR-INTAKE.md",
        title="SESSION-CRIAR-INTAKE - Criacao de Intake em Sessao de Chat",
        objective="Gerar ou revisar o intake inicial do projeto usando o contexto do scaffold.",
        canonical_ref="PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md",
        params=[
            ("PROJETO", project),
            ("INTAKE_KIND", "new-product"),
            ("SOURCE_MODE", "original"),
            ("ORIGEM", "scaffold inicial do projeto"),
            ("ORIGIN_AUDIT", "nao_aplicavel"),
            ("CONTEXT", "Projeto novo com scaffold canônico gerado automaticamente pelo script criar_projeto.py"),
            ("OBSERVACOES", context.options.observacoes),
        ],
        local_note="Use este wrapper quando precisar regenerar o intake ou explicar o contexto do scaffold.",
    )


def _render_session_create_prd(context: ProjectContext) -> str:
    """Renderiza o wrapper local de criacao de PRD."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-CRIAR-PRD.md",
        title="SESSION-CRIAR-PRD - Criacao de PRD em Sessao de Chat",
        objective="Gerar o PRD inicial a partir do intake do projeto e do scaffold existente.",
        canonical_ref="PROJETOS/COMUM/SESSION-CRIAR-PRD.md",
        params=[
            ("PROJETO", project),
            ("INTAKE_PATH", context.rel(f"INTAKE-{project}.md")),
            ("OBSERVACOES", context.options.observacoes),
        ],
        local_note="Use o intake gerado pelo scaffold como entrada inicial do PRD.",
    )


def _render_session_implement_issue(context: ProjectContext) -> str:
    """Renderiza o wrapper local de implementacao da issue bootstrap."""
    project = context.options.nome_projeto
    issue_path = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-IMPLEMENTAR-ISSUE.md",
        title="SESSION-IMPLEMENTAR-ISSUE - Execucao de Issue em Sessao de Chat",
        objective="Executar a issue bootstrap da fase F1-FUNDACAO e validar o scaffold inicial do projeto.",
        canonical_ref="PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md",
        params=[
            ("PROJETO", project),
            ("FASE", BOOTSTRAP_PHASE_DIR),
            ("ISSUE_ID", BOOTSTRAP_ISSUE_DOC_ID),
            ("ISSUE_PATH", issue_path),
            ("TASK_ID", BOOTSTRAP_TASK_ID),
        ],
        local_note="A primeira issue do projeto aponta para o bootstrap inicial gerado pelo scaffold.",
    )


def _render_session_review_issue(context: ProjectContext) -> str:
    """Renderiza o wrapper local de revisao pos-issue."""
    project = context.options.nome_projeto
    issue_path = context.rel(BOOTSTRAP_PHASE_DIR, "issues", BOOTSTRAP_ISSUE_DOC_ID)
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-REVISAR-ISSUE.md",
        title="SESSION-REVISAR-ISSUE - Revisao Pos-Issue em Sessao de Chat",
        objective="Revisar a issue bootstrap caso o scaffold precise de ajuste ou validacao formal.",
        canonical_ref="PROJETOS/COMUM/SESSION-REVISAR-ISSUE.md",
        params=[
            ("PROJETO", project),
            ("FASE", BOOTSTRAP_PHASE_DIR),
            ("ISSUE_ID", BOOTSTRAP_ISSUE_DOC_ID),
            ("ISSUE_PATH", issue_path),
            ("BASE_COMMIT", "HEAD"),
            ("TARGET_COMMIT", "worktree"),
            ("EVIDENCIA", "git diff HEAD..worktree"),
            ("OBSERVACOES", "revisar o scaffold inicial do projeto"),
        ],
        local_note="Use quando houver alteracoes locais no bootstrap ou uma revisao do scaffold precisar ser registrada.",
    )


def _render_session_audit_phase(context: ProjectContext) -> str:
    """Renderiza o wrapper local de auditoria da fase."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-AUDITAR-FASE.md",
        title="SESSION-AUDITAR-FASE - Auditoria de Fase em Sessao de Chat",
        objective="Auditar a fase F1-FUNDACAO quando o scaffold inicial estiver pronto para revisao.",
        canonical_ref="PROJETOS/COMUM/SESSION-AUDITAR-FASE.md",
        params=[
            ("PROJETO", project),
            ("FASE", BOOTSTRAP_PHASE_DIR),
            ("RODADA", BOOTSTRAP_ROUND),
            ("BASE_COMMIT", "HEAD"),
            ("AUDIT_LOG", context.rel("AUDIT-LOG.md")),
        ],
        local_note=f"O relatorio base da fase fica em {context.rel(BOOTSTRAP_PHASE_DIR, 'auditorias', BOOTSTRAP_AUDIT_REPORT)}.",
    )


def _render_session_remediate_hold(context: ProjectContext) -> str:
    """Renderiza o wrapper local de remediacao pos-auditoria."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-REMEDIAR-HOLD.md",
        title="SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria",
        objective="Roteiar follow-ups caso a auditoria inicial da fase bootstrap retorne hold.",
        canonical_ref="PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md",
        params=[
            ("PROJETO", project),
            ("FASE", BOOTSTRAP_PHASE_DIR),
            ("RELATORIO_PATH", context.rel(BOOTSTRAP_PHASE_DIR, "auditorias", BOOTSTRAP_AUDIT_REPORT)),
            ("AUDIT_LOG_PATH", context.rel("AUDIT-LOG.md")),
            ("OBSERVACOES", "nenhuma"),
        ],
        local_note="Use este wrapper imediatamente apos uma auditoria com veredito hold.",
    )


def _render_session_refactor_monolith(context: ProjectContext) -> str:
    """Renderiza o wrapper local de refatoracao de monolito."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-REFATORAR-MONOLITO.md",
        title="SESSION-REFATORAR-MONOLITO - Mini-Projeto de Refatoracao Estrutural",
        objective="Preparar um fluxo de remediacao estrutural caso o projeto herde um monolito ou uma area grande demais.",
        canonical_ref="PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md",
        params=[
            ("PROJETO", project),
            ("INTAKE_PATH", context.rel(f"INTAKE-{project}.md")),
            ("ARQUIVO_ALVO", "nao_aplicavel"),
            ("AUDIT_REF", "nao_aplicavel"),
        ],
        local_note="Quando houver uma remediacao estrutural real, troque os sentinelas pelos caminhos concretos.",
    )


def _render_session_map(context: ProjectContext) -> str:
    """Renderiza o mapa local de sessoes."""
    project = context.options.nome_projeto
    wrappers = [
        "SESSION-CRIAR-INTAKE.md",
        "SESSION-CRIAR-PRD.md",
        "SESSION-PLANEJAR-PROJETO.md",
        "SESSION-IMPLEMENTAR-ISSUE.md",
        "SESSION-REVISAR-ISSUE.md",
        "SESSION-AUDITAR-FASE.md",
        "SESSION-REMEDIAR-HOLD.md",
        "SESSION-REFATORAR-MONOLITO.md",
    ]
    local_wrappers = _bullet_list([f"`PROJETOS/{project}/{name}`" for name in wrappers])
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "SESSION-MAPA.md"),
            ("version", "1.0"),
            ("status", "active"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
        ])}

        # SESSION-MAPA - {project}

        > Mapa dos wrappers locais do projeto novo.
        > Use este arquivo como ponto de entrada quando operar em chat interativo
        > em vez de Cloud Agent autonomo.

        ## Mapa Canonico

        Leia e use como fonte de verdade:

        - `PROJETOS/COMUM/SESSION-MAPA.md`

        ## Wrappers Locais de {project}

        {local_wrappers}

        ## Regra Local Adicional

        - os wrappers locais apontam para os caminhos repo-relative do projeto
        - em caso de conflito, `PROJETOS/COMUM/SESSION-MAPA.md` prevalece
        """
    ).strip() + "\n"


def _render_session_wrapper(
    context: ProjectContext,
    *,
    doc_id: str,
    title: str,
    objective: str,
    canonical_ref: str,
    params: Sequence[tuple[str, str]],
    local_note: str,
) -> str:
    """Renderiza wrappers locais em um formato consistente."""
    project = context.options.nome_projeto
    param_width = max(len(label) for label, _ in params) if params else 0
    rendered_params = [
        "```text",
        *[
            f"{label}:{' ' * (param_width - len(label) + 2)}{value}"
            for label, value in params
        ],
        "```",
    ]

    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", doc_id),
            ("version", "1.0"),
            ("status", "active"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
        ])}

        # {title}

        ## Objetivo

        {objective}

        ## Sessao Canonica

        Leia e siga integralmente:

        - `{canonical_ref}`

        ## Parametros Preenchidos

        {"\n".join(rendered_params)}

        ## Regra Local Adicional

        {local_note}
        """
    ).strip() + "\n"


def _build_scaffold_items(context: ProjectContext) -> list[ScaffoldItem]:
    """Constrói a lista declarativa de itens do scaffold."""
    paths = context.paths
    return [
        ScaffoldItem(paths.feito_dir, "dir"),
        ScaffoldItem(paths.phase_dir, "dir"),
        ScaffoldItem(paths.issues_dir, "dir"),
        ScaffoldItem(paths.sprints_dir, "dir"),
        ScaffoldItem(paths.auditorias_dir, "dir"),
        ScaffoldItem(paths.intake_path, "file", _render_intake),
        ScaffoldItem(paths.prd_path, "file", _render_prd),
        ScaffoldItem(paths.audit_log_path, "file", _render_audit_log),
        ScaffoldItem(paths.session_plan_path, "file", _render_session_planner),
        ScaffoldItem(paths.session_create_intake_path, "file", _render_session_create_intake),
        ScaffoldItem(paths.session_create_prd_path, "file", _render_session_create_prd),
        ScaffoldItem(paths.session_implement_issue_path, "file", _render_session_implement_issue),
        ScaffoldItem(paths.session_review_issue_path, "file", _render_session_review_issue),
        ScaffoldItem(paths.session_audit_phase_path, "file", _render_session_audit_phase),
        ScaffoldItem(paths.session_remediate_hold_path, "file", _render_session_remediate_hold),
        ScaffoldItem(paths.session_refactor_monolith_path, "file", _render_session_refactor_monolith),
        ScaffoldItem(paths.session_map_path, "file", _render_session_map),
        ScaffoldItem(paths.phase_manifest_path, "file", _render_phase_manifest),
        ScaffoldItem(paths.epic_manifest_path, "file", _render_epic_manifest),
        ScaffoldItem(paths.issue_readme_path, "file", _render_issue_readme),
        ScaffoldItem(paths.task1_path, "file", _render_task),
        ScaffoldItem(paths.sprint_path, "file", _render_sprint),
        ScaffoldItem(paths.audit_report_path, "file", _render_audit_report),
    ]


def _create_item(context: ProjectContext, item: ScaffoldItem, *, verbose: bool) -> None:
    """Cria um unico item do scaffold."""
    if item.kind == "dir":
        _ensure_dir(item.path)
        if verbose:
            print(f"  ✓ diretorio: {item.path}")
        return

    if item.renderer is None:
        raise ValueError(f"renderer ausente para {item.path}")
    _ensure_dir(item.path.parent)
    _write_text(item.path, item.renderer(context))
    if verbose:
        print(f"  ✓ arquivo: {item.path}")


def _create_structure(context: ProjectContext, *, verbose: bool) -> list[Path]:
    """Cria a raiz do projeto e os diretorios canonicos do scaffold."""
    created_dirs = [context.paths.filesystem_root]
    _ensure_dir(context.paths.filesystem_root)
    if verbose:
        print(f"✓ Diretorio raiz criado: {context.paths.filesystem_root}")

    for item in _build_scaffold_items(context):
        if item.kind != "dir":
            continue
        _create_item(context, item, verbose=verbose)
        created_dirs.append(item.path)

    return created_dirs


def _create_files(context: ProjectContext, *, verbose: bool) -> list[Path]:
    """Cria todos os arquivos do scaffold canonico."""
    created_files: list[Path] = []
    for item in _build_scaffold_items(context):
        if item.kind != "file":
            continue
        _create_item(context, item, verbose=verbose)
        created_files.append(item.path)
    return created_files


def criar_estrutura_minima(options: ScaffoldOptions | str) -> list[Path]:
    """Cria a estrutura minima do projeto novo.

    A estrutura inclui a raiz do projeto, ``feito/`` e os diretórios da fase
    bootstrap. Esta função e pública para facilitar testes focados na árvore.
    """
    resolved = _coerce_options(options)
    context = _build_context(resolved)
    return _create_structure(context, verbose=resolved.verbose)


def criar_arquivos_base(options: ScaffoldOptions | str) -> list[Path]:
    """Cria os arquivos base e os wrappers do projeto novo.

    A função é pública para permitir testes isolados da renderização dos
    artefatos sem depender da orquestração completa da CLI.
    """
    resolved = _coerce_options(options)
    context = _build_context(resolved)
    return _create_files(context, verbose=resolved.verbose)


def criar_projeto(options: ScaffoldOptions | str) -> list[Path]:
    """Cria um novo projeto com o scaffold canonico preenchido."""
    resolved = _coerce_options(options)
    context = _build_context(resolved)
    if context.paths.filesystem_root.exists():
        raise FileExistsError(
            f"Projeto '{resolved.nome_projeto}' ja existe em {context.paths.filesystem_root}"
        )

    _create_structure(context, verbose=resolved.verbose)
    created_files = _create_files(context, verbose=resolved.verbose)

    print("\n" + "=" * 60)
    print(f"PROJETO CRIADO: {resolved.nome_projeto}")
    print("=" * 60)
    print(f"Localizacao: {context.paths.filesystem_root}")
    print(f"Arquivos criados: {len(created_files)}")
    print(f"\nProximo passo: preencha {context.paths.intake_path.name} e {context.paths.prd_path.name}")

    return created_files


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a interface de linha de comando."""
    try:
        parsed = parse_args(argv)
        criar_projeto(parsed)
        return 0
    except (ValueError, FileExistsError) as exc:
        print(f"Erro: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - defesa final da CLI
        print(f"Erro inesperado: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
