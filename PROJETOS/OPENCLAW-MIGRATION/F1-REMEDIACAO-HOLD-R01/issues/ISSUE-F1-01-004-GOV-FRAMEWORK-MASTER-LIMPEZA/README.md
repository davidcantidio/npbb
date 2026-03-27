---
doc_id: "ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA"
version: "1.2"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
task_instruction_mode: "required"
decision_refs:
  - "PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md#follow-ups-bloqueantes"
---

# ISSUE-F1-01-004 - GOV-FRAMEWORK-MASTER limpeza

## User Story

Como agente que le o mapa mestre do repositório, quero que `GOV-FRAMEWORK-MASTER.md` nao declare `issue-first` nem arquitectura de fase como padrao actual, para que o documento reflita Feature > User Story > Task salvo compatibilidade explicitamente marcada como deprecated.

## Feature de Origem

- **Feature**: Feature 1 (Documentos de Governanca Centrais)
- **Comportamento coberto**: Follow-up B4 / ACHADO A-04 — limpeza de `issue-first` e referencias a fase fora de contexto `deprecated`.

## Contexto Tecnico

O relatorio cita linhas 57-60 com persistencia de `issue-first` e arquivamento de fase sem marcacao deprecated.

## Plano TDD

- Red: nao aplicavel
- Green: master alinhado ao PRD da migracao
- Refactor: tabela de fontes de verdade coerente com `GOV-AUDITORIA-FEATURE` vs conflitos PRD mencionados no relatorio

## Criterios de Aceitacao

- [x] Nenhuma linha activa descreve o repositório como `issue-first` como padrao vigente
- [x] Referencias a Fase/Sprint/Epico no ciclo actual ausentes ou confinadas a secao `deprecated` / retroativa
- [x] Tabela de fontes de verdade coerente com decisao documentada (resolver conflito GOV-AUDITORIA-FEATURE vs texto PRD se ainda existir)

## Definition of Done da Issue

- [x] `TASK-1.md` concluida
- [x] Revisao pos-issue conforme governanca

## Tasks

- [T1 - Limpar GOV-FRAMEWORK-MASTER](./TASK-1.md)

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/COMUM/GOV-AUDITORIA-FEATURE.md` (se existir; senao verificar nome canónico em COMUM)
- `AGENTS.md` (alinhamento com premissas do master; condicao de paragem da TASK-1)
- `PRD-OPENCLAW-MIGRATION.md`

## Artifact Minimo

- `GOV-FRAMEWORK-MASTER.md` actualizado

## Handoff para Revisao Pos-Issue

status: aprovado
round: 1
base_commit: 4014b818e44851fea1b5a604865797b105009171
target_commit: 2f2c033aefa4dc067f23e0df6eceec37e9e14e34
evidencia: "git show 2f2c033aefa4dc067f23e0df6eceec37e9e14e34; git diff 4014b818e44851fea1b5a604865797b105009171..2f2c033aefa4dc067f23e0df6eceec37e9e14e34 -- PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md AGENTS.md"
commits_execucao:
  - 2f2c033aefa4dc067f23e0df6eceec37e9e14e34
validacoes_executadas:
  - "rg -n issue-first PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md — ocorrencia apenas na secao 2.1 (compatibilidade legada)"
  - "Leitura das seccoes 0-2: premissas principais em Feature > US > Task, sem issue-first como padrao vigente"
arquivos_de_codigo_relevantes:
  - PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md
  - AGENTS.md
limitacoes:
  - "boot-prompt.md niveis 1-3 ainda abrem com rotulo issue-first; F1-01-002 limitou-se a niveis 4-6 — fora do artefacto minimo desta issue"

## Dependencias

- [Intake](../../../INTAKE-OPENCLAW-MIGRATION.md)
- [PRD](../../../PRD-OPENCLAW-MIGRATION.md)
- [Epic](../../EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md)
- [Fase](../../F1_OPENCLAW-MIGRATION_EPICS.md)
- [Relatorio R01](../../../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
