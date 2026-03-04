---
doc_id: "SCRUM-GOV.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-03"
---

# SCRUM-GOV

## Cadeia de Trabalho

`PRD -> Fases -> Epicos -> Issues -> Microtasks`

## Fluxo de Decomposicao

1. O PRD define objetivo, escopo, arquitetura, criterios de aceite e governanca.
2. Cada fase agrupa uma fatia coerente de entrega com gate de saida proprio.
3. Cada epico representa um resultado tecnico mensuravel dentro de uma fase.
4. Cada issue detalha uma entrega atomica, verificavel e concluivel.
5. Cada microtask descreve o menor passo operacional necessario para completar uma issue sem ambiguidade.

## Definition of Done por Tipo

### PRD

- objetivo e problema explicitados
- escopo e fora de escopo definidos
- arquitetura, fases e criterios de aceite definidos
- governanca e riscos materializados

### Fase

- `EPICS.md` preenchido com objetivo, gate e escopo
- todos os epicos da fase possuem documento proprio
- gate de saida da fase definido de forma objetiva
- status da fase rastreavel por evidencia
- fase com gate concluido e evidencia consolidada deve ser movida para a pasta `feito/` do projeto

### Epico

- objetivo tecnico mensuravel definido
- resultado de negocio verificavel definido
- Definition of Done especifica evidencia consolidada
- dependencias declaradas sem acoplamento indevido a outros epicos

### Issue

- user story explicita
- plano TDD definido em `Red`, `Green`, `Refactor`
- criterios de aceitacao no formato `Given/When/Then`
- tamanho compativel com `SPRINT-LIMITS.md`

### Microtask

- descreve uma unica acao operacional
- possui saida esperada e criterio de conclusao
- pode ser executada sem abrir novo escopo
- nao duplica issue ou epico

### Sprint

- respeita limites de capacidade e criticidade
- nao vira camada estrutural do backlog
- agrega apenas items com rastreabilidade a fase/epico/issue
- produz status consolidado sem datas inventadas

## Regras Anti Jira Inflation

- nenhuma tarefa existe sem decomposicao suficiente para execucao
- sprint nao e camada estrutural entre fase e epico
- nenhuma data e inferida sem fonte explicita
- nao criar issue que represente mais de um resultado tecnico
- nao criar microtask que apenas repete texto da issue
- nao referenciar dependencias entre epicos por links diretos em arquivos de epico

## Regras de Arquivamento de Fase

- cada projeto em `PROJETOS/` deve manter uma pasta `feito/` na sua raiz
- quando uma fase atingir `done`, sua pasta inteira deve ser movida de `<projeto>/F*-.../` para `<projeto>/feito/F*-.../`
- a movimentacao so pode ocorrer apos validacao do gate da fase e consolidacao da evidencia correspondente em `artifacts/`
- links internos e automacoes que dependam do caminho da fase devem ser atualizados no mesmo change set

## Status Validos

- `todo`
- `active`
- `done`
- `cancelled`
