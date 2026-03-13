---
doc_id: "ISSUE-F3-02-001-REDIGIR-SESSION-CRIAR-PRD-COM-PASSAGENS-HITL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-02-001 - Redigir SESSION-CRIAR-PRD com passagens HITL

## User Story

Como PM, quero um prompt de sessao para gerar PRD a partir de intake aprovado
sem perder checkpoints de confirmacao humana.

## Contexto Tecnico

Esta issue cria o fluxo base de `SESSION-CRIAR-PRD.md`, articulando leitura
minima, checkpoints HITL e uso de `GOV-INTAKE.md`.

## Plano TDD

- Red: listar as passagens do fluxo onde confirmacao humana e obrigatoria.
- Green: redigir o prompt com etapas e checkpoints claros.
- Refactor: revisar aderencia ao gate `intake -> PRD`.

## Criterios de Aceitacao

- Given `SESSION-CRIAR-PRD.md`, When for lido, Then o fluxo parte de um intake
  aprovado e nao de contexto solto
- Given o prompt, When chegar a uma etapa de gravacao, Then a confirmacao do PM
  e exigida antes de qualquer escrita
- Given o gate `intake -> PRD`, When o prompt for seguido, Then a leitura
  canonica passa por `boot-prompt` e `GOV-INTAKE.md`

## Definition of Done da Issue

- [ ] sessao de criacao de PRD redigida
- [ ] checkpoints HITL explicitos
- [ ] gate canonico respeitado

## Tasks Decupadas

- [ ] T1: estruturar leitura minima do fluxo
- [ ] T2: redigir checkpoints HITL e criticos de gravacao
- [ ] T3: revisar aderencia ao gate de intake

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
- `PROJETOS/COMUM/GOV-INTAKE.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`

## Dependencias

- [Epic](../EPIC-F3-02-SESSION-CRIAR-PRD.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
