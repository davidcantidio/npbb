---
doc_id: "ISSUE-F1-06-002-RECONCILIAR-STATUS-DE-EPICOS-ISSUES-E-MANIFESTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-10"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-06-002 - Reconciliar status de epicos, issues e manifesto

## User Story

Como mantenedor do FRAMEWORK2.0, quero reconciliar os status documentais de
`EPIC-F1-04`, `EPIC-F1-05`, `EPIC-F1-06`, `ISSUE-F1-04-001`,
`ISSUE-F1-04-002`, `ISSUE-F1-05-001` e `F1_FRAMEWORK2_0_EPICS.md` com as
evidencias ja implementadas para que a leitura do gate da F1 volte a refletir o
estado material real antes da proxima auditoria.

## Contexto Tecnico

A auditoria `RELATORIO-AUDITORIA-F1-R01.md` registrou `hold` porque o commit
auditado apresentava drift entre entrega material e status documental. O
relatorio aponta evidencias objetivas ja implementadas em:

- `PROJETOS/COMUM/GOV-DECISOES.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`

Esta issue cobre apenas a reconciliacao documental desses artefatos com os
manifestos e issues da F1. Nao inclui normalizacao das sprints nem atualizacao
do `AUDIT-LOG.md`, que seguem como follow-ups separados do mesmo `hold`.

## Plano TDD

- Red: localizar, arquivo a arquivo, quais status/DoD/tabelas ainda divergem das
  evidencias explicitamente citadas pela auditoria.
- Green: ajustar frontmatter, tabelas e checklists somente onde o relatorio
  sustenta a conclusao material da entrega.
- Refactor: validar se a derivacao de status entre issue, epic e fase ficou
  coerente, sem promover gate nem ampliar escopo.

## Criterios de Aceitacao

- Given `EPIC-F1-04`, `EPIC-F1-05`, `EPIC-F1-06` e
  `F1_FRAMEWORK2_0_EPICS.md`, When forem lidos apos a correcao, Then seus
  status e tabelas refletem as evidencias materiais citadas em `F1-R01`.
- Given `ISSUE-F1-04-001`, `ISSUE-F1-04-002` e `ISSUE-F1-05-001`, When forem
  consultadas, Then frontmatter, DoD e tasks estao coerentes com o estado
  efetivamente entregue e auditado.
- Given esta reconciliacao, When a fase F1 for consultada, Then o gate continua
  em `hold` com `ultima_auditoria: F1-R01` ate os demais follow-ups bloqueantes
  serem concluidos.
- Given qualquer ponto sem evidencia suficiente no relatorio, When a execucao
  encontrar esse caso, Then o agente para e reporta bloqueio em vez de marcar
  `done` por inferencia.

## Definition of Done da Issue

- [ ] `ISSUE-F1-04-001`, `ISSUE-F1-04-002` e `ISSUE-F1-05-001` reconciliadas
      com as evidencias auditadas
- [ ] `EPIC-F1-04`, `EPIC-F1-05`, `EPIC-F1-06` reconciliadas com o estado das
      issues filhas e com as evidencias ja implementadas
- [ ] `F1_FRAMEWORK2_0_EPICS.md` coerente com o estado material real da fase no
      escopo desta issue
- [ ] nenhum arquivo deste escopo permanece com drift documental apontado pelo
      follow-up bloqueante B1

## Tasks Decupadas

- [ ] T1: consolidar a matriz de evidencias e o status-alvo de cada artefato do
      escopo B1
- [ ] T2: reconciliar `ISSUE-F1-04-001`, `ISSUE-F1-04-002` e
      `ISSUE-F1-05-001` com as evidencias ja implementadas
- [ ] T3: reconciliar `EPIC-F1-04`, `EPIC-F1-05`, `EPIC-F1-06` e
      `F1_FRAMEWORK2_0_EPICS.md` com o estado atualizado das issues
- [ ] T4: validar coerencia final de status, DoD e gate dentro do escopo desta
      issue

## Instructions por Task

### T1
- objetivo: mapear o que a auditoria efetivamente comprovou para cada artefato
  do follow-up B1
- precondicoes:
  - `RELATORIO-AUDITORIA-F1-R01.md` lido integralmente
  - entendimento claro de que esta issue nao cobre sprints nem `AUDIT-LOG.md`
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
  - `PROJETOS/COMUM/GOV-DECISOES.md`
  - `PROJETOS/COMUM/GOV-INTAKE.md`
  - `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
  - `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
  - `PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`
- passos_atomicos:
  1. listar cada evidencia material citada no relatorio para F1-04, F1-05 e F1-06
  2. associar cada evidencia ao artefato documental que precisa refletir esse
     estado
  3. registrar qual status/checklist/tabela pode ser alterado sem inferencia
     extra
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: matriz objetiva ligando evidencias auditadas aos ajustes
  documentais permitidos
- testes_ou_validacoes_obrigatorias:
  - `rg -n "PROMPT-PLANEJAR-FASE|backfilled|Checklist de Transicao de Gate|decision_refs" PROJETOS/COMUM/GOV-DECISOES.md PROJETOS/COMUM/GOV-INTAKE.md PROJETOS/COMUM/GOV-ISSUE-FIRST.md PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`
- stop_conditions:
  - parar se alguma conclusao depender de evidencia nao citada no relatorio
  - parar se houver contradicao entre o relatorio e os artefatos fonte

### T2
- objetivo: corrigir o drift nas issues diretamente apontadas pelo follow-up B1
- precondicoes:
  - T1 concluida
  - status-alvo de cada issue definido sem ambiguidade
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md`
- passos_atomicos:
  1. atualizar apenas frontmatter, DoD, tasks e texto estritamente necessarios
     para refletir a entrega material comprovada
  2. preservar rastreabilidade existente, incluindo `decision_refs` onde ja
     houver referencia documentada
  3. nao marcar como concluido nenhum item que a auditoria nao tenha sustentado
     explicitamente
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: tres issues coerentes com o estado entregue e sem drift
  interno
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^task_instruction_mode:|^decision_refs:|^- \\[|^## Definition of Done da Issue" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md`
- stop_conditions:
  - parar se alguma issue exigir reabrir escopo funcional alem do follow-up B1
  - parar se uma issue depender de alterar sprint ou `AUDIT-LOG.md` para ficar
    coerente

### T3
- objetivo: alinhar os epicos e o manifesto da fase ao estado reconciliado das
  issues e as evidencias auditadas
- precondicoes:
  - T2 concluida
  - issues alvo sem drift interno
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- passos_atomicos:
  1. atualizar status e DoD dos epicos somente conforme o estado efetivo das
     issues filhas e das evidencias comprovadas
  2. corrigir a tabela de epicos da fase para refletir o novo estado material
  3. manter `audit_gate: hold`, `gate_atual: hold` e `ultima_auditoria: F1-R01`
     no manifesto da fase
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: epicos e manifesto F1 coerentes com o estado reconciliado
  sem promover o gate indevidamente
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^audit_gate:|gate_atual:|ultima_auditoria:|^\\| EPIC-F1-0[456] " PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- stop_conditions:
  - parar se o manifesto da fase so puder ficar coerente com alteracao de
    sprint ou `AUDIT-LOG.md`
  - parar se o estado derivado de algum epic conflitar com o estado real das
    issues filhas

### T4
- objetivo: validar que o drift do follow-up B1 foi removido sem contaminar
  outros follow-ups do hold
- precondicoes:
  - T3 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md`
- passos_atomicos:
  1. revisar se status de issues, epicos e fase obedecem a derivacao canonica de
     `GOV-SCRUM.md`
  2. confirmar que nenhum artefato do escopo B1 permaneceu como `todo` ou `done`
     em desacordo com as evidencias ja implementadas
  3. registrar no fechamento da issue que a auditoria de origem continua em
     `hold` ate os follow-ups B2 e B3 serem tratados
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: B1 encerrado com coerencia documental local e sem falso
  fechamento do gate
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^audit_gate:|gate_atual:|ultima_auditoria:" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md`
- stop_conditions:
  - parar se a validacao final apontar follow-up adicional nao descrito no
    relatorio
  - parar se houver necessidade de promover `hold -> approved` nesta mesma issue

## Arquivos Reais Envolvidos

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/F1_FRAMEWORK2_0_EPICS.md`

## Dependencias

- [Epic](../EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
- [Auditoria de Origem](../auditorias/RELATORIO-AUDITORIA-F1-R01.md)
