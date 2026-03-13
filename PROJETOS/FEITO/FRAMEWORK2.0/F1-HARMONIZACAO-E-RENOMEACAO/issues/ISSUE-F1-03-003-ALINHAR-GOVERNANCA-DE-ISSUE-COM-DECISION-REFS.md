---
doc_id: "ISSUE-F1-03-003-ALINHAR-GOVERNANCA-DE-ISSUE-COM-DECISION-REFS.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-03-003 - Alinhar governanca de issue com decision refs

## User Story

Como auditor do framework, quero ligar issues e auditorias a decisoes R2/R3 para
conseguir verificar aprovacoes estruturais sem buscar contexto fora do fluxo.

## Contexto Tecnico

Esta issue adiciona `decision_refs` ao template de issue e substitui a copia das
regras de task instructions por referencia a `SPEC-TASK-INSTRUCTIONS.md`.

## Plano TDD

- Red: localizar a ausencia de `decision_refs` e a duplicacao de regras.
- Green: atualizar o template de issue e a regra de scrum.
- Refactor: revisar rastreabilidade e nomes finais.

## Criterios de Aceitacao

- Given o template de issue, When for lido, Then existe campo opcional `decision_refs`
- Given `GOV-SCRUM.md`, When a secao de task instructions for lida, Then ela aponta para `SPEC-TASK-INSTRUCTIONS.md` em vez de copiar criterios

## Definition of Done da Issue

- [x] `decision_refs` incluido no template
- [x] duplicacao de regra de task instruction removida

## Tasks Decupadas

- [x] T1: atualizar template de issue em `GOV-ISSUE-FIRST.md`
- [x] T2: substituir copia de criterios em `GOV-SCRUM.md`
- [x] T3: revisar referencias finais

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/SPEC-TASK-INSTRUCTIONS.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`

## Dependencias

- [Issue 002](./ISSUE-F1-03-002-CONSOLIDAR-LEITURA-CANONICA-E-GATE-INTAKE-PARA-PRD.md)
- [Epic](../EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
