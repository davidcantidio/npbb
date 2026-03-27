---
doc_id: "EPIC-F1-01-REMEDIACAO-HOLD-MIGRATION-R01.md"
version: "1.3"
status: "done"
owner: "PM"
last_updated: "2026-03-25"
---

# EPIC-F1-01 - Remediacao hold MIGRATION-R01

## Objetivo

Entregar os quatro follow-ups bloqueantes B1-B4 do [RELATORIO-AUDITORIA-MIGRATION-R01.md](../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md), restaurando alinhamento entre PRD/spec da migracao e `PROJETOS/COMUM/`.

## Resultado de Negocio Mensuravel

Framework auditavel e operavel na hierarquia Feature > User Story > Task nos pontos bloqueados pelo R01.

## Feature de Origem

- **Feature**: Migracao OpenClaw (Features 1-3 do [PRD-OPENCLAW-MIGRATION.md](../PRD-OPENCLAW-MIGRATION.md))
- **Comportamento coberto**: Templates, boot autonomo, superficie SESSION/GOV consistente.

## Contexto Arquitetural

- Artefactos centrais em `PROJETOS/COMUM/`
- Auditoria ao nivel do projecto OPENCLAW-MIGRATION (`MIGRATION-R01`)

## Definition of Done do Epico

- [x] B1: `TEMPLATE-USER-STORY.md` criado e alinhado a `GOV-USER-STORY.md` e US 2.2 do spec
- [x] B2: `boot-prompt.md` com niveis 4-6 em Feature > US > Task
- [x] B3: `SESSION-REVISAR-US.md`, `SESSION-MAPA.md`, `SESSION-AUDITAR-FEATURE.md`, `GOV-SCRUM.md` e depreciacao dos SESSIONs legados conforme relatorio
- [x] B4: `GOV-FRAMEWORK-MASTER.md` sem `issue-first` e referencias a fase fora de contexto `deprecated`

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Template User Story canonico | Criar TEMPLATE-USER-STORY.md | 2 | done | [ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO](./issues/ISSUE-F1-01-001-TEMPLATE-USER-STORY-CANONICO/) | Feature 2 |
| ISSUE-F1-01-002 | Boot prompt Feature-US-Task | Reescrever boot niveis 4-6 | 5 | done | [ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK](./issues/ISSUE-F1-01-002-BOOT-PROMPT-FEATURE-US-TASK/) | Feature 3 |
| ISSUE-F1-01-003 | Superficie SESSION e GOV-SCRUM | Consolidar SESSION-* e depreciar legados | 5 | done | [ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM](./issues/ISSUE-F1-01-003-SUPERFICIE-SESSION-E-GOV-SCRUM/) | Feature 1 / 3 |
| ISSUE-F1-01-004 | GOV-FRAMEWORK-MASTER limpeza | Remover issue-first fora de deprecated | 3 | done | [ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA](./issues/ISSUE-F1-01-004-GOV-FRAMEWORK-MASTER-LIMPEZA/) | Feature 1 |

## Artifact Minimo do Epico

- Quatro pastas `issues/ISSUE-F1-01-00x-*/` com `README.md` e `TASK-*.md`
- Actualizacao de [AUDIT-LOG.md](../AUDIT-LOG.md) com Refs canonicas

## Dependencias

- [Intake](../INTAKE-OPENCLAW-MIGRATION.md)
- [PRD](../PRD-OPENCLAW-MIGRATION.md)
- [Spec](../openclaw-migration-spec.md)
- [Fase](./F1_OPENCLAW-MIGRATION_EPICS.md)
- [Relatorio R01](../auditorias/RELATORIO-AUDITORIA-MIGRATION-R01.md)
