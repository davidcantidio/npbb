---
doc_id: "ISSUE-F3-04-002-INTEGRAR-REMEDIACAO-ANTI-MONOLITO-E-AUDIT-LOG.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-04-002 - Integrar remediacao anti monolito e atualizacao de audit log

## User Story

Como auditor do framework, quero que a sessao de auditoria saiba abrir o
caminho de remediacao estrutural e atualizar o audit log sem improviso.

## Contexto Tecnico

Esta issue fecha o fluxo de follow-up da `SESSION-AUDITAR-FASE.md`. Quando a
auditoria detectar um monolito acima de threshold, a sessao deve propor o uso
de `PROMPT-MONOLITO-PARA-INTAKE.md`, orientar o handoff e so entao permitir a
gravacao controlada de relatorio e `AUDIT-LOG.md`.

## Plano TDD

- Red: localizar o gap entre achar monolito e acionar remediacao documentada.
- Green: integrar o caminho de remediacao e update de audit log na sessao.
- Refactor: revisar se os pontos de confirmacao cobrem toda escrita material.

## Criterios de Aceitacao

- Given um achado estrutural acima de threshold, When a sessao de auditoria for
  seguida, Then ela propoe o caminho para `PROMPT-MONOLITO-PARA-INTAKE.md`
- Given a proposta de remediacao, When o PM confirmar o prosseguimento, Then o
  fluxo orienta o handoff sem gravar automaticamente novos artefatos
- Given a auditoria concluida, When houver confirmacao de escrita, Then o
  relatorio e o `AUDIT-LOG.md` podem ser atualizados de forma controlada

## Definition of Done da Issue

- [ ] remediacao anti-monolito integrada a sessao de auditoria
- [ ] update de audit log documentado no fluxo
- [ ] escrita material protegida por confirmacao explicita

## Tasks Decupadas

- [ ] T1: integrar o caminho de remediacao estrutural ao prompt de auditoria
- [ ] T2: explicitar o update controlado de relatorio e `AUDIT-LOG.md`
- [ ] T3: validar os pontos de parada e confirmacao

## Instructions por Task

### T1
- objetivo: conectar achado de monolito ao fluxo de remediacao rastreavel
- precondicoes: `SESSION-AUDITAR-FASE.md`, `SPEC-ANTI-MONOLITO.md` e `PROMPT-MONOLITO-PARA-INTAKE.md` existentes
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
  - `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
  - `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- passos_atomicos:
  1. localizar na sessao de auditoria o momento em que um achado estrutural vira follow-up
  2. inserir uma regra explicita para consultar o `SPEC-ANTI-MONOLITO.md` antes de classificar o caso como remediacao estrutural
  3. orientar o operador a propor o uso de `PROMPT-MONOLITO-PARA-INTAKE.md` somente quando o threshold estiver acima de `warn` ou `block`, conforme o caso
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: sessao com caminho claro de remediacao estrutural rastreavel
- testes_ou_validacoes_obrigatorias:
  - `rg -n "PROMPT-MONOLITO-PARA-INTAKE|SPEC-ANTI-MONOLITO" PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- stop_conditions:
  - parar se a sessao exigir um artefato de follow-up nao previsto no PRD

### T2
- objetivo: garantir que relatorio e audit log so sejam atualizados com confirmacao
- precondicoes: T1 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
  - `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
  - `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`
- passos_atomicos:
  1. explicitar no prompt que o relatorio so pode ser gravado apos confirmacao do PM
  2. explicitar no prompt que `AUDIT-LOG.md` so pode ser atualizado apos confirmacao separada ou conjunta, mas sempre explicita
  3. registrar o conteudo minimo do update de audit log: rodada, veredito, gate e referencia ao relatorio
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: escrita de relatorio e log protegida por checkpoints HITL
- testes_ou_validacoes_obrigatorias:
  - `rg -n "AUDIT-LOG|confirm" PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- stop_conditions:
  - parar se o fluxo exigir escrita automatica sem possibilidade de aprovacao humana

### T3
- objetivo: validar guardrails do fluxo final de auditoria com follow-up estrutural
- precondicoes: T2 concluida
- arquivos_a_ler_ou_tocar:
  - `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
  - `PROJETOS/COMUM/GOV-AUDITORIA.md`
  - `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- passos_atomicos:
  1. revisar se a sessao para quando faltar insumo para classificar monolito
  2. revisar se a sessao nao grava artefatos nem abre intake sem confirmacao
  3. revisar coerencia entre veredito, log e caminho de remediacao
- comandos_permitidos:
  - `rg`
  - `apply_patch`
- resultado_esperado: fluxo final coerente, bloqueavel e rastreavel
- testes_ou_validacoes_obrigatorias:
  - `rg -n "parar|BLOQUEADO|confirmacao|PROMPT-MONOLITO-PARA-INTAKE" PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- stop_conditions:
  - parar se faltar regra normativa no PRD para decidir entre auditoria simples e remediacao estrutural

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-LOG.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

## Dependencias

- [Issue 001](./ISSUE-F3-04-001-REDIGIR-SESSION-AUDITAR-FASE-COM-FLUXO-HITL.md)
- [Epic](../EPIC-F3-04-SESSION-AUDITAR-FASE.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [F2](../../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
