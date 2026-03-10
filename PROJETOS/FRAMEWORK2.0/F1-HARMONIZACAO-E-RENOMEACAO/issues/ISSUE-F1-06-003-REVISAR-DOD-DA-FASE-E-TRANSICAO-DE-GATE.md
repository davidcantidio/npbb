---
doc_id: "ISSUE-F1-06-003-REVISAR-DOD-DA-FASE-E-TRANSICAO-DE-GATE.md"
version: "1.1"
status: "cancelled"
owner: "PM"
last_updated: "2026-03-10"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-06-003 - Revisar DoD da fase e transicao de gate

## Encerramento

- status_final: cancelada por superveniencia de `F1-R02` via `situacao A` da
  verificacao de defasagem de estado de auditoria
- motivo: `AUDIT-LOG.md` e `RELATORIO-AUDITORIA-F1-R02.md` ja registram rodada
  posterior com veredito `go` e gate `approved` em `2026-03-10`, tornando
  obsoleta esta remediacao limitada ao contexto de `F1-R01`
- acao_substituta: nenhuma implementacao nesta issue; qualquer reconciliacao
  residual entre manifesto, backlog e auditoria deve ser tratada em trilha
  propria, com decisao explicita do PM

## User Story

Como mantenedor do FRAMEWORK2.0, quero revisar o DoD da F1 e a transicao
operacional do gate apos o saneamento documental para que `F1_FRAMEWORK2_0_EPICS.md`
e `AUDIT-LOG.md` permanecam coerentes com o `hold` de `F1-R01` e com os
follow-ups ja roteados. Essa necessidade foi superada pela rodada posterior
`F1-R02`, que promoveu a fase para `approved`.

## Contexto Tecnico

O follow-up bloqueante B3 de `RELATORIO-AUDITORIA-F1-R01.md` exige revisar o
DoD da fase e a transicao operacional de gate depois da reconciliacao dos
artefatos apontados em B1 e da normalizacao das sprints em B2. A governanca
explicita que:

- o gate da fase permanece `hold` ate nova rodada com veredito `go`
- a fase continua rastreavel pelo manifesto da fase e pelo `AUDIT-LOG.md`
- follow-ups do `hold` precisam permanecer vinculados ao relatorio de origem

Esta issue cobria apenas a coerencia entre manifesto da fase e `AUDIT-LOG.md`
dentro do contexto de `F1-R01`. A verificacao de defasagem identificou que esse
estado foi superado por `F1-R02`, entao a issue foi encerrada sem executar
mudancas documentais adicionais.

## Plano TDD

- status_final: cancelada por superveniencia de `F1-R02`
- motivo: a rodada posterior registrada no `AUDIT-LOG.md` tornou obsoleta a
  remediacao local limitada a `F1-R01`
- acao_substituta: nenhuma alteracao em manifesto, gate ou log sera inferida
  nesta issue; o conflito residual deve ser tratado fora desta trilha

## Criterios de Aceitacao

- Given a verificacao de defasagem encontra `F1-R02` com gate `approved`, When o
  PM escolhe `situacao A`, Then a issue e encerrada como `cancelled` com
  justificativa explicita.
- Given a issue cancelada, When for consultada junto com `AUDIT-LOG.md` e
  `RELATORIO-AUDITORIA-F1-R02.md`, Then o leitor entende por que a remediacao
  limitada a `F1-R01` nao deve mais ser executada.
- Given ainda existem inconsistencias residuais no backlog documental, When esta
  issue e encerrada, Then nenhuma promocao, reversao ou reconciliacao adicional
  de gate e inferida automaticamente por esta trilha.

## Definition of Done da Issue

- [x] issue cancelada formalmente por superveniencia de `F1-R02`
- [x] justificativa registrada com referencia a `AUDIT-LOG.md` e
      `RELATORIO-AUDITORIA-F1-R02.md`
- [x] nenhuma alteracao de manifesto, gate ou rodada foi inferida nesta issue
- [x] necessidade de reconciliacao residual explicitamente delegada para trilha
      separada

## Tasks Decupadas

- [x] T1: registrar a defasagem entre `F1-R01/hold` e `F1-R02/approved`
- [x] T2: encerrar a issue como `cancelled` com justificativa rastreavel
- [x] T3: registrar no `AUDIT-LOG.md` que o follow-up `B3` foi superado por
      `F1-R02`

## Instructions por Task

### T1
- objetivo: determinar exatamente o que o manifesto da fase e o `AUDIT-LOG.md`
  devem refletir apos B1 e B2, sem inferir uma nova auditoria
- precondicoes:
  - `RELATORIO-AUDITORIA-F1-R01.md` lido integralmente
  - entendimento claro de que B1 e B2 tratam reconciliacao de artefatos e
    sprints antes desta issue
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`
  - `PROJETOS/COMUM/GOV-AUDITORIA.md`
  - `PROJETOS/COMUM/GOV-SCRUM.md`
- passos_atomicos:
  1. listar os itens do DoD da fase e do checklist de gate que ja podem ser
     confirmados apos B1/B2
  2. identificar quais campos do manifesto e do `AUDIT-LOG.md` devem permanecer
     em `hold`
  3. separar claramente o que e saneamento documental do que exigiria nova
     auditoria formal
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: matriz objetiva de atualizacoes permitidas em manifesto e
  `AUDIT-LOG.md` dentro do contexto de `F1-R01`
- testes_ou_validacoes_obrigatorias:
  - `rg -n "hold|approved|ultima_auditoria|gate_atual|Definition of Done da Fase|Follow-up" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md PROJETOS/COMUM/GOV-AUDITORIA.md PROJETOS/COMUM/GOV-SCRUM.md`
- stop_conditions:
  - parar se a coerencia so puder ser obtida criando uma nova rodada de
    auditoria
  - parar se algum item do DoD depender de evidencia nao registrada em `F1-R01`

### T2
- objetivo: atualizar o manifesto da fase para o estado correto pos-saneamento,
  mantendo o gate em `hold`
- precondicoes:
  - T1 concluida
  - criterio claro do que pode ser marcado no DoD e no checklist
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- passos_atomicos:
  1. revisar checkboxes do DoD da fase conforme as evidencias e o saneamento
     concluido
  2. alinhar `gate_atual`, `ultima_auditoria` e checklist de transicao ao estado
     de `hold` vigente
  3. preservar `status: active` enquanto a fase ainda aguarda nova auditoria
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: manifesto F1 pronto para nova auditoria, mas ainda em
  `hold`
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^audit_gate:|gate_atual:|ultima_auditoria:|^## Definition of Done da Fase|^- \\[" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- stop_conditions:
  - parar se o manifesto so ficar coerente marcando `approved`
  - parar se a fase tiver de ser movida para `feito/` nesta mesma issue

### T3
- objetivo: manter `AUDIT-LOG.md` coerente com o manifesto da fase e com o
  `hold` de `F1-R01`
- precondicoes:
  - T2 concluida
  - estado final esperado do manifesto da fase definido
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- passos_atomicos:
  1. revisar a linha de `Gate Atual por Fase` da F1 para refletir o estado
     correto de `hold`
  2. revisar a linha da rodada `F1-R01` para manter destino e referencia dos
     follow-ups coerentes com a remediacao local em andamento
  3. nao adicionar nova rodada, novo veredito ou novo relatorio nesta issue
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: `AUDIT-LOG.md` coerente com a fase em `hold`, sem simular
  auditoria inexistente
- testes_ou_validacoes_obrigatorias:
  - `rg -n "F1 - HARMONIZACAO-E-RENOMEACAO|F1-R01|hold|issue-local|new-intake|cancelled" PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`
- stop_conditions:
  - parar se o log exigir registrar conclusao de follow-up ainda nao implementado
  - parar se houver pressao para criar `F1-R02` sem relatorio correspondente

### T4
- objetivo: validar que manifesto da fase, `AUDIT-LOG.md` e relatorio de origem
  contam a mesma historia operacional
- precondicoes:
  - T3 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- passos_atomicos:
  1. conferir se `gate_atual`, `audit_gate`, `ultima_auditoria` e a linha da F1
     no `AUDIT-LOG.md` sao mutuamente coerentes
  2. confirmar que os follow-ups bloqueantes continuam rastreaveis a partir de
     `F1-R01`
  3. registrar no fechamento da issue que a proxima mudanca de gate depende de
     auditoria formal posterior
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: rastreabilidade fechada do `hold` sem contradicao entre os
  artefatos
- testes_ou_validacoes_obrigatorias:
  - `rg -n "F1-R01|hold|ultima_auditoria|audit_gate|gate_atual" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
- stop_conditions:
  - parar se a validacao final revelar que B1 ou B2 ainda nao estao prontos
  - parar se surgir necessidade de remediacao adicional nao descrita em `F1-R01`

## Arquivos Reais Envolvidos

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- `PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/AUDIT-LOG.md`

## Dependencias

- [Issue Dependente](./ISSUE-F1-06-002-RECONCILIAR-STATUS-DE-EPICOS-ISSUES-E-MANIFESTO.md)
- [Issue Dependente](./ISSUE-F1-03-004-NORMALIZAR-MANIFESTOS-DE-SPRINT-DA-F1.md)
- [Epic](../EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
- [Auditoria de Origem](../auditorias/RELATORIO-AUDITORIA-F1-R01.md)
