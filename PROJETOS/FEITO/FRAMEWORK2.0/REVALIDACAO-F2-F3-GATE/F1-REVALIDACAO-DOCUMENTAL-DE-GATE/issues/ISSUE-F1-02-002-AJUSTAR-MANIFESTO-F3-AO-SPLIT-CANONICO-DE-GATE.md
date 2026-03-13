---
doc_id: "ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-10"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-02-002 - Ajustar manifesto F3 ao split canonico de gate

## User Story

Como mantenedor do sibling `REVALIDACAO-F2-F3-GATE`, quero ajustar o manifesto
de F3 apenas no split canonico de checklist/gate para remover o drift
documental sem mexer em qualquer outra parte da fase.

## Contexto Tecnico

Esta issue espelha a logica de F2, mas aplicada ao manifesto
`F3_FRAMEWORK2_0_EPICS.md`. A baseline deve dizer se F3 exige patch minimo ou
no-op controlado. O resultado precisa preservar integralmente `status`,
`audit_gate`, `gate_atual`, `ultima_auditoria`, backlog funcional e dependencia
entre epicos do projeto principal.

## Plano TDD

- Red: confirmar a classificacao de F3 na baseline e isolar o trecho permitido de edicao
- Green: aplicar o patch minimo ou registrar no-op controlado
- Refactor: validar que nenhum campo fora de checklist/gate foi alterado

## Criterios de Aceitacao

- Given a baseline classifica F3 como `drift confirmado`, When a issue for executada, Then o checklist de F3 passa a ter ramos separados `pending -> hold` e `pending -> approved`
- Given a baseline classifica F3 como `no-op controlado`, When a issue for executada, Then nenhum patch e aplicado e o resultado fica registrado explicitamente
- Given surgir divergencia fora de checklist/gate, When ela for detectada, Then a issue responde `BLOQUEADO` antes de tocar qualquer outra secao do manifesto

## Definition of Done da Issue

- [x] F3 foi tratada como patch minimo ou no-op controlado
- [x] nenhum campo fora de checklist/gate foi alterado
- [x] `status`, `audit_gate`, `gate_atual` e `ultima_auditoria` permaneceram preservados
- [x] existe stop condition explicita para drift fora do escopo

## Tasks Decupadas

- [x] T1: confirmar na baseline se F3 exige patch ou no-op
- [x] T2: aplicar o patch minimo em F3 ou registrar no-op controlado
- [x] T3: validar que nao houve alteracao fora de checklist/gate

## Instructions por Task

### T1
- objetivo: usar a baseline para determinar exatamente o que esta issue pode tocar em F3
- precondicoes:
  - [Issue de Baseline](./ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md) concluida
  - classificacao de F3 explicitada como `drift confirmado` ou `no-op controlado`
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
  - `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md`
- passos_atomicos:
  1. localizar na baseline a classificacao final de F3
  2. identificar no manifesto F3 o bloco exato de checklist/gate que a issue pode tocar
  3. confirmar que nao existe necessidade de alterar nenhum campo fora desse bloco
- comandos_permitidos:
  - `sed`
  - `rg`
- resultado_esperado: faixa de edicao de F3 delimitada antes de qualquer patch
- testes_ou_validacoes_obrigatorias:
  - `rg -n "F3|drift confirmado|no-op controlado|BLOQUEADO" PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
- stop_conditions:
  - parar se a baseline nao delimitar claramente o trecho de checklist/gate
  - parar se F3 exigir alteracao de `status`, `audit_gate`, `gate_atual` ou `ultima_auditoria`

### T2
- objetivo: aplicar apenas o patch minimo em F3 ou registrar no-op controlado
- precondicoes:
  - T1 concluida
  - faixa de edicao de F3 delimitada
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md`
- passos_atomicos:
  1. se a baseline indicar `drift confirmado`, substituir em F3 a forma agregada `pending -> hold/approved` pelos blocos canonicos separados
  2. se a baseline indicar `no-op controlado`, registrar explicitamente na issue que nenhum patch foi necessario
  3. nao tocar em epicos, dependencias, escopo, DoD, `status` ou campos de estado da fase
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: F3 corrigida apenas no checklist/gate ou issue encerrada como no-op controlado
- testes_ou_validacoes_obrigatorias:
  - `rg -n "pending -> hold|pending -> approved|pending -> hold/approved" PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
- stop_conditions:
  - parar se o patch precisar alterar qualquer secao fora de checklist/gate
  - parar se for necessario criar relatorio de auditoria ou atualizar `AUDIT-LOG.md`

### T3
- objetivo: comprovar que a issue nao introduziu alteracoes indevidas em F3
- precondicoes:
  - T2 concluida
  - resultado final de patch ou no-op definido
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
  - `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-02-002-AJUSTAR-MANIFESTO-F3-AO-SPLIT-CANONICO-DE-GATE.md`
- passos_atomicos:
  1. verificar que `status`, `audit_gate`, `gate_atual` e `ultima_auditoria` continuam iguais ao estado de entrada
  2. verificar que apenas o bloco de checklist/gate foi alterado quando houve patch
  3. registrar na issue o resultado final como `patch minimo` ou `no-op controlado`
- comandos_permitidos:
  - `sed`
  - `rg`
  - `apply_patch`
- resultado_esperado: validacao final de que F3 permaneceu em estado pre-auditoria e sem drift adicional introduzido
- testes_ou_validacoes_obrigatorias:
  - `rg -n "^status:|^audit_gate:|gate_atual:|ultima_auditoria:|pending -> hold|pending -> approved" PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
- stop_conditions:
  - parar se a validacao revelar drift fora do escopo aprovado
  - parar se a issue depender de reinterpretar a prontidao operacional de F3

## Resultado da Execucao

- classificacao final: `patch minimo`
- baseline consumida: F3 classificada como `drift confirmado` em `ISSUE-F1-01-001`
- alteracao aplicada: split de `pending -> hold/approved` para `pending -> hold` e `pending -> approved` em `F3_FRAMEWORK2_0_EPICS.md`
- validacao final: `status`, `audit_gate`, `gate_atual` e `ultima_auditoria` permaneceram preservados, e o diff ficou restrito ao bloco de checklist/gate
- stop condition mantida: qualquer drift fora de checklist/gate permanece `BLOQUEADO`

## Arquivos Reais Envolvidos

- `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`
- `PROJETOS/FRAMEWORK2.0/REVALIDACAO-F2-F3-GATE/F1-REVALIDACAO-DOCUMENTAL-DE-GATE/issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md`
- `PROJETOS/FRAMEWORK2.0/PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md`

## Artifact Minimo

- `PROJETOS/FRAMEWORK2.0/F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md`

## Dependencias

- [Issue de Baseline](./ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md)
- [Epic](../EPIC-F1-02-CORRECAO-DOCUMENTAL-MINIMA-DE-GATE.md)
- [Fase](../F1_REVALIDACAO_F2_F3_GATE_EPICS.md)
- [F3](../../../F3-PROMPTS-DE-SESSAO/F3_FRAMEWORK2_0_EPICS.md)
- [PRD Derivado](../../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md)
