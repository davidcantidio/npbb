---
doc_id: "ISSUE-F3-03-002-VALIDAR-GUARDRAILS-DE-EXECUCAO-MATERIAL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-03-002 - Validar guardrails de execucao material

## User Story

Como mantenedor do framework, quero validar os guardrails de execucao material
para evitar que a sessao de implementacao vire um modo autonomo irrestrito.

## Contexto Tecnico

Esta issue revisa `SESSION-IMPLEMENTAR-ISSUE.md` com foco em confirmacoes de
gravacao, bloqueios por insumo ausente e respeito a `Instructions por Task`.

## Plano TDD

- Red: localizar pontos onde a sessao ainda poderia escrever ou concluir sem
  base suficiente.
- Green: registrar os guardrails faltantes.
- Refactor: revisar se o fluxo continua pragmatico e executavel.

## Criterios de Aceitacao

- Given a sessao de implementacao, When faltar uma issue bem formada, Then o
  prompt manda parar ou sinalizar bloqueio
- Given uma etapa de gravacao, When o fluxo for seguido, Then a confirmacao do
  PM e exigida
- Given issues com `task_instruction_mode: required`, When forem executadas,
  Then o prompt exige leitura e cumprimento das `Instructions por Task`

## Definition of Done da Issue

- [ ] guardrails de bloqueio registrados
- [ ] escrita material protegida por confirmacao
- [ ] respeito a `task_instruction_mode` validado

## Tasks Decupadas

- [ ] T1: revisar o prompt de implementacao em busca de lacunas
- [ ] T2: inserir guardrails de bloqueio e gravacao
- [ ] T3: revisar integracao com `Instructions por Task`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`

## Dependencias

- [Issue 001](./ISSUE-F3-03-001-REDIGIR-SESSION-IMPLEMENTAR-ISSUE-COM-LEITURA-MINIMA.md)
- [Epic](../EPIC-F3-03-SESSION-IMPLEMENTAR-ISSUE.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
