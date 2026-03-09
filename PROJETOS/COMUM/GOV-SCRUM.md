---
doc_id: "GOV-SCRUM.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# GOV-SCRUM

## Cadeia de Trabalho

`Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias`

## Unidade Operacional Canonica

- `issue` e a menor unidade documental completa para execucao
- `task` e o menor item executavel dentro da issue
- `instruction` e a menor unidade atomica dentro da task quando `task_instruction_mode` exigir detalhamento
- `EPIC-*.md` funciona como manifesto do epico e indice das issues
- `SPRINT-*.md` existe apenas para selecao operacional e capacidade
- `auditorias/RELATORIO-AUDITORIA-*.md` e a unidade documental da auditoria de fase

## Modos de Operacao

- `boot-prompt.md`: modo autonomo; o agente descobre a unidade elegivel e executa
- `SESSION-*.md`: modo interativo; o PM informa parametros e aprova cada etapa material
- ambos os modos usam a mesma governanca documental; o que muda e o protocolo operacional

## Definition of Done por Tipo

### Intake

- seguir `GOV-INTAKE.md` como fonte unica do gate `Intake -> PRD`

### Fase

- arquivo de fase preenchido com objetivo, gate de saida, tabela de epicos, escopo e dependencias
- manifesto da fase declara o estado atual do gate de auditoria
- manifesto da fase inclui checklist verificavel de transicao `not_ready -> pending -> hold/approved`
- status da fase deriva do estado dos epicos combinado ao gate
- fase `done` so existe apos auditoria `go` e movimentacao para `feito/`

### Epico

- objetivo tecnico mensuravel definido
- contexto arquitetural e dependencias documentados
- Definition of Done explicita evidencia consolidada
- arquivo referencia todas as issues do escopo por tabela navegavel
- status deriva do estado das issues filhas

### Issue

- documento proprio com frontmatter padronizado
- `task_instruction_mode` definido como `optional` ou `required`
- user story, contexto tecnico, plano `Red/Green/Refactor`, criterios e DoD declarados
- tasks decupadas e artefato minimo declarados
- `decision_refs` opcional quando houver decisao R2/R3 relevante
- quando `task_instruction_mode = required`, existe um bloco `Instructions por Task` completo e consistente

### Sprint

- respeita `GOV-SPRINT-LIMITES.md`
- nao substitui fase, epico ou issue como fonte de verdade
- referencia `issues/ISSUE-*.md` por ID e documento
- status deriva do estado das issues selecionadas

### Auditoria

- seguir `GOV-AUDITORIA.md` como fonte unica de vereditos, severidades, thresholds e remediacao

## Regras de Status

Status canonicos persistidos:

- `todo`
- `active`
- `done`
- `cancelled`

Regra derivada:

- `todo`: nenhum filho iniciado
- `active`: existe filho `active` ou `done`, mas nem todos estao `done`
- `done`: todos os filhos estao `done` e o DoD do pai foi fechado
- `cancelled`: cancelamento explicito com justificativa

`BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais e nao devem ser persistidos como status principal de fase, epico, issue ou sprint.

## Gate de Auditoria da Fase

Estados operacionais do gate:

- `not_ready`
- `pending`
- `hold`
- `approved`

O significado operacional e os criterios de auditoria vivem em `GOV-AUDITORIA.md`.

## Task Instructions

- `instruction` nao e documento independente; vive inline na issue
- os criterios de quando `required` e obrigatorio vivem exclusivamente em `SPEC-TASK-INSTRUCTIONS.md`
- issue `required` sem bloco completo de `Instructions por Task` nao e elegivel para execucao

## Arquivamento de Fase

- cada projeto ativo deve manter `feito/`, `INTAKE-<PROJETO>.md`, `PRD-<PROJETO>.md` e `AUDIT-LOG.md`
- cada fase ativa deve manter `issues/`, `sprints/` e `auditorias/`
- quando uma fase atingir `done`, sua pasta inteira deve ser movida para `<projeto>/feito/F*-.../`
- a movimentacao so pode ocorrer apos gate `approved` e consolidacao das evidencias
