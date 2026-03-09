---
doc_id: "ISSUE-F1-03-001-DELIMITAR-RESPONSABILIDADES-ENTRE-MASTER-E-SCRUM.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F1-03-001 - Delimitar responsabilidades entre master e scrum

## User Story

Como operador do framework, quero saber qual documento trata do mapa geral e qual
trata das regras scrum para nao depender de leitura comparativa.

## Contexto Tecnico

Esta issue separa `GOV-FRAMEWORK-MASTER.md` e `GOV-SCRUM.md` por responsabilidade
sem duplicar gates ou regras detalhadas.

## Plano TDD

- Red: localizar sobreposicoes entre master e scrum.
- Green: delimitar claramente o escopo de cada arquivo.
- Refactor: remover duplicacoes residuais.

## Criterios de Aceitacao

- Given os dois documentos, When forem lidos, Then `GOV-FRAMEWORK-MASTER` funciona como mapa e `GOV-SCRUM` como regra de ciclo/DoD
- Given uma regra detalhada de intake ou auditoria, When for procurada, Then ela nao esta reescrita nos dois arquivos

## Definition of Done da Issue

- [ ] responsabilidades separadas
- [ ] duplicacoes principais removidas

## Tasks Decupadas

- [ ] T1: mapear sobreposicoes entre os dois documentos
- [ ] T2: mover ou substituir duplicacoes por referencias
- [ ] T3: revisar o resultado final

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-SCRUM.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`

## Dependencias

- [Epic](../EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
