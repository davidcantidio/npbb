---
doc_id: "FEATURE-1.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-1 - Documentos de Governanca Centrais

## Objetivo de Negocio

Definir no master e no scrum do framework a cadeia `Feature > User Story > Task`
e os limites de User Story.

## Dependencias da Feature

- nenhuma

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] `GOV-FRAMEWORK-MASTER.md` descreve a hierarquia canonica e as fontes de
      verdade correctas
- [ ] `GOV-SCRUM.md` nao usa Sprint, Epico ou Fase como cadeia operacional
      principal
- [ ] `GOV-USER-STORY.md` define limites numericos e DoD de User Story

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-1.1 | Atualizar GOV-FRAMEWORK-MASTER.md | 5 | - | todo | `user-stories/US-1-01-ATUALIZAR-GOV-FRAMEWORK-MASTER-MD/README.md` |
| US-1.2 | Atualizar GOV-SCRUM.md | 5 | US-1.1 | todo | `user-stories/US-1-02-ATUALIZAR-GOV-SCRUM-MD/README.md` |
| US-1.3 | Criar/alinhar GOV-USER-STORY.md | 3 | - | todo | `user-stories/US-1-03-CRIAR-ALINHAR-GOV-USER-STORY-MD/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

