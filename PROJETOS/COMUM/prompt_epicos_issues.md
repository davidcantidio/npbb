# Prompt de Planejamento - Epicos e Issues no Padrao Issue-First

## Contexto

Voce e um agente de engenharia responsavel por materializar o planejamento de um novo projeto no repositorio `npbb`.

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

---

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

Se o PO ainda nao tiver selecionado a sprint, o arquivo em `sprints/` pode ser omitido.

---

## Regras Obrigatorias

### Nomeacao e frontmatter

- todo arquivo novo comeca com frontmatter YAML contendo `doc_id`, `version`, `status`, `owner`, `last_updated`
- `doc_id` e o nome do arquivo sem extensao
- novos `EPIC-*.md`, `ISSUE-*.md` e `SPRINT-*.md` iniciam com status `todo`

### Conteudo do arquivo de fase

O arquivo `F<N>_<PROJETO>_EPICS.md` deve conter:

- objetivo da fase
- gate de saida objetivo
- tabela de epicos
- dependencias entre epicos
- escopo dentro e fora

### Conteudo do arquivo de epico

O arquivo `EPIC-*.md` deve conter:

- objetivo tecnico mensuravel
- resultado de negocio mensuravel
- contexto arquitetural
- Definition of Done do epico
- tabela indice das issues com colunas `Issue ID | Nome | Objetivo | SP | Status | Documento`
- artifact minimo do epico
- dependencias com links Markdown canonicos
- navegacao rapida com wikilinks qualificados

O epico nao deve duplicar criterios detalhados, DoD da issue ou tarefas decupadas se a issue possuir arquivo proprio.

### Conteudo dos arquivos de issue

Cada `issues/ISSUE-*.md` deve conter:

- user story
- contexto tecnico minimo
- plano TDD com `Red`, `Green`, `Refactor`
- criterios de aceitacao no formato `Given / When / Then`
- Definition of Done da issue
- tarefas decupadas e concluiveis
- arquivos reais do repositorio a serem tocados ou testados
- artifact minimo ou evidencia verificavel
- dependencias com links Markdown
- navegacao rapida com wikilinks qualificados

### Conteudo do arquivo de sprint

Cada `sprints/SPRINT-*.md` deve conter apenas:

- objetivo da sprint
- capacidade declarada
- tabela de issues selecionadas
- riscos e bloqueios
- decisao de encerramento

Nao repetir criterios de aceitacao, DoD ou tarefas da issue no arquivo de sprint.

---

## Regras de Conteudo

- nenhum placeholder como `...`, `<texto>` ou `TODO`
- toda issue deve representar um unico resultado tecnico verificavel
- toda issue deve caber em uma sprint e respeitar `SPRINT-LIMITS.md`
- tarefas devem ser atomicas e executaveis sem abrir novo escopo
- o planejamento deve priorizar modularidade, baixo acoplamento e evitar monolitos
- dependencias entre epicos aparecem no arquivo da fase; dependencias entre issues do mesmo epico aparecem na propria issue

---

## Convencao de Links

- links Markdown relativos sao a referencia canonica
- wikilinks sao complementares e nunca unicos
- usar wikilinks qualificados por caminho local
- exemplos validos:
  - `[Epic](../EPIC-F1-01-NOME.md)`
  - `[PRD](../../PRD-PROJETO.md)`
  - `[[../EPIC-F1-01-NOME]]`
  - `[[../../PRD-PROJETO]]`

---

## Output Esperado

Ao final, entregar:

1. `F<N>_<PROJETO>_EPICS.md`
2. `EPIC-F<N>-<NN>-<NOME>.md`
3. todos os `issues/ISSUE-*.md` do epico
4. opcionalmente `sprints/SPRINT-*.md` se a selecao da sprint ja estiver definida

Cada arquivo deve estar pronto para salvar, sem campos vazios e com navegacao funcional por links Markdown e wikilinks qualificados.
