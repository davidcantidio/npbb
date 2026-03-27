---
doc_id: "FEATURE-7.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-7 - Banco de Dados e Queries Estruturadas Reais

## Objetivo de Negocio

Fazer o SQLite v4 reflectir projectos reais do framework, nao apenas fixtures.

## Dependencias da Feature

- Feature 4
- Feature 5

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] um projecto criado pelo scaffold canonico popular `features`,
      `user_stories`, `tasks` e `feature_audits`
- [ ] projectos legados continuam indexados em `documents` sem poluir o modelo
      estruturado
- [ ] existe teste de integracao criando projecto, rodando sync e validando
      SQL minima

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-7.1 | Validar ingestao estruturada real no indice v4 | 5 | US-5.2 | todo | `user-stories/US-7-01-VALIDAR-INGESTAO-ESTRUTURADA-REAL-NO-INDICE-V4/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

