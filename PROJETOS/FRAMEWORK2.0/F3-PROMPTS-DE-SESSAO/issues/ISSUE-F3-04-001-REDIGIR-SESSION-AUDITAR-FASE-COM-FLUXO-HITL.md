---
doc_id: "ISSUE-F3-04-001-REDIGIR-SESSION-AUDITAR-FASE-COM-FLUXO-HITL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-04-001 - Redigir SESSION-AUDITAR-FASE com fluxo HITL

## User Story

Como PM, quero um prompt de auditoria de fase com checkpoints HITL para conduzir
achados, veredito e validacao de escrita em uma sessao unica.

## Contexto Tecnico

Esta issue cria o fluxo base de `SESSION-AUDITAR-FASE.md`, articulando leitura
da fase, relatorio, audit log e proposta de veredito.

## Plano TDD

- Red: mapear as decisoes da sessao onde o PM precisa confirmar o proximo passo.
- Green: redigir o fluxo base com checkpoints HITL.
- Refactor: revisar a aderencia a `GOV-AUDITORIA.md`.

## Criterios de Aceitacao

- Given `SESSION-AUDITAR-FASE.md`, When for lido, Then existe fluxo claro para
  leitura, analise, proposta de veredito e escrita controlada
- Given a sessao, When chegar em gravacao de relatorio ou audit log, Then a
  confirmacao do PM e obrigatoria
- Given uma fase em auditoria, When o prompt for seguido, Then `GOV-AUDITORIA`
  e o template de relatorio sao usados como base

## Definition of Done da Issue

- [ ] sessao de auditoria base redigida
- [ ] checkpoints HITL explicitos
- [ ] acoplamento com governanca de auditoria preservado

## Tasks Decupadas

- [ ] T1: estruturar leitura minima da fase e da governanca
- [ ] T2: redigir checkpoints HITL do fluxo de auditoria
- [ ] T3: revisar pontos de escrita controlada

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`
- `PROJETOS/COMUM/GOV-AUDITORIA.md`
- `PROJETOS/COMUM/TEMPLATE-AUDITORIA-RELATORIO.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-AUDITAR-FASE.md`

## Dependencias

- [Epic](../EPIC-F3-04-SESSION-AUDITAR-FASE.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
