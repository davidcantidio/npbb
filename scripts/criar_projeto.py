#!/usr/bin/env python3
"""Cria um novo projeto em ``PROJETOS/`` com scaffold canonico preenchido."""

from __future__ import annotations

import argparse
import os
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

BOOTSTRAP_FEATURE_DIR = "FEATURE-1-FOUNDATION"
BOOTSTRAP_FEATURE_ID = BOOTSTRAP_FEATURE_DIR
BOOTSTRAP_FEATURE_CODE = "FEATURE-1"
BOOTSTRAP_FEATURE_LABEL = "Foundation"
BOOTSTRAP_FEATURE_MANIFEST = "FEATURE-1.md"
BOOTSTRAP_US_ID = "US-1-01"
BOOTSTRAP_US_PRD_ID = "US-1.1"
BOOTSTRAP_US_SLUG = "BOOTSTRAP"
BOOTSTRAP_US_DIR = f"{BOOTSTRAP_US_ID}-{BOOTSTRAP_US_SLUG}"
BOOTSTRAP_US_DOC_ID = BOOTSTRAP_US_DIR
BOOTSTRAP_US_TITLE = "Bootstrap do projeto"
BOOTSTRAP_TASK_ID = "T1"
BOOTSTRAP_ROUND = "R01"
BOOTSTRAP_AUDIT_REPORT = f"RELATORIO-AUDITORIA-F1-{BOOTSTRAP_ROUND}.md"


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
    features_dir: Path
    feature_dir: Path
    user_stories_dir: Path
    user_story_dir: Path
    auditorias_dir: Path
    encerramento_dir: Path
    intake_path: Path
    prd_path: Path
    audit_log_path: Path
    feature_manifest_path: Path
    user_story_readme_path: Path
    task1_path: Path
    audit_report_path: Path
    closing_report_path: Path
    session_plan_path: Path
    session_create_intake_path: Path
    session_create_prd_path: Path
    session_implement_us_path: Path
    session_implement_task_path: Path
    session_review_us_path: Path
    session_audit_feature_path: Path
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

    def md_href(self, writer: Path, target: Path) -> str:
        """Caminho relativo de ``writer`` a ``target``, valido como href Markdown."""
        return Path(os.path.relpath(target, writer.parent)).as_posix()


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
        choices=[
            "projeto completo",
            "apenas FEATURE-<N>-<NOME>",
            "apenas US-<N>-<NN>-<NOME>",
            "encerramento",
        ],
        help="Escopo predefinido para SESSION-PLANEJAR-PROJETO",
    )
    parser.add_argument(
        "--profundidade",
        default=DEFAULT_PROFUNDIDADE,
        choices=["features", "features+user_stories", "completo", "encerramento"],
        help="Profundidade predefinida para SESSION-PLANEJAR-PROJETO",
    )
    parser.add_argument(
        "--task-mode",
        default=DEFAULT_TASK_MODE,
        choices=["optional", "required", "por user story"],
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
    features_dir = filesystem_root / "features"
    feature_dir = features_dir / BOOTSTRAP_FEATURE_DIR
    user_stories_dir = feature_dir / "user-stories"
    user_story_dir = user_stories_dir / BOOTSTRAP_US_DIR
    auditorias_dir = feature_dir / "auditorias"
    encerramento_dir = filesystem_root / "encerramento"

    return ProjectPaths(
        filesystem_root=filesystem_root,
        project_ref=project_ref,
        features_dir=features_dir,
        feature_dir=feature_dir,
        user_stories_dir=user_stories_dir,
        user_story_dir=user_story_dir,
        auditorias_dir=auditorias_dir,
        encerramento_dir=encerramento_dir,
        intake_path=filesystem_root / f"INTAKE-{options.nome_projeto}.md",
        prd_path=filesystem_root / f"PRD-{options.nome_projeto}.md",
        audit_log_path=filesystem_root / "AUDIT-LOG.md",
        feature_manifest_path=feature_dir / BOOTSTRAP_FEATURE_MANIFEST,
        user_story_readme_path=user_story_dir / "README.md",
        task1_path=user_story_dir / "TASK-1.md",
        audit_report_path=auditorias_dir / BOOTSTRAP_AUDIT_REPORT,
        closing_report_path=encerramento_dir / "RELATORIO-ENCERRAMENTO.md",
        session_plan_path=filesystem_root / "SESSION-PLANEJAR-PROJETO.md",
        session_create_intake_path=filesystem_root / "SESSION-CRIAR-INTAKE.md",
        session_create_prd_path=filesystem_root / "SESSION-CRIAR-PRD.md",
        session_implement_us_path=filesystem_root / "SESSION-IMPLEMENTAR-US.md",
        session_implement_task_path=filesystem_root / "SESSION-IMPLEMENTAR-TASK.md",
        session_review_us_path=filesystem_root / "SESSION-REVISAR-US.md",
        session_audit_feature_path=filesystem_root / "SESSION-AUDITAR-FEATURE.md",
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
        > bootstrap de feature sejam criados sem preenchimento manual repetitivo.

        ## 0. Rastreabilidade de Origem

        - projeto de origem: nao_aplicavel
        - unidade de origem: nao_aplicavel
        - auditoria de origem: nao_aplicavel
        - relatorio de origem: nao_aplicavel
        - motivo da abertura deste intake: gerar um projeto novo com scaffold canônico e wrappers prontos para uso

        ## 1. Resumo Executivo

        - nome curto da iniciativa: scaffold canônico do projeto
        - tese em 1 frase: criar um projeto pronto para planejamento e execucao sem preencher manualmente os cabecalhos principais
        - valor esperado em 3 linhas:
          - intake, PRD, audit log e wrappers locais prontos
          - feature bootstrap, user story bootstrap e task inicial geradas
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
        3. Criar `features/FEATURE-1-FOUNDATION` com user story bootstrap e task inicial.
        4. Deixar o projeto pronto para planejamento, implementacao e auditoria.

        ## 6. Escopo Inicial

        ### Dentro

        - scaffold inicial do projeto
        - wrappers de sessao prontos para uso
        - feature bootstrap com user story granularizada

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
        - observabilidade: audit log e relatorio base de feature
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
        - evidencia tecnica: o gerador precisa criar wrappers, feature bootstrap e artefatos base
        - componente(s) afetado(s): `scripts/criar_projeto.py`, `PROJETOS/COMUM` e os novos arquivos do projeto
        - riscos de nao agir: cada novo projeto diverge do padrao e aumenta retrabalho

        ## 14. Lacunas Conhecidas

        - nenhuma no nivel de scaffold
        """
    ).strip() + "\n"


def _render_prd(context: ProjectContext) -> str:
    """Renderiza o PRD inicial do projeto."""
    project = context.options.nome_projeto
    p = context.paths
    prd_w = p.prd_path
    href_intake = context.md_href(prd_w, p.intake_path)
    href_audit_log = context.md_href(prd_w, p.audit_log_path)
    href_feature = context.md_href(prd_w, p.feature_manifest_path)
    href_user_story = context.md_href(prd_w, p.user_story_readme_path)
    href_report = context.md_href(prd_w, p.audit_report_path)
    href_closing = context.md_href(prd_w, p.closing_report_path)

    dependency_table = _table(
        ["Dependencia", "Tipo", "Origem", "Impacto", "Status"],
        [
            [
                "PROJETOS/COMUM",
                "docs-governance",
                "framework",
                "fonte canonica do scaffold",
                "active",
            ]
        ],
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

        > **STATUS: PENDENTE - aguardando conclusao do Intake**
        >
        > Este arquivo nasce como scaffold inicial. Antes de planejar features reais
        > do projeto, ele deve ser reescrito a partir do intake concreto.

        # PRD - {project}

        > Origem: [INTAKE-{project}.md]({href_intake})
        >
        > Este PRD descreve o scaffold canonico do projeto, nao um produto de negocio
        > final. A intencao e deixar o projeto pronto para intake -> PRD -> decomposicao
        > sem confundir o placeholder inicial com backlog real.

        ## 0. Rastreabilidade

        - **Intake de origem**: [INTAKE-{project}.md]({href_intake})
        - **Versao do intake**: 1.0
        - **Data de criacao**: {context.today}
        - **PRD derivado**: nao aplicavel

        ## 1. Resumo Executivo

        - **Nome do projeto**: {project}
        - **Tese em 1 frase**: criar um projeto pronto para planejamento e execucao sem preenchimento manual dos cabecalhos principais
        - **Valor esperado em 3 linhas**:
          - intake, PRD, audit log e wrappers locais prontos
          - feature bootstrap, user story bootstrap e task inicial geradas
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
        - feature bootstrap com user story granularizada

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

        > Visao unificada de impacto arquitetural em nivel de projeto. O detalhamento
        > por entregavel acontece apos este PRD, na etapa `PRD -> Features`.

        - **Backend**: nao aplicavel
        - **Frontend**: nao aplicavel
        - **Banco/migracoes**: nao aplicavel
        - **Observabilidade**: audit log e relatorio base de feature
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

        > **Pos-PRD (nao faz parte deste arquivo):** backlog estruturado de features,
        > user stories e tasks segue `GOV-FEATURE.md`, `GOV-USER-STORY.md`,
        > `GOV-SCRUM.md` e as sessoes `SESSION-DECOMPOR-*`.

        ## 12. Dependencias Externas

        {dependency_table}

        ## 13. Rollout e Comunicacao

        - **Estratégia de deploy**: uso local do scaffold gerado
        - **Comunicacao de mudancas**: o PM recebe os wrappers prontos, o PRD placeholder e a indicacao explicita da proxima etapa `PRD -> Features`
        - **Treinamento necessário**: nenhum
        - **Suporte pos-launch**: ajuste do scaffold caso o projeto real exija novas features

        ## 14. Revisoes e Auditorias

        - **Gates e auditorias em nivel de projeto**: preencher apos intake e PRD concretos; o bootstrap existe apenas para evitar drift inicial
        - **Critérios de auditoria**: aderencia ao scaffold, rastreabilidade e ausencia de drift
        - **Threshold anti-monolito**: nao aplicavel; o artefato e documental

        ## 15. Checklist de Prontidao

        - [ ] Intake referenciado e versao confirmada
        - [ ] Problema, escopo, restricoes, riscos e metricas preenchidos de forma verificavel
        - [ ] Arquitetura geral e rollout descritos sem catalogo de features nem tabelas de user stories neste PRD
        - [ ] Dependencias externas mapeadas
        - [ ] Proxima etapa explicita: `PRD -> Features` via `SESSION-DECOMPOR-PRD-EM-FEATURES.md` / `PROMPT-PRD-PARA-FEATURES.md`

        ## 16. Anexos e Referencias

        - [Intake]({href_intake})
        - [Audit Log]({href_audit_log})
        - [Feature bootstrap]({href_feature})
        - [User Story bootstrap]({href_user_story})
        - [Relatorio de auditoria]({href_report})
        - [Relatorio de encerramento]({href_closing})

        > Frase Guia: "PRD direciona, Feature organiza, User Story fatia, Task executa, Teste valida"
        """
    ).strip() + "\n"


def _render_audit_log(context: ProjectContext) -> str:
    """Renderiza o AUDIT-LOG inicial do projeto."""
    project = context.options.nome_projeto
    audit_w = context.paths.audit_log_path
    report_href = context.md_href(audit_w, context.paths.audit_report_path)
    feature_href = context.md_href(audit_w, context.paths.feature_manifest_path)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "AUDIT-LOG.md"),
            ("version", "2.0"),
            ("status", "active"),
            ("owner", "PM"),
            ("last_updated", context.today),
        ])}

        # AUDIT-LOG - {project}

        ## Politica

        - toda auditoria formal deve gerar relatorio versionado por feature em `features/FEATURE-*/auditorias/`
        - toda rodada deve registrar commit base, veredito e categoria dos achados materiais
        - auditoria `hold` abre follow-ups rastreaveis
        - follow-up pode ter destino `same-feature`, `new-intake` ou `cancelled`
        - auditoria `go` e pre-requisito para encerrar a feature
        - cada resolucao de follow-up deve registrar o `Audit ID de Origem` da rodada `hold` que gerou o item

        ## Gate Atual por Feature

        | Feature | Estado do Gate | Ultima Auditoria | Relatorio Mais Recente | Observacoes |
        |---|---|---|---|---|
        | [{BOOTSTRAP_FEATURE_ID}]({feature_href}) | not_ready | nao_aplicavel | [{BOOTSTRAP_AUDIT_REPORT}]({report_href}) | O ficheiro em `auditorias/` e um shell com `status: planned`; nao ha veredito canonico ate haver auditoria real concluida e registo coerente neste log. Scaffold inicial gerado. |

        ## Resolucoes de Follow-ups

        | Data | Audit ID de Origem | Feature | Follow-up | Destino Final | Resumo | Ref | Observacoes |
        |---|---|---|---|---|---|---|---|
        | nenhum | - | - | - | - | - | - | - |

        ## Rodadas

        | Audit ID | Feature | Data | Reviewer/Model | Base Commit | Commit Anterior Auditado | Verdict | Status | Relatorio | Achados Materiais | Follow-up Destino | Follow-up Ref | Supersedes |
        |---|---|---|---|---|---|---|---|---|---|---|---|---|
        | nenhum | - | - | - | - | - | - | - | - | - | - | - | - |
        """
    ).strip() + "\n"


def _render_feature_manifest(context: ProjectContext) -> str:
    """Renderiza o manifesto da feature bootstrap."""
    p = context.paths
    feature_w = p.feature_manifest_path
    prd_href = context.md_href(feature_w, p.prd_path)
    audit_log_href = context.md_href(feature_w, p.audit_log_path)
    user_story_href = context.md_href(feature_w, p.user_story_readme_path)
    report_href = context.md_href(feature_w, p.audit_report_path)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", BOOTSTRAP_FEATURE_MANIFEST),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("audit_gate", "not_ready"),
        ])}

        # {BOOTSTRAP_FEATURE_CODE} - {BOOTSTRAP_FEATURE_LABEL}

        ## Objetivo de Negocio

        Entregar o scaffold inicial do projeto no paradigma
        `Feature -> User Story -> Task`, com wrappers locais e auditabilidade
        prontos para uso.

        ## Resultado de Negocio Mensuravel

        O PM consegue iniciar planejamento e execucao sem preencher manualmente
        os cabecalhos principais nem adaptar caminhos legados.

        ## Dependencias da Feature

        - nenhuma

        ## Estado Operacional

        - status: `todo`
        - audit_gate: `not_ready`
        - relatorio_mais_recente: [RELATORIO-AUDITORIA-F1-R01]({report_href})
        - audit_log: [AUDIT-LOG.md]({audit_log_href})

        ## Criterios de Aceite

        - [ ] intake, PRD e audit log existem com frontmatter preenchido
        - [ ] wrappers locais apontam para `SESSION-IMPLEMENTAR-US`,
              `SESSION-IMPLEMENTAR-TASK`, `SESSION-REVISAR-US` e `SESSION-AUDITAR-FEATURE`
        - [ ] `features/{BOOTSTRAP_FEATURE_DIR}/` existe com manifesto, user story
              bootstrap e `TASK-1.md`
        - [ ] nao existem `F1-*`, `issues/`, `sprints/` nem wrappers
              `SESSION-*-ISSUE/FASE` no projeto novo

        ## User Stories da Feature

        | US ID | Titulo | SP | Depende de | Status | Documento |
        |---|---|---|---|---|---|
        | {BOOTSTRAP_US_ID} | {BOOTSTRAP_US_TITLE} | 3 | nenhuma | todo | [README](./user-stories/{BOOTSTRAP_US_DIR}/README.md) |

        ## Definition of Done da Feature

        - [ ] todas as user stories estao `done` ou `cancelled`
        - [ ] auditoria da feature aprovada com veredito `go`
        - [ ] `AUDIT-LOG.md` atualizado com a rodada mais recente

        ## Dependencias

        - [PRD]({prd_href})
        - [AUDIT-LOG]({audit_log_href})
        - [User Story bootstrap]({user_story_href})
        """
    ).strip() + "\n"


def _render_user_story_readme(context: ProjectContext) -> str:
    """Renderiza o manifesto da user story bootstrap."""
    project = context.options.nome_projeto
    p = context.paths
    us_w = p.user_story_readme_path
    task_href = context.md_href(us_w, p.task1_path)
    feature_href = context.md_href(us_w, p.feature_manifest_path)
    prd_href = context.md_href(us_w, p.prd_path)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", BOOTSTRAP_US_DOC_ID),
            ("version", "1.0"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("task_instruction_mode", "required"),
            ("feature_id", BOOTSTRAP_FEATURE_ID),
            ("decision_refs", []),
        ])}

        # {BOOTSTRAP_US_ID} - {BOOTSTRAP_US_TITLE}

        ## User Story

        Como PM, quero validar o scaffold inicial do projeto para que intake,
        PRD, wrappers e estrutura `Feature -> User Story -> Task` fiquem prontos
        sem preenchimento manual repetitivo.

        ## Feature de Origem

        - **Feature**: {BOOTSTRAP_FEATURE_ID}
        - **Comportamento coberto**: scaffold inicial do projeto com documentos,
          wrappers e relatorio base de auditoria.

        ## Contexto Tecnico

        O script `scripts/criar_projeto.py` gera a raiz do projeto, os docs
        canonicos, os wrappers locais, a feature bootstrap, a user story
        bootstrap, a primeira task e o shell de auditoria da feature.

        ## Plano TDD (opcional no manifesto da US)

        - **Red**: nao aplicavel
        - **Green**: nao aplicavel
        - **Refactor**: nao aplicavel

        ## Criterios de Aceitacao (Given / When / Then)

        - **Given** um repositorio sem o projeto alvo,
          **when** o script gera o scaffold,
          **then** o projeto nasce com `features/{BOOTSTRAP_FEATURE_DIR}/`.
        - **Given** a feature bootstrap criada,
          **when** o PM abre os wrappers locais,
          **then** apenas sessoes canonicas `Feature/User Story/Task` sao
          referenciadas.
        - **Given** a user story bootstrap,
          **when** ela for inspecionada,
          **then** `TASK-1.md` estara linkada e pronta para execucao.

        ## Definition of Done da User Story

        - [ ] Todas as tasks em `TASK-*.md` estao `done` ou `cancelled` com justificativa
        - [ ] Criterios Given/When/Then verificados
        - [ ] Handoff de revisao preenchido neste documento quando o fluxo do projeto exigir revisao pos-US
        - [ ] Revisao aprovada conforme `PROJETOS/COMUM/GOV-SCRUM.md` antes de promover a US a `done`

        ## Tasks

        - [T1 - Validar o scaffold inicial](./TASK-1.md)

        ## Arquivos Reais Envolvidos

        - `INTAKE-{project}.md`
        - `PRD-{project}.md`
        - `AUDIT-LOG.md`
        - `SESSION-PLANEJAR-PROJETO.md`
        - `SESSION-IMPLEMENTAR-US.md`
        - `SESSION-IMPLEMENTAR-TASK.md`
        - `SESSION-REVISAR-US.md`
        - `SESSION-AUDITAR-FEATURE.md`
        - `features/{BOOTSTRAP_FEATURE_DIR}/FEATURE-1.md`

        ## Artefato Minimo

        - `features/{BOOTSTRAP_FEATURE_DIR}/FEATURE-1.md`
        - `features/{BOOTSTRAP_FEATURE_DIR}/user-stories/{BOOTSTRAP_US_DIR}/README.md`
        - `features/{BOOTSTRAP_FEATURE_DIR}/user-stories/{BOOTSTRAP_US_DIR}/TASK-1.md`

        ## Handoff para Revisao Pos-User Story

        status: nao_iniciado
        base_commit: nao_informado
        target_commit: nao_informado
        evidencia: nao_informado
        commits_execucao: []
        validacoes_executadas: []
        arquivos_de_codigo_relevantes: []
        limitacoes: []

        ## Dependencias

        - [Feature bootstrap]({feature_href})
        - [PRD do projeto]({prd_href})
        - Outras USs: nenhuma
        - [GOV-USER-STORY.md](../../../../COMUM/GOV-USER-STORY.md)

        ## Navegacao Rapida

        - [TASK-1]({task_href})
        """
    ).strip() + "\n"


def _render_task(context: ProjectContext) -> str:
    """Renderiza a task bootstrap."""
    project = context.options.nome_projeto
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "TASK-1.md"),
            ("us_id", BOOTSTRAP_US_DOC_ID),
            ("task_id", BOOTSTRAP_TASK_ID),
            ("version", "1.1"),
            ("status", "todo"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("tdd_aplicavel", False),
        ])}

        # T1 - Validar o scaffold inicial

        ## objetivo

        Conferir se o scaffold gerado pelo script esta completo e sem drift de
        nomes, wrappers ou caminhos.

        ## precondicoes

        - projeto novo gerado
        - intake, PRD, wrappers e feature bootstrap presentes

        ## arquivos_a_ler_ou_tocar

        - `PROJETOS/{project}/INTAKE-{project}.md`
        - `PROJETOS/{project}/PRD-{project}.md`
        - `PROJETOS/{project}/SESSION-PLANEJAR-PROJETO.md`
        - `PROJETOS/{project}/SESSION-IMPLEMENTAR-US.md`
        - `PROJETOS/{project}/SESSION-IMPLEMENTAR-TASK.md`
        - `PROJETOS/{project}/SESSION-REVISAR-US.md`
        - `PROJETOS/{project}/SESSION-AUDITAR-FEATURE.md`
        - `PROJETOS/{project}/features/{BOOTSTRAP_FEATURE_DIR}/FEATURE-1.md`
        - `PROJETOS/{project}/features/{BOOTSTRAP_FEATURE_DIR}/user-stories/{BOOTSTRAP_US_DIR}/README.md`
        - `PROJETOS/{project}/features/{BOOTSTRAP_FEATURE_DIR}/user-stories/{BOOTSTRAP_US_DIR}/TASK-1.md`

        ## passos_atomicos

        1. revisar a arvore do projeto
        2. validar os cabecalhos preenchidos
        3. confirmar links e caminhos dos wrappers
        4. confirmar a ausencia de `F1-*`, `issues/` e `sprints/`
        5. corrigir placeholders residuais se houver

        ## comandos_permitidos

        - `find PROJETOS/{project} -maxdepth 5 -type f | sort`
        - `rg -n "SESSION-PLANEJAR-PROJETO|SESSION-IMPLEMENTAR-US|SESSION-IMPLEMENTAR-TASK|FEATURE-1|US-1-01" PROJETOS/{project}`
        - `git status --short`

        ## resultado_esperado

        Scaffold inicial pronto para planejamento e execucao no paradigma
        `Feature -> User Story -> Task`.

        ## testes_ou_validacoes_obrigatorias

        - checar que nao ha placeholders residuais em `SESSION-PLANEJAR-PROJETO.md`
        - checar que a feature bootstrap existe
        - checar que os caminhos sao repo-relative

        ## stop_conditions

        - parar se algum arquivo esperado nao existir
        - parar se houver drift entre nome do arquivo e doc_id
        """
    ).strip() + "\n"


def _render_feature_audit_report(context: ProjectContext) -> str:
    """Renderiza um relatorio base de auditoria para a primeira rodada da feature."""
    project = context.options.nome_projeto
    p = context.paths
    report_w = p.audit_report_path
    href_intake = context.md_href(report_w, p.intake_path)
    href_prd = context.md_href(report_w, p.prd_path)
    href_feature = context.md_href(report_w, p.feature_manifest_path)
    href_us = context.md_href(report_w, p.user_story_readme_path)
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", BOOTSTRAP_AUDIT_REPORT[:-3]),
            ("version", "1.0"),
            ("status", "planned"),
            ("scope_type", "feature"),
            ("scope_ref", BOOTSTRAP_FEATURE_ID),
            ("feature_id", BOOTSTRAP_FEATURE_ID),
            ("reviewer_model", "nao_aplicavel"),
            ("base_commit", "HEAD"),
            ("compares_to", "none"),
            ("round", 1),
            ("supersedes", "none"),
            ("followup_destination", "same-feature"),
            ("decision_refs", []),
            ("last_updated", context.today),
        ])}

        # RELATORIO-AUDITORIA - {project} / {BOOTSTRAP_FEATURE_ID} / {BOOTSTRAP_ROUND}

        ## Resumo Executivo

        Este ficheiro e um shell para a primeira rodada de auditoria da feature.
        Com `status: planned`, a rodada nao foi executada; o `AUDIT-LOG.md`
        permanece sem veredito material ate haver auditoria real.

        ## Escopo Auditado e Evidencias

        - intake: [INTAKE-{project}.md]({href_intake})
        - prd: [PRD-{project}.md]({href_prd})
        - feature: [Feature bootstrap]({href_feature})
        - user stories: [US bootstrap]({href_us})
        - testes: `tests/test_criar_projeto.py`
        - diff/commit: nao aplicavel ainda

        ## Conformidades

        - nao aplicavel enquanto `planned`

        ## Nao Conformidades

        - nao aplicavel enquanto `planned`

        ## Cobertura de Testes

        | Funcionalidade | Teste existe? | Tipo | Observacao |
        |---|---|---|---|
        | scaffold do projeto | sim | unit | cobre arvore, wrappers e ausencia de legados no bootstrap |

        ## Decisao

        - estado do artefato: `planned`
        - veredito canonico (`go` / `hold` / `cancelled`): nao aplicavel ate conclusao da rodada
        - gate_da_feature: `not_ready`
        - follow-up padrao: `same-feature`

        ## Follow-ups Bloqueantes

        1. nao aplicavel ao shell `planned`

        ## Follow-ups Nao Bloqueantes

        1. nao aplicavel ao shell `planned`
        """
    ).strip() + "\n"


def _render_closing_report(context: ProjectContext) -> str:
    """Renderiza o relatorio de encerramento placeholder."""
    project = context.options.nome_projeto
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "RELATORIO-ENCERRAMENTO.md"),
            ("version", "1.0"),
            ("status", "draft"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
        ])}

        # RELATORIO-ENCERRAMENTO - {project}

        ## Estado Atual

        Projeto em bootstrap inicial. Este relatorio existe apenas para manter
        a arvore canonica completa do projeto.

        ## Pre-condicoes para preenchimento

        - todas as features do projeto encerradas
        - auditorias finais aprovadas
        - `AUDIT-LOG.md` coerente com o estado final
        """
    ).strip() + "\n"


def _render_session_planner(context: ProjectContext) -> str:
    """Renderiza o wrapper local de planejamento."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-PLANEJAR-PROJETO.md",
        title="SESSION-PLANEJAR-PROJETO - Planejamento de Projeto em Sessao de Chat",
        objective="Planejar o projeto novo a partir do PRD gerado e do bootstrap inicial em `features/`.",
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
            - a feature bootstrap inicial do projeto e `{BOOTSTRAP_FEATURE_ID}`
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


def _render_session_implement_us(context: ProjectContext) -> str:
    """Renderiza o wrapper local de execucao de user story."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-IMPLEMENTAR-US.md",
        title="SESSION-IMPLEMENTAR-US - Execucao de User Story em Sessao de Chat",
        objective="Executar a user story atualmente elegivel do projeto, resolvida a partir da fila documental vigente.",
        canonical_ref="PROJETOS/COMUM/SESSION-IMPLEMENTAR-US.md",
        params=[
            ("PROJETO", project),
            ("FEATURE_ID", "<resolver_na_feature_ativa_do_projeto>"),
            ("US_ID", "<resolver_na_user_story_elegivel_do_projeto>"),
            ("US_PATH", "<resolver_na_user_story_elegivel_do_projeto>"),
            ("TASK_ID", "auto"),
            ("ROUND", "1"),
        ],
        local_note=dedent(
            """
            - use `boot-prompt.md` nos niveis de descoberta para resolver a unidade elegivel antes de colar os parametros
            - nao trate este wrapper como congelado na bootstrap; a fila atual do projeto prevalece
            - se o projeto ainda estiver apenas no scaffold inicial, a US bootstrap continua sendo a primeira candidata natural
            """
        ).strip(),
    )


def _render_session_implement_task(context: ProjectContext) -> str:
    """Renderiza o wrapper local de execucao com entrada na task."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-IMPLEMENTAR-TASK.md",
        title="SESSION-IMPLEMENTAR-TASK - Execucao com entrada na Task",
        objective=(
            "Executar uma task concreta (`TASK-*.md`) com leitura ascendente ate "
            "PRD/Intake e delegacao ao fluxo operacional de user story."
        ),
        canonical_ref="PROJETOS/COMUM/SESSION-IMPLEMENTAR-TASK.md",
        params=[
            ("PROJETO", project),
            (
                "TASK_PATH",
                "<caminho completo para PROJETOS/"
                f"{project}/features/.../user-stories/.../TASK-N.md>",
            ),
            ("ROUND", "1"),
        ],
        local_note=dedent(
            """
            - prefira esta sessao quando a task alvo ja for conhecida (commit atomico, TDD por task); use `SESSION-IMPLEMENTAR-US.md` com `TASK_ID: auto` quando a fila ainda tiver de ser resolvida na US
            - nao congele caminhos da bootstrap; a fila real do projeto prevalece
            """
        ).strip(),
    )


def _render_session_review_us(context: ProjectContext) -> str:
    """Renderiza o wrapper local de revisao pos-user-story."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-REVISAR-US.md",
        title="SESSION-REVISAR-US - Revisao Pos-User Story em Sessao de Chat",
        objective="Revisar a user story atualmente em `ready_for_review` ou a user story explicitamente indicada pelo PM.",
        canonical_ref="PROJETOS/COMUM/SESSION-REVISAR-US.md",
        params=[
            ("PROJETO", project),
            ("FEATURE_ID", "<resolver_no_handoff_ou_na_us_alvo>"),
            ("US_ID", "<resolver_no_handoff_ou_na_us_alvo>"),
            ("US_PATH", "<resolver_no_handoff_ou_na_us_alvo>"),
            ("BASE_COMMIT", "auto"),
            ("TARGET_COMMIT", "auto"),
            ("EVIDENCIA", "auto"),
            ("OBSERVACOES", "usar o handoff persistido na user story alvo sempre que existir"),
            ("REVIEW_MODE", "auto"),
        ],
        local_note=dedent(
            """
            - resolva primeiro a user story `ready_for_review` vigente do projeto; so use override manual quando o PM trouxer evidencia reproduzivel
            - este wrapper nao fixa a revisao na bootstrap; a US alvo muda conforme a fila
            - em caso de conflito, o handoff persistido na user story continua sendo a fonte de verdade
            """
        ).strip(),
    )


def _render_session_audit_feature(context: ProjectContext) -> str:
    """Renderiza o wrapper local de auditoria da feature."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-AUDITAR-FEATURE.md",
        title="SESSION-AUDITAR-FEATURE - Auditoria de Feature em Sessao de Chat",
        objective="Auditar a feature atualmente pronta para gate, conforme manifesto da feature e `AUDIT-LOG.md`.",
        canonical_ref="PROJETOS/COMUM/SESSION-AUDITAR-FEATURE.md",
        params=[
            ("PROJETO", project),
            ("FEATURE_ID", "<resolver_na_feature_pronta_para_gate>"),
            ("FEATURE_PATH", "<resolver_na_feature_pronta_para_gate>"),
            ("RODADA", "<resolver_na_feature_pronta_para_gate>"),
            ("BASE_COMMIT", "worktree"),
            ("AUDIT_LOG", context.rel("AUDIT-LOG.md")),
        ],
        local_note=dedent(
            f"""
            - descubra a feature pronta para auditoria a partir de `AUDIT-LOG.md` e dos manifestos `FEATURE-*.md`
            - nao congele este wrapper na bootstrap; use a rodada correspondente ao estado atual do projeto
            - o log do projeto permanece em `{context.rel("AUDIT-LOG.md")}`
            """
        ).strip(),
    )


def _render_session_remediate_hold(context: ProjectContext) -> str:
    """Renderiza o wrapper local de remediacao pos-auditoria."""
    project = context.options.nome_projeto
    return _render_session_wrapper(
        context=context,
        doc_id="SESSION-REMEDIAR-HOLD.md",
        title="SESSION-REMEDIAR-HOLD - Roteamento de Remediacao Pos-Auditoria",
        objective="Roteiar follow-ups caso a auditoria inicial da feature bootstrap retorne hold.",
        canonical_ref="PROJETOS/COMUM/SESSION-REMEDIAR-HOLD.md",
        params=[
            ("PROJETO", project),
            ("FEATURE_ID", "<resolver_na_ultima_auditoria_hold>"),
            ("FEATURE_PATH", "<resolver_na_ultima_auditoria_hold>"),
            ("RELATORIO_PATH", "<resolver_na_ultima_auditoria_hold>"),
            ("AUDIT_LOG_PATH", context.rel("AUDIT-LOG.md")),
            ("OBSERVACOES", "usar o ultimo relatorio `hold` realmente ativo"),
        ],
        local_note=dedent(
            """
            - use este wrapper apenas quando houver um `hold` real aberto no projeto
            - resolva feature e relatorio a partir do `AUDIT-LOG.md`, nao do scaffold inicial
            """
        ).strip(),
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
        "SESSION-IMPLEMENTAR-US.md",
        "SESSION-IMPLEMENTAR-TASK.md",
        "SESSION-REVISAR-US.md",
        "SESSION-AUDITAR-FEATURE.md",
        "SESSION-REMEDIAR-HOLD.md",
        "SESSION-REFATORAR-MONOLITO.md",
    ]
    local_wrappers = _bullet_list([f"`PROJETOS/{project}/{name}`" for name in wrappers])
    return dedent(
        f"""
        {_frontmatter([
            ("doc_id", "SESSION-MAPA.md"),
            ("version", "2.0"),
            ("status", "active"),
            ("owner", "PM"),
            ("last_updated", context.today),
            ("project", project),
        ])}

        # SESSION-MAPA - {project}

        > Mapa dos wrappers locais do projeto.
        > Use este arquivo como ponto de entrada quando operar em chat interativo
        > em vez de Cloud Agent autonomo.

        ## Mapa Canonico

        Leia e use como fonte de verdade:

        - `PROJETOS/COMUM/SESSION-MAPA.md`

        ## Wrappers Locais de {project}

        {local_wrappers}

        ## Regra Local Adicional

        - os wrappers locais sao presets finos do projeto, nao uma segunda fonte normativa
        - wrappers de user story/revisao/auditoria nao devem congelar a fila na bootstrap; resolva a unidade atual nos artefatos do projeto
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
        ScaffoldItem(paths.features_dir, "dir"),
        ScaffoldItem(paths.feature_dir, "dir"),
        ScaffoldItem(paths.user_stories_dir, "dir"),
        ScaffoldItem(paths.user_story_dir, "dir"),
        ScaffoldItem(paths.auditorias_dir, "dir"),
        ScaffoldItem(paths.encerramento_dir, "dir"),
        ScaffoldItem(paths.intake_path, "file", _render_intake),
        ScaffoldItem(paths.prd_path, "file", _render_prd),
        ScaffoldItem(paths.audit_log_path, "file", _render_audit_log),
        ScaffoldItem(paths.session_plan_path, "file", _render_session_planner),
        ScaffoldItem(paths.session_create_intake_path, "file", _render_session_create_intake),
        ScaffoldItem(paths.session_create_prd_path, "file", _render_session_create_prd),
        ScaffoldItem(paths.session_implement_us_path, "file", _render_session_implement_us),
        ScaffoldItem(paths.session_implement_task_path, "file", _render_session_implement_task),
        ScaffoldItem(paths.session_review_us_path, "file", _render_session_review_us),
        ScaffoldItem(paths.session_audit_feature_path, "file", _render_session_audit_feature),
        ScaffoldItem(paths.session_remediate_hold_path, "file", _render_session_remediate_hold),
        ScaffoldItem(paths.session_refactor_monolith_path, "file", _render_session_refactor_monolith),
        ScaffoldItem(paths.session_map_path, "file", _render_session_map),
        ScaffoldItem(paths.feature_manifest_path, "file", _render_feature_manifest),
        ScaffoldItem(paths.user_story_readme_path, "file", _render_user_story_readme),
        ScaffoldItem(paths.task1_path, "file", _render_task),
        ScaffoldItem(paths.audit_report_path, "file", _render_feature_audit_report),
        ScaffoldItem(paths.closing_report_path, "file", _render_closing_report),
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

    A estrutura inclui a raiz do projeto, ``features/``, a feature bootstrap,
    ``encerramento/`` e os diretórios canonicos da user story bootstrap.
    Esta função e pública para facilitar testes focados na árvore.
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
