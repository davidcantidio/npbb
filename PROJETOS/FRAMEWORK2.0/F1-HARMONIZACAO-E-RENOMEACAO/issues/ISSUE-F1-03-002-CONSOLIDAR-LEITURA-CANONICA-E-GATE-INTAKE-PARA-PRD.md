---
doc_id: "ISSUE-F1-03-002-CONSOLIDAR-LEITURA-CANONICA-E-GATE-INTAKE-PARA-PRD.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-03-002 - Consolidar leitura canonica e gate intake para PRD

## User Story

Como PM, quero prompts canonicos apontando para uma ordem de leitura unica e um
gate unico de intake para PRD para evitar drift silencioso.

## Contexto Tecnico

Esta issue centraliza o gate em `GOV-INTAKE.md` e faz `PROMPT-INTAKE-PARA-PRD.md`
e `PROMPT-AUDITORIA.md` apontarem para `boot-prompt.md` em vez de manter listas paralelas.

## Plano TDD

- Red: localizar listas paralelas e gates duplicados.
- Green: apontar prompts para a leitura unica e mover o gate para `GOV-INTAKE`.
- Refactor: revisar linguagem e referencias.

## Criterios de Aceitacao

- Given `PROMPT-INTAKE-PARA-PRD` e `PROMPT-AUDITORIA`, When forem lidos, Then apontam para `boot-prompt.md` e para referencias adicionais minimas
- Given o gate `Intake -> PRD`, When for procurado, Then a fonte unica e `GOV-INTAKE.md`

## Definition of Done da Issue

- [ ] prompts sem listas paralelas desnecessarias
- [ ] gate consolidado em `GOV-INTAKE.md`

## Tasks Decupadas

- [ ] T1: mapear duplicacoes de leitura e gate
- [ ] T2: ajustar prompts para o ponteiro unico
- [ ] T3: revisar `GOV-INTAKE.md` como fonte unica

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-INTAKE.md`
- `PROJETOS/COMUM/PROMPT-INTAKE-PARA-PRD.md`
- `PROJETOS/COMUM/PROMPT-AUDITORIA.md`
- `PROJETOS/boot-prompt.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-INTAKE.md`

## Dependencias

- [Issue 001](./ISSUE-F1-03-001-DELIMITAR-RESPONSABILIDADES-ENTRE-MASTER-E-SCRUM.md)
- [Epic](../EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
