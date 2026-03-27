---
doc_id: "FEATURE-8.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-8 - Toolchain de Metadata das Skills

## Objetivo de Negocio

Eliminar drift entre `SKILL.md`, `agents/openai.yaml` e scripts de deploy.

## Dependencias da Feature

- Feature 3
- Feature 5

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] `bin/codex-skills-common.sh` emite labels canonicos
- [ ] `agents/openai.yaml` visiveis nao usam `Issue`, `Phase`, `Epic` ou
      `Sprint` como superficie principal
- [ ] existe cobertura de teste para blindar a metadata das skills

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-8.1 | Blindar metadata canonica das skills | 3 | US-5.1 | todo | `user-stories/US-8-01-BLINDAR-METADATA-CANONICA-DAS-SKILLS/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)
