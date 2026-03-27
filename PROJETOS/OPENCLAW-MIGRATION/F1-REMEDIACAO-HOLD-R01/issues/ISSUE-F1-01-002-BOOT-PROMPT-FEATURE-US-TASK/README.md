---
doc_id: "ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
task_instruction_mode: "required"
decision_refs:
  - "PROJETOS/OPENCLAW-MIGRATION/auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md#follow-ups-bloqueantes"
---

# ISSUE-F1-01-002 - Boot prompt Feature / US / Task

## User Story

Como agente autonomo OpenClaw, quero que `boot-prompt.md` descubra Feature, User Story e Task nos niveis 4-6, para que o fluxo autonomo nao dependa de Fase/Epico/Issue.

## Feature de Origem

- **Feature**: Feature 3 (Documentos Operacionais e Skills)
- **Comportamento coberto**: Follow-up B2 / ACHADO A-01 — reescrita de `PROJETOS/COMUM/boot-prompt.md` conforme Task 3.1.1 do spec.

## Contexto Tecnico

O relatorio indica que linhas 113-203 permanecem em Fases/Epicos/Issues. A reescrita deve alinhar quadro de confirmacao, sequencias minimas (ex. AUDITORIA-FEATURE) e descoberta de unidade elegivel.

## Plano TDD

- Red: nao aplicavel
- Green: boot coerente com PRD/spec
- Refactor: reduzir duplicacao com `SESSION-MAPA.md` apos ISSUE-F1-01-003

## Criterios de Aceitacao

- [x] Niveis 4, 5 e 6 descrevem Feature -> User Story -> Task
- [x] Quadro de confirmacao usa nomenclatura do spec (MODO, FEATURE ALVO, US ALVO, TASK ALVO, etc.)
- [x] Referencias a ISSUE/Fase/Epico removidas ou confinadas a bloco `deprecated` se ainda necessarias
- [x] Alinhamento com estrutura de pastas definida em `GOV-FRAMEWORK-MASTER.md` apos B4

## Definition of Done da Issue

- [x] `TASK-1.md` concluida com evidencia
- [x] Revisao pos-issue conforme governanca

## Tasks

- [T1 - Reescrever boot-prompt niveis 4-6](./TASK-1.md)

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/boot-prompt.md`
- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`
- `PROJETOS/OPENCLAW-MIGRATION/openclaw-migration-spec.md`

## Artifact Minimo

- `boot-prompt.md` actualizado

## Handoff para Revisao Pos-Issue

status: pronto_para_revisao_senior
round: 1
base_commit: 6b7369043bc2e4ea2468cae960c5f060e6ad231e
target_commit: 3e1b08b6cde99bd830c89259c4e4ee2d8c5125a1
evidencia: git diff 6b7369043bc2e4ea2468cae960c5f060e6ad231e..3e1b08b6cde99bd830c89259c4e4ee2d8c5125a1
commits_execucao:
  - "5fa4586b029e17b25db509b1e4788e5eb10c0bad OPENCLAW-MIGRATION ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK T1: reescrever boot-prompt niveis 4-6 Feature/US/Task"
  - "3e1b08b6cde99bd830c89259c4e4ee2d8c5125a1 OPENCLAW-MIGRATION ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK CLOSE: preparar handoff de revisao"
validacoes_executadas:
  - "Leitura estrutural: niveis 4-6 canonicos usam features/FEATURE-* e user-stories/US-*; sem uso de ISSUE-* como unidade de descoberta nesse ramo"
  - "Bloco deprecated: quando nao ha features/FEATURE-*, descoberta Fase/Epico/Issue permanece explicita e isolada"
  - "Modo AUDITORIA-FEATURE referencia SESSION-AUDITAR-FEATURE.md e caminho de relatorio sob features/"
arquivos_de_codigo_relevantes:
  - "PROJETOS/COMUM/boot-prompt.md"
limitacoes:
  - "nenhuma"

## Dependencias

- [Intake](../../../INTAKE-OPENCLAW-MIGRATION.md)
- [PRD](../../../PRD-OPENCLAW-MIGRATION.md)
- [Epic](../../EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md)
- [Fase](../../F1_OPENCLAW-MIGRATION_EPICS.md)
- [Relatorio R01](../../../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
