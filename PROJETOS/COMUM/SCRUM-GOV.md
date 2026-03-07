---
doc_id: "SCRUM-GOV.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-07"
---

# SCRUM-GOV

## Cadeia de Trabalho

`PRD -> Fases -> Epicos -> Issues -> Microtasks`

## Unidade Operacional Canonica

- `issue` e a menor unidade documental completa para execucao
- `EPIC-*.md` funciona como manifesto do epico e indice das issues, nao como container canonico de criterios e tarefas detalhadas
- `SPRINT-*.md` existe apenas para selecionar e acompanhar issues; sprint nao e fonte primaria de requisitos
- criterios de aceitacao, DoD e tarefas decupadas devem viver no arquivo da issue quando o projeto estiver no padrao `issue-first`
- projetos legados podem manter issues embutidas no epico, mas novos projetos devem preferir `issues/ISSUE-*.md`

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

- arquivo de fase preenchido com objetivo, gate, escopo e indice de epicos
- todos os epicos da fase possuem documento proprio
- gate de saida da fase definido de forma objetiva
- status da fase rastreavel por evidencia
- fase com gate concluido e evidencia consolidada deve ser movida para a pasta `feito/` do projeto

### Epico

- objetivo tecnico mensuravel definido
- resultado de negocio verificavel definido
- Definition of Done especifica evidencia consolidada
- dependencias declaradas sem acoplamento indevido a outros epicos
- decisao arquitetural considerada: modularidade, manutenibilidade e evitacao de monolitos
- arquivo do epico referencia todas as issues do escopo por tabela ou indice navegavel
- projetos novos devem manter as issues detalhadas em `issues/ISSUE-*.md`

### Issue

- documento proprio com frontmatter padronizado
- user story explicita
- plano TDD definido em `Red`, `Green`, `Refactor`
- criterios de aceitacao no formato `Given/When/Then`
- Definition of Done da issue explicita
- tarefas decupadas, concluiveis e sem duplicar o texto dos criterios
- tamanho compativel com `SPRINT-LIMITS.md`
- abordagem arquitetural considerada: responsabilidade unica, baixo acoplamento, funcoes e arquivos nao monoliticos
- arquivos reais impactados ou testados declarados
- artifact minimo ou evidencia verificavel declarada quando houver side effect relevante

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
- referencia `issues/ISSUE-*.md` por ID e documento, sem duplicar criterios, DoD ou tarefas
- pode existir em `sprints/SPRINT-*.md`, mas nunca substitui fase, epico ou issue como fonte de verdade

## Regras Anti Jira Inflation

- nenhuma tarefa existe sem decomposicao suficiente para execucao
- sprint nao e camada estrutural entre fase e epico
- nenhuma data e inferida sem fonte explicita
- nao criar issue que represente mais de um resultado tecnico
- nao criar microtask que apenas repete texto da issue
- nao referenciar dependencias entre epicos por links diretos em arquivos de epico
- nao duplicar criterios de aceitacao ou tarefas da issue dentro de `SPRINT-*.md`
- nao manter backlog detalhado de issue apenas no arquivo `EPIC-*.md` em projetos novos

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
