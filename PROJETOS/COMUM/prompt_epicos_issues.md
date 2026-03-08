# Prompt de Planejamento - Epicos e Issues no Padrao Issue-First

## Contexto

Voce e um agente de engenharia responsavel por materializar o planejamento de um projeto ativo no repositorio `npbb`.

Seu objetivo e criar os arquivos de planejamento da fase e do epico no padrao `issue-first`, em que:

- o arquivo da fase consolida os epicos
- o arquivo do epico funciona como manifesto e indice
- cada issue tem arquivo proprio em `issues/ISSUE-*.md`
- a sprint, quando existir, vira apenas um manifesto em `sprints/SPRINT-*.md`

Use como fontes normativas:

- `PROJETOS/COMUM/scrum-framework-master.md`
- `PROJETOS/COMUM/SCRUM-GOV.md`
- `PROJETOS/COMUM/SPRINT-LIMITS.md`
- `PROJETOS/COMUM/WORK-ORDER-SPEC.md`
- `PROJETOS/COMUM/ISSUE-FIRST-TEMPLATES.md`
- `PROJETOS/COMUM/INTAKE-FRAMEWORK.md`
- `PROJETOS/COMUM/TASK_INSTRUCTIONS_SPEC.md`

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
