---
doc_id: "ISSUE-F3-05-001-REDIGIR-SESSION-REFATORAR-MONOLITO-COMO-MINI-PROJETO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-05-001 - Redigir SESSION-REFATORAR-MONOLITO como mini projeto

## User Story

Como PM, quero uma sessao de refatoracao estrutural que trate um monolito como
mini-projeto guiado, com intake, planejamento e entrega incremental.

## Contexto Tecnico

Esta issue cria `SESSION-REFATORAR-MONOLITO.md`, usando o caminho de remediacao
como um projeto curto e controlado, e nao como patch ad hoc.

## Plano TDD

- Red: listar quais etapas minimas transformam um achado estrutural em plano de
  refatoracao guiado.
- Green: redigir o prompt com framing de mini-projeto.
- Refactor: revisar a compatibilidade com o restante do framework issue-first.

## Criterios de Aceitacao

- Given `SESSION-REFATORAR-MONOLITO.md`, When for lido, Then o fluxo trata a
  refatoracao estrutural como mini-projeto
- Given um intake vindo do prompt de monolito, When a sessao for seguida, Then
  ela indica os passos para PRD enxuto, fases e implementacao
- Given o fluxo de sessao, When houver escrita material, Then ha checkpoints de
  confirmacao do PM

## Definition of Done da Issue

- [ ] sessao de refatoracao estrutural redigida
- [ ] framing de mini-projeto explicito
- [ ] checkpoints HITL presentes

## Tasks Decupadas

- [ ] T1: definir o framing de mini-projeto
- [ ] T2: redigir o fluxo de refatoracao guiada
- [ ] T3: revisar compatibilidade com issue-first

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`
- `PROJETOS/COMUM/PROMPT-MONOLITO-PARA-INTAKE.md`
- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-REFATORAR-MONOLITO.md`

## Dependencias

- [Epic](../EPIC-F3-05-SESSION-REFATORAR-MONOLITO.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [F2](../../F2-ANTI-MONOLITH-ENFORCEMENT/F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
