---
doc_id: "PROMPT-PLANEJAR-FASE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# PROMPT-PLANEJAR-FASE

## Como usar

Use este prompt via `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`.
Ele define a estrutura canonica do planejamento; o PM nao deve colar este
arquivo diretamente no chat fora do fluxo de sessao.

## Prompt

## Contexto

Voce e um agente de engenharia responsavel por materializar o planejamento de um projeto ativo no repositorio atual.

Seu objetivo e criar os arquivos de planejamento da fase e do epico no padrao `issue-first`, em que:

- o arquivo da fase consolida os epicos
- o arquivo do epico funciona como manifesto e indice
- cada issue tem arquivo proprio em `issues/ISSUE-*.md`
- a sprint, quando existir, vira apenas um manifesto em `sprints/SPRINT-*.md`

Use como fontes normativas:

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/GOV-SPRINT-LIMITES.md`
- `PROJETOS/COMUM/GOV-WORK-ORDER.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`

## Tarefa

Criar, para a fase e o epico indicados, a seguinte estrutura minima:

```text
PROJETOS/<PROJETO>/
  F<N>-<NOME-DA-FASE>/
    F<N>_<PROJETO>_EPICS.md
    EPIC-F<N>-<NN>-<NOME>.md
    issues/
      ISSUE-F<N>-<NN>-001-<NOME>.md
      ISSUE-F<N>-<NN>-002-<NOME>.md
    sprints/
      SPRINT-F<N>-01.md
```

Se a sprint ainda nao estiver definida, o arquivo em `sprints/` pode ser omitido.

## Regras Obrigatorias

- todo arquivo novo comeca com frontmatter YAML contendo `doc_id`, `version`, `status`, `owner`, `last_updated`
- novos `EPIC-*.md`, `ISSUE-*.md` e `SPRINT-*.md` iniciam com status `todo`
- o arquivo de fase deve conter objetivo, gate de saida, tabela de epicos, dependencias e escopo dentro/fora
- o epico nao duplica criterios detalhados da issue
- cada issue deve conter `task_instruction_mode`, user story, contexto tecnico, plano TDD, criterios, DoD, tarefas, arquivos reais e artefato minimo
- se a issue envolver risco alto ou ordem critica, usar `task_instruction_mode: required` e adicionar `## Instructions por Task` com um bloco por task
- se a issue for simples, usar `task_instruction_mode: optional` e manter apenas as tasks decupadas
- `SPRINT-*.md` nao repete criterios, DoD ou tarefas da issue
- usar apenas os status documentais `todo`, `active`, `done`, `cancelled`
- ao concluir uma fase, o arquivamento futuro sera em `<projeto>/feito/`
- use o intake e o PRD como origem do escopo e nao invente requisitos fora deles

## Artefatos Vinculados

- sessao de chat para este fluxo: `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- estrutura canonica dos artefatos: `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- limites de sprint: `PROJETOS/COMUM/GOV-SPRINT-LIMITES.md`
- regras de `task_instruction_mode`: `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`
