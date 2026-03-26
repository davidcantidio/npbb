---
doc_id: "GOV-SCRUM.md"
version: "2.10"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
---

# GOV-SCRUM

## Cadeia de Trabalho

`Intake -> PRD -> Features -> User Stories -> Tasks`

## Unidade Operacional Canonica

- `feature` e a unidade de entrega completa, com comportamento entregavel,
  dependencias declaradas e auditoria propria
- `user story` e a menor unidade documental completa para execucao;
  concentra contexto tecnico, criterios, DoD e lista de tasks da feature de origem
- `task` e o menor item executavel dentro da user story
- `instruction` e a menor unidade atomica dentro da task quando
  `task_instruction_mode` exigir detalhamento

## Modos de Operacao

- `boot-prompt.md`: modo autonomo; o agente descobre a unidade elegivel e executa
- `SESSION-*.md`: modo interativo; o humano escolhe o prompt e informa os parametros da sessao
- ambos os modos usam a mesma governanca documental; o que muda e o protocolo operacional

## Aprovacao Multi-Agente

- intake e PRD continuam exigindo aprovacao humana explicita do usuario/PM
- apos o PRD aprovado, os gates de planejamento, revisao pos-user-story,
  auditoria e remediacao pos-hold sao obrigatoriamente executados por um
  `agente senior` independente
- `agente senior` significa o modelo configurado em `OPENCLAW_AUDITOR_MODEL`,
  acessado via OpenRouter; o default operacional esperado e
  `openrouter/anthropic/claude-opus-4.6`
- `SESSION-*` continua sendo a superficie interativa escolhida pelo humano,
  mas nao introduz confirmacoes humanas extras apos o PRD
- override humano apos o PRD so existe como excecao explicita para conflito
  reproduzivel de parametros/evidencias, cancelamento declarado ou contexto
  externo novo
- o agente local executa planejamento fino, implementacao, testes e
  validacoes locais ate `ready_for_review`; o agente senior aprova, pede
  ajustes ou reprova
- todo agente deve reler PRD, feature de origem, criterios e artefato alvo
  antes de propor, aprovar ou executar mudanca, para impedir `scope-drift`
- qualquer resposta de gate deve ser tratada como uma entre:
  `APROVADO`, `AJUSTAR`, `REPROVADO`

## Definition of Done por Tipo

### Intake

- seguir `GOV-INTAKE.md` como fonte unica do gate `Intake -> PRD`

### Feature

- dependencias satisfeitas declaradas no PRD
- todas as User Stories `done`
- auditoria com veredito `go`
- branch mergeada para `main`

### User Story

- arquivo proprio com frontmatter padronizado
- user story, contexto tecnico, criterios `Given/When/Then` e DoD declarados
- tasks decupadas com `task_instruction_mode` definido
- handoff de revisao persistido ao concluir execucao
- `done` somente apos revisao do agente senior aprovada

### Task

- task rastreavel e documentada no formato canonico definido em `TEMPLATE-TASK.md`
- quando `tdd_aplicavel: true`, ordem TDD e `testes_red` completos conforme `SPEC-TASK-INSTRUCTIONS.md`
- validacoes obrigatorias executadas antes de encerrar
- commit da task realizado conforme `GOV-COMMIT-POR-TASK.md` antes da cascata de fechamento

### Auditoria

- seguir `GOV-AUDITORIA.md` como fonte unica de vereditos, severidades, thresholds e remediacao

## Regras de Status

Status canonicos persistidos por nivel:

- `feature`: `todo`, `active`, `done`, `cancelled`
- `user story`: `todo`, `active`, `ready_for_review`, `done`, `cancelled`
- `task`: `todo`, `active`, `done`, `cancelled`

Regra derivada:

- `todo`: nenhum trabalho iniciado no nivel atual
- `active`: execucao em andamento no nivel atual, ou filho ainda nao encerrado
- `ready_for_review`: so vale para `user story`; execucao encerrada, tasks
  `done`, DoD de implementacao conferido e handoff de revisao persistido na
  `README.md`, aguardando veredito do agente senior
- `done`: execucao encerrada e DoD do nivel atual fechado; para `feature`,
  exige todas as user stories `done` ou `cancelled` e gate de auditoria com
  veredito `go` (`audit_gate: approved`)
- `cancelled`: cancelamento explicito com justificativa

Regras adicionais:

- `ready_for_review` nao satisfaz dependencias entre user stories; apenas
  `done` ou `cancelled` liberam a proxima user story dependente
- `feature` permanece `active` enquanto existir user story `todo`, `active`
  ou `ready_for_review`
- `feature` tambem permanece `active` quando todas as user stories ja estao
  `done` ou `cancelled`, mas o `audit_gate` ainda esta `not_ready`, `pending`
  ou `hold`
- user story filha em `ready_for_review` conta como entrega ainda nao
  encerrada para a feature
- `audit_gate: pending` so e elegivel quando todas as user stories da feature
  estiverem `done` ou `cancelled`
- se uma user story voltar para `active` apos `correcao_requerida`, a feature
  deve ser recalculada e qualquer `audit_gate: pending` deve voltar para
  `not_ready`

`BLOQUEADO` e `BLOCKED_LIMIT` sao estados operacionais e nao devem ser
persistidos como status principal de `feature`, `user story` ou `task`.

## Gate de Auditoria da Feature

Estados operacionais do gate:

- `not_ready`: a feature ainda tem user stories em `todo`, `active` ou
  `ready_for_review`
- `pending`: todas as user stories da feature estao `done` ou `cancelled`,
  aguardando rodada de auditoria
- `hold`: a ultima auditoria reprovou o gate da feature
- `approved`: a ultima auditoria aprovou o gate da feature com veredito `go`

O significado operacional e os criterios de auditoria vivem em
`GOV-AUDITORIA.md`. Ate `GOV-AUDITORIA-FEATURE.md` deixar de ser placeholder,
esta taxonomia permanece a referencia vigente para o gate da feature.

## Task Instructions

- `instruction` nao e documento independente; vive inline numa user story em
  formato legado (ficheiro `.md` unico) ou no corpo de `TASK-N.md` quando a
  user story for granularizada (pasta com `README.md` e `TASK-*.md`)
- os criterios de quando `required` e obrigatorio vivem exclusivamente em `SPEC-TASK-INSTRUCTIONS.md`
- user story com `task_instruction_mode: required` sem detalhamento completo por
  task no formato escolhido (`TASK-N.md` na user story granularizada ou
  `## Instructions por Task` na user story em formato legado) nao e elegivel
  para execucao

## Commit por Task

- apos cada task concluida, o executor deve fazer commit com mensagem descritiva
- formato e regras vivem em `GOV-COMMIT-POR-TASK.md`
- o commit deve identificar projeto, user story e task conforme esse documento
- sem commit por task, a cascata de fechamento nao deve ser executada

## Procedimento de Review-Ready e Fechamento de User Story

Ao concluir a execucao de uma user story, a sessao deve primeiro sincronizar o
estado `ready_for_review`. O fechamento em `done` fica reservado para a sessao
de revisao pos-user-story. Pular um passo deixa o backlog da feature
incoerente para a proxima leitura.

### 1. Ao concluir a execucao

1. Atualizar a `README.md` da user story para `ready_for_review`: confirmar
   que todas as tasks estao `done`, marcar os itens do DoD de implementacao,
   atualizar `last_updated` e persistir o handoff de revisao com
   `base_commit`, `target_commit`, `evidencia`, `commits_execucao`,
   `validacoes_executadas`, `arquivos_de_codigo_relevantes` e `limitacoes`.
2. Atualizar a feature pai: ajustar a linha da user story na tabela de user
   stories da feature para `ready_for_review` e manter a feature em `active`
   enquanto existir user story `todo`, `active` ou `ready_for_review`.
3. Nao avancar o `audit_gate` da feature para `pending` por execucao sozinha;
   esse estado so pode existir quando todas as user stories ja estiverem
   `done` ou `cancelled`.

### 2. Ao concluir a revisao pos-user-story

1. Se o veredito for `aprovada`, promover a user story
   `ready_for_review -> done` e recalcular a feature; quando todas as user
   stories estiverem `done` ou `cancelled`, a feature pode avancar para
   `audit_gate: pending`.
2. Se o veredito for `correcao_requerida` por escopo original faltante,
   devolver a mesma user story `ready_for_review -> active`, adicionando ou
   ajustando tasks dentro da propria user story sempre que a correcao ainda
   pertencer ao escopo original; se a feature ja estiver com
   `audit_gate: pending`, voltar para `not_ready`.
3. Se o veredito for `cancelled`, marcar a user story como `cancelled` e
   recalcular a feature conforme o novo estado.

Regras de aplicacao:

- a cascata e sempre `user story -> feature`
- `audit_gate: pending` so pode existir quando todas as user stories da
  feature estiverem `done` ou `cancelled`
- o agente nao deve marcar a feature como `done` diretamente; isso continua
  reservado ao fechamento do gate de auditoria com veredito `go`
- user story `cancelled` conta como encerrada para calculo de completude da
  feature
- user story `ready_for_review` nunca conta como encerrada para calculo de
  completude da feature
- review pos-user-story nao abre nova user story local; o ciclo de correcao
  permanece dentro da mesma user story ate veredito final
- lacuna nos criterios `Given/When/Then` descoberta durante execucao (sem
  contradizer o PRD) exige trilha `SCOPE-LEARN.md` conforme
  `TEMPLATE-SCOPE-LEARN.md` e decisao do agente senior em
  `SESSION-REVISAR-US.md`; alterar criterios em silencio viola rastreabilidade

## Review Pos-User-Story

- o proximo passo natural apos uma user story chegar em `ready_for_review` e
  uma sessao de revisao do agente senior via `PROJETOS/COMUM/SESSION-REVISAR-US.md`
  (ou o wrapper `SESSION-REVISAR-US.md` do projeto, quando existir)
- a review pos-user-story altera a cadeia operacional canonica para
  `Intake -> PRD -> Features -> User Stories -> Tasks -> Revisao -> Auditoria de Feature`
- a review pos-user-story nao substitui a auditoria formal da feature
- a review atua como gate de fechamento da user story antes de `done`
- vereditos canonicos da review: `aprovada`, `correcao_requerida`, `cancelled`
- `aprovada`: promove a user story para `done` e recalcula a feature
- `correcao_requerida`: devolve a mesma user story para `active`; o revisor
  deve preferir criar ou ajustar `TASK-N.md` dentro da propria user story
  quando o fix ainda pertence ao escopo original
- `cancelled`: encerra a user story com justificativa e recalcula a feature
- review pos-user-story nao gera novo artefato persistido alem da atualizacao
  da propria user story, da feature pai e de `SCOPE-LEARN.md` quando usado como
  aprendizado emergente (`TEMPLATE-SCOPE-LEARN.md`)
- feature com `audit_gate: approved` nao deve receber reabertura de user story
  no mesmo ciclo; qualquer remediacao apos aprovacao deve seguir fluxo proprio
  fora da feature ja encerrada

## Encerramento de Feature

- cada projeto ativo deve manter `features/`, `encerramento/`,
  `INTAKE-<PROJETO>.md`, `PRD-<PROJETO>.md` e `AUDIT-LOG.md`
- cada feature ativa deve manter `FEATURE-<N>.md`, `user-stories/` e
  `auditorias/`
- quando uma feature atingir `done`, sua pasta inteira deve ser movida para
  `features/encerradas/FEATURE-<N>-<NOME>/`
- a movimentacao so pode ocorrer apos gate `approved` e consolidacao das
  evidencias
