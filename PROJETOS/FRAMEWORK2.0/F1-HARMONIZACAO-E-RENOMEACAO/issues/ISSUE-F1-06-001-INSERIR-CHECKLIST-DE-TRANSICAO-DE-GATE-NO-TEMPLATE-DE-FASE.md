---
doc_id: "ISSUE-F1-06-001-INSERIR-CHECKLIST-DE-TRANSICAO-DE-GATE-NO-TEMPLATE-DE-FASE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-06-001 - Inserir checklist de transicao de gate no template de fase

## User Story

Como operador do framework, quero um checklist explicito no manifesto de fase
para saber quando mudar o gate sem depender de inferencia manual.

## Contexto Tecnico

Esta issue atualiza o template de fase dentro de `GOV-ISSUE-FIRST.md` para
incluir checklist verificavel de `not_ready -> pending -> hold/approved`.

## Plano TDD

- Red: localizar a ambiguidade atual de transicao de gate.
- Green: inserir checklist verificavel no template.
- Refactor: alinhar o checklist a `GOV-AUDITORIA.md`.

## Criterios de Aceitacao

- Given o template de fase, When for lido, Then existe checklist explicito de transicao de gate
- Given o checklist, When for comparado a `GOV-AUDITORIA.md`, Then os estados e evidencias sao coerentes

## Definition of Done da Issue

- [ ] checklist adicionado ao template de fase
- [ ] checklist coerente com a governanca de auditoria

## Tasks Decupadas

- [ ] T1: revisar estados de gate atuais
- [ ] T2: inserir checklist verificavel no template de fase
- [ ] T3: revisar consistencia com `GOV-AUDITORIA.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/GOV-AUDITORIA.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`

## Dependencias

- [Epic](../EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
