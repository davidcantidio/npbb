---
doc_id: "GOV-SCRUM.md"
version: "2.2"
status: "active"
owner: "PM"
last_updated: "2026-03-16"
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

## Commit por Task

- apos cada task concluida, o executor deve fazer commit com mensagem descritiva
- formato e regras vivem em `GOV-COMMIT-POR-TASK.md`
- o commit deve conter PROJETO, ISSUE_ID, TASK_ID e descricao breve
- sem commit por task, a cascata de fechamento nao deve ser executada

## Procedimento de Fechamento de Issue

Ao concluir uma issue, a cascata de fechamento deve ser executada em ordem.
Pular um passo deixa backlog, fase e sprint incoerentes para a proxima leitura.

1. Fechar a issue: marcar `status: done`, atualizar `last_updated` e confirmar
   que todos os itens do DoD estao marcados.
2. Atualizar o epico pai: ajustar a linha da issue na tabela `Issues do Epico`;
   se todas as issues estiverem encerradas, marcar o epico como `done`,
   senao manter `active` quando ja houver entrega parcial.
3. Atualizar o manifesto da fase: ajustar a linha do epico na tabela `Epicos`;
   quando todos os epicos estiverem `done`, mover o `audit_gate` para `pending`;
   antes disso, a fase permanece `todo` ou `active` conforme o progresso.
4. Atualizar a sprint: ajustar a linha da issue na tabela `Issues Selecionadas`;
   quando todas as issues da sprint estiverem `done` ou `cancelled`, marcar a
   sprint como `done`.

Regras de aplicacao:

- a cascata e sempre `issue -> epico -> fase -> sprint`
- `audit_gate: pending` so pode existir quando todos os epicos da fase estiverem `done`
- o agente nao deve marcar a fase como `done` diretamente; isso continua
  reservado ao fechamento do gate de auditoria com veredito `go`
- issue `cancelled` conta como encerrada para calculo de completude do epico e da sprint

## Review Pos-Issue Opcional

- `SESSION-REVISAR-ISSUE.md` e um fluxo ad hoc, acionado apenas quando o PM
  pedir uma segunda leitura apos a execucao de uma issue
- a review pos-issue nao altera a cadeia canonica
  `Intake -> PRD -> Fases -> Epicos -> Issues -> Tasks -> Auditorias`
- a review pos-issue nao substitui a auditoria formal da fase
- a review pode inspecionar uma issue ja marcada como `done`, mas nao reabre
  automaticamente a issue original nem desfaz a cascata
  `issue -> epico -> fase -> sprint`
- vereditos canonicos da review: `aprovada`, `correcao_requerida`, `cancelled`
- `aprovada`: encerra a review sem gerar artefato novo
- `correcao_requerida`: gera follow-up rastreavel; se a remediacao for local e
  contida, abrir nova `ISSUE-*.md` no mesmo epico e fase; se for estrutural ou
  sistemica, abrir `INTAKE-*.md`
- issue gerada por review deve citar a issue de origem no `Contexto Tecnico` e
  em `Dependencias`
- review pos-issue nao gera relatorio persistido; o unico artefato novo
  permitido em v1 e a `ISSUE-*.md` local quando houver follow-up elegivel
- quando a review gerar nova issue local, a sincronizacao documental minima e:
  - adicionar a issue ao `EPIC-*.md` pai
  - manter ou retornar o epico para `active`, se necessario
  - se a fase estiver com `audit_gate: pending`, voltar para `not_ready`
  - a sprint nao e atualizada automaticamente; a nova issue entra no fluxo de
    planejamento normal
- fase com `audit_gate: approved` nao deve receber nova issue local de review;
  qualquer remediacao apos aprovacao deve seguir fluxo proprio fora da fase ja
  fechada

## Arquivamento de Fase

- cada projeto ativo deve manter `feito/`, `INTAKE-<PROJETO>.md`, `PRD-<PROJETO>.md` e `AUDIT-LOG.md`
- cada fase ativa deve manter `issues/`, `sprints/` e `auditorias/`
- quando uma fase atingir `done`, sua pasta inteira deve ser movida para `<projeto>/feito/F*-.../`
- a movimentacao so pode ocorrer apos gate `approved` e consolidacao das evidencias
