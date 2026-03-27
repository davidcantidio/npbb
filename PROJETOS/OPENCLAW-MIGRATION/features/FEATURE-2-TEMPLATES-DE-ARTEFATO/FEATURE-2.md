---
doc_id: "FEATURE-2.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-2 - Templates de Artefato

## Objetivo de Negocio

Disponibilizar templates coerentes com PRD feature-centric e User Story
canonica.

## Dependencias da Feature

- Feature 1

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] `TEMPLATE-USER-STORY.md` existe com frontmatter e campos canonicos
- [ ] `TEMPLATE-PRD.md`, `TEMPLATE-AUDITORIA-FEATURE.md` e
      `TEMPLATE-ENCERRAMENTO.md` estao alinhados
- [ ] `TEMPLATE-TASK.md` mantem TDD e rastreabilidade

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-2.1 | Atualizar TEMPLATE-PRD.md | 3 | US-1.1 | todo | `user-stories/US-2-01-ATUALIZAR-TEMPLATE-PRD-MD/README.md` |
| US-2.2 | Criar TEMPLATE-USER-STORY.md | 3 | US-1.3 | todo | `user-stories/US-2-02-CRIAR-TEMPLATE-USER-STORY-MD/README.md` |
| US-2.3 | Criar TEMPLATE-AUDITORIA-FEATURE.md | 3 | US-2.1 | todo | `user-stories/US-2-03-CRIAR-TEMPLATE-AUDITORIA-FEATURE-MD/README.md` |
| US-2.4 | Criar TEMPLATE-ENCERRAMENTO.md | 2 | US-2.1 | todo | `user-stories/US-2-04-CRIAR-TEMPLATE-ENCERRAMENTO-MD/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

