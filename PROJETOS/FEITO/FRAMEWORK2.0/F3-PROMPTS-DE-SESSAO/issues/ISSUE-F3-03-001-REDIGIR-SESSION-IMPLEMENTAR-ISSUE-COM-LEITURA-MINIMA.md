---
doc_id: "ISSUE-F3-03-001-REDIGIR-SESSION-IMPLEMENTAR-ISSUE-COM-LEITURA-MINIMA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-03-001 - Redigir SESSION-IMPLEMENTAR-ISSUE com leitura minima

## User Story

Como PM, quero uma sessao de execucao de issue que leia apenas o necessario e
preserve guardrails de implementacao orientada por issue.

## Contexto Tecnico

Esta issue cria `SESSION-IMPLEMENTAR-ISSUE.md`, conectando a leitura minima do
projeto, a issue alvo e as regras de materializacao segura.

## Plano TDD

- Red: listar leituras minimas necessarias para executar uma issue com contexto
  suficiente.
- Green: redigir a sessao com ordem de leitura e execucao.
- Refactor: revisar acoplamento com governanca de issue-first.

## Criterios de Aceitacao

- Given `SESSION-IMPLEMENTAR-ISSUE.md`, When for lido, Then a ordem minima de
  leitura fica explicita
- Given uma issue concreta, When a sessao for seguida, Then a execucao parte da
  issue e nao de exploracao aberta
- Given o fluxo de implementacao, When houver escrita material, Then os
  guardrails de confirmacao ficam claros

## Definition of Done da Issue

- [ ] sessao de implementacao redigida
- [ ] leitura minima explicita
- [ ] acoplamento a issue-first preservado

## Tasks Decupadas

- [ ] T1: definir a ordem minima de leitura
- [ ] T2: redigir o fluxo de execucao por issue
- [ ] T3: revisar guardrails de escrita

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`

## Dependencias

- [Epic](../EPIC-F3-03-SESSION-IMPLEMENTAR-ISSUE.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
