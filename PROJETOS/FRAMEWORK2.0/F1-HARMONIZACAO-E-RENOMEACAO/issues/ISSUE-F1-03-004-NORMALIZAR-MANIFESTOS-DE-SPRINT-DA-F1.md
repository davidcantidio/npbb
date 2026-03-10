---
doc_id: "ISSUE-F1-03-004-NORMALIZAR-MANIFESTOS-DE-SPRINT-DA-F1.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-10"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-03-004 - Normalizar manifestos de sprint da F1

## User Story

Como mantenedor do FRAMEWORK2.0, quero que `SPRINT-F1-01.md`,
`SPRINT-F1-02.md` e `SPRINT-F1-03.md` reflitam apenas as issues realmente
selecionadas e seus status reais para que a descoberta da unidade elegivel e a
leitura historica da F1 deixem de depender de inferencia manual.

## Contexto Tecnico

A auditoria `RELATORIO-AUDITORIA-F1-R01.md` apontou `architecture-drift` de
severidade `medium` porque os manifestos de sprint da F1 permaneciam
`active/todo` com linhas de issue desatualizadas. O relatorio cita
explicitamente:

- `SPRINT-F1-01.md`
- `SPRINT-F1-02.md`
- `SPRINT-F1-03.md`

Esta issue cobre apenas a normalizacao documental desses manifestos, mantendo a
sprint como artefato de selecao operacional conforme `GOV-SPRINT-LIMITES.md`.
Nao inclui reconciliacao de issues/epicos/manisfesto da fase nem atualizacao do
`AUDIT-LOG.md`, que seguem como follow-ups separados do mesmo `hold`.

## Plano TDD

- Red: comparar cada manifesto de sprint com o estado real das issues
  selecionadas e localizar linhas/status em drift.
- Green: atualizar tabelas, status da sprint e encerramento para refletir a
  selecao e o estado material real.
- Refactor: revisar se os manifestos permanecem enxutos e aderentes ao formato
  canonico de sprint.

## Criterios de Aceitacao

- Given `SPRINT-F1-01.md`, `SPRINT-F1-02.md` e `SPRINT-F1-03.md`, When forem
  consultados apos a correcao, Then cada um lista apenas issues realmente
  selecionadas e com status coerente com os artefatos da F1.
- Given os manifestos de sprint atualizados, When forem comparados a
  `GOV-SPRINT-LIMITES.md`, Then continuam contendo apenas objetivo, capacidade,
  tabela de issues, riscos/bloqueios e encerramento.
- Given a F1 permanece em `hold`, When os manifestos forem lidos, Then nenhum
  deles sugere erroneamente que ainda existe issue `todo/active` ja concluida ou
  sprint aberta sem evidencia.
- Given alguma sprint nao tenha evidencia suficiente para confirmar selecao ou
  encerramento, When a execucao encontrar esse caso, Then o agente para e
  reporta bloqueio em vez de inventar status.

## Definition of Done da Issue

- [x] `SPRINT-F1-01.md` normalizada com base no estado real das issues
      selecionadas
- [x] `SPRINT-F1-02.md` normalizada com base no estado real das issues
      selecionadas
- [x] `SPRINT-F1-03.md` normalizada com base no estado real das issues
      selecionadas
- [x] status e encerramento das sprints coerentes com a governanca canonica e
      com o `hold` vigente da F1

## Tasks Decupadas

- [x] T1: levantar o conjunto real de issues selecionadas e seus status por
      sprint
- [x] T2: normalizar `SPRINT-F1-01.md` e `SPRINT-F1-02.md`
- [x] T3: normalizar `SPRINT-F1-03.md`
- [x] T4: validar aderencia final dos tres manifestos ao formato canonico de
      sprint

## Instructions por Task

### T1
- objetivo: mapear o estado real das issues que cada sprint F1 deveria refletir
- precondicoes:
  - `RELATORIO-AUDITORIA-F1-R01.md` lido integralmente
  - entendimento claro de que esta issue nao reconcilia epicos, fase ou
    `AUDIT-LOG.md`
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/auditorias/RELATORIO-AUDITORIA-F1-R01.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/`
- passos_atomicos:
  1. listar as issues presentes em cada sprint
  2. comparar o status de cada linha com o status real do arquivo da issue
  3. marcar quais linhas podem ser mantidas, ajustadas ou removidas com base em
     evidencia documental
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: matriz objetiva por sprint com issues selecionadas e
  status reais
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-*.md`
- stop_conditions:
  - parar se alguma sprint exigir inferir selecao sem evidencia documental
  - parar se o estado real das issues depender primeiro de outra remediacao nao
    concluida

### T2
- objetivo: corrigir o drift documental em `SPRINT-F1-01.md` e `SPRINT-F1-02.md`
- precondicoes:
  - T1 concluida
  - status reais das issues dessas sprints conhecidos
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md`
- passos_atomicos:
  1. atualizar a coluna `Status` de cada issue para o estado real documentado
  2. ajustar `status:` do frontmatter e `Encerramento` de cada sprint para
     refletir a realidade documental
  3. remover somente linhas sem evidencia de selecao real, se esse caso estiver
     objetivamente demonstrado
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: `SPRINT-F1-01.md` e `SPRINT-F1-02.md` coerentes com suas
  issues e sem status stale
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^\\| ISSUE-F1-" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md`
- stop_conditions:
  - parar se a normalizacao exigir alterar escopo, capacidade ou objetivo de
    sprint sem evidencia no relatorio
  - parar se o encerramento da sprint depender de promover gate da fase

### T3
- objetivo: corrigir o drift documental em `SPRINT-F1-03.md`
- precondicoes:
  - T2 concluida
  - issues de `SPRINT-F1-03.md` com status reais confirmados
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-03-001-DELIMITAR-RESPONSABILIDADES-ENTRE-MASTER-E-SCRUM.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-03-002-CONSOLIDAR-LEITURA-CANONICA-E-GATE-INTAKE-PARA-PRD.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-03-003-ALINHAR-GOVERNANCA-DE-ISSUE-COM-DECISION-REFS.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/issues/ISSUE-F1-06-001-INSERIR-CHECKLIST-DE-TRANSICAO-DE-GATE-NO-TEMPLATE-DE-FASE.md`
- passos_atomicos:
  1. alinhar as linhas de issue ao estado real documentado
  2. ajustar o `status:` da sprint e o bloco `Encerramento` para refletir o
     resultado material da sprint
  3. preservar a sprint como artefato historico de selecao, sem duplicar DoD ou
     criterios das issues
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: `SPRINT-F1-03.md` sem drift e coerente com o fechamento
  documental da sprint
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^\\| ISSUE-F1-03-001|^\\| ISSUE-F1-03-002|^\\| ISSUE-F1-03-003|^\\| ISSUE-F1-06-001" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`
- stop_conditions:
  - parar se for necessario reabrir issue ja concluida sem evidencia no
    relatorio
  - parar se a sprint depender de reconciliacao fora do seu proprio escopo para
    ficar coerente

### T4
- objetivo: validar que os tres manifestos de sprint ficaram aderentes ao
  formato canonico e ao estado real da F1
- precondicoes:
  - T3 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/GOV-SPRINT-LIMITES.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md`
  - `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`
- passos_atomicos:
  1. revisar se os tres manifestos mantem apenas as secoes canonicas de sprint
  2. confirmar que os status das sprints e das linhas de issue batem com os
     artefatos reais
  3. registrar no fechamento da issue que esta remediacao nao fecha o `hold`
     sozinha e depende dos demais follow-ups bloqueantes
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: tres sprints coerentes, enxutas e prontas para leitura
  historica sem ambiguidade
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^## (Objetivo da Sprint|Capacidade|Issues Selecionadas|Riscos e Bloqueios|Encerramento)$" PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`
- stop_conditions:
  - parar se a validacao final revelar follow-up novo nao descrito no relatorio
  - parar se houver necessidade de editar epicos, fase ou `AUDIT-LOG.md` nesta
    mesma issue

## Arquivos Reais Envolvidos

## Encerramento

- decisao: concluida
- observacoes: a validacao documental confirmou que `SPRINT-F1-01.md`,
  `SPRINT-F1-02.md` e `SPRINT-F1-03.md` ja estavam coerentes com o estado real
  das issues e com o formato canonico de sprint; esta remediacao fecha apenas o
  follow-up B2 e nao substitui os follow-ups remanescentes
  `ISSUE-F1-06-002` e `ISSUE-F1-06-003`

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-01.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-02.md`
- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/F1-HARMONIZACAO-E-RENOMEACAO/sprints/SPRINT-F1-03.md`

## Dependencias

- [Issue Dependente](./ISSUE-F1-06-002-RECONCILIAR-STATUS-DE-EPICOS-ISSUES-E-MANIFESTO.md)
- [Epic](../EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
- [Auditoria de Origem](../auditorias/RELATORIO-AUDITORIA-F1-R01.md)
