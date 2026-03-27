---
doc_id: "FEATURE-3.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-3 - Documentos Operacionais e Skills

## Objetivo de Negocio

Fazer `boot-prompt.md`, `SESSION-*` e skills operarem no mesmo vocabulario
`Feature/US/Task`.

## Dependencias da Feature

- Feature 1
- Feature 2

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] niveis 4-6 do `boot-prompt.md` operam em `Feature > User Story > Task`
- [ ] `SESSION-IMPLEMENTAR-US.md` e `SESSION-AUDITAR-FEATURE.md` sao os
      entrypoints corretos
- [ ] `SESSION-MAPA.md` e skills relevantes apontam apenas para a superficie
      activa

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-3.1 | Atualizar boot-prompt.md | 5 | US-2.2 | todo | `user-stories/US-3-01-ATUALIZAR-BOOT-PROMPT-MD/README.md` |
| US-3.2 | SESSION-IMPLEMENTAR-US.md | 3 | US-3.1 | todo | `user-stories/US-3-02-SESSION-IMPLEMENTAR-US-MD/README.md` |
| US-3.3 | SESSION-AUDITAR-FEATURE.md | 3 | US-3.1 | todo | `user-stories/US-3-03-SESSION-AUDITAR-FEATURE-MD/README.md` |
| US-3.4 | Atualizar skills e SESSION-MAPA.md | 3 | US-3.2, US-3.3 | todo | `user-stories/US-3-04-ATUALIZAR-SKILLS-E-SESSION-MAPA-MD/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

