---
doc_id: "FEATURE-5.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-5 - Smoke Test e Projeto de Referencia Canonicos

## Objetivo de Negocio

Garantir que o smoke verde prove aderencia ao paradigma novo, e nao apenas ao
legado.

## Dependencias da Feature

- Feature 4

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] smoke local valida apenas `SESSION-*` e caminhos canonicos
- [ ] smoke remoto falha quando `features`, `user_stories` ou `tasks` nao
      forem populadas no SQLite v4
- [ ] `PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md` descreve apenas o fluxo
      canonico

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-5.1 | Reescrever o smoke test | 5 | US-4.1 | todo | `user-stories/US-5-01-REESCREVER-O-SMOKE-TEST/README.md` |
| US-5.2 | Migrar OC-SMOKE-SKILLS para a arvore canonica | 5 | US-5.1 | todo | `user-stories/US-5-02-MIGRAR-OC-SMOKE-SKILLS-PARA-A-ARVORE-CANONICA/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

