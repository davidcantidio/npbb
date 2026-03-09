---
doc_id: "ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-05-001 - Documentar regra operacional de backfilled em GOV-INTAKE

## User Story

Como PM, quero uma regra clara para `source_mode: backfilled` para que intakes
retroativos nao dependam de improviso.

## Contexto Tecnico

O PRD identificou que `backfilled` existia na taxonomia sem regra operacional.
Esta issue fecha contexts validos, campos obrigatorios e relacao com o gate.

## Plano TDD

- Red: localizar a lacuna do `backfilled`.
- Green: documentar origem, campos minimos e gate.
- Refactor: alinhar a linguagem ao template de intake e aos prompts.

## Criterios de Aceitacao

- Given `GOV-INTAKE.md`, When a secao de backfilled for lida, Then contexts validos de origem estao declarados
- Given o mesmo documento, When a regra for consultada, Then fica claro que o gate `Intake -> PRD` continua valendo integralmente

## Definition of Done da Issue

- [ ] secao de backfilled criada
- [ ] gate para backfill explicitado

## Tasks Decupadas

- [ ] T1: definir contexts validos de origem
- [ ] T2: definir campos minimos obrigatorios em backfill
- [ ] T3: revisar o gate com a nova secao

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-INTAKE.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-INTAKE.md`

## Dependencias

- [Epic](../EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
