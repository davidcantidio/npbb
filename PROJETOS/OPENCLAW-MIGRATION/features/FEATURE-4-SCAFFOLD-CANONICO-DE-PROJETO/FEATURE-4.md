---
doc_id: "FEATURE-4.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-25"
audit_gate: "not_ready"
---

# FEATURE-4 - Scaffold Canonico de Projeto

## Objetivo de Negocio

Fazer novos projectos nascerem directamente no formato
`Feature -> User Story -> Task`.

## Dependencias da Feature

- Feature 1
- Feature 2
- Feature 3

## Estado Operacional

- status: `todo`
- audit_gate: `not_ready`

## Criterios de Aceite

- [ ] `scripts/criar_projeto.py` nao gera `F1-*`, `issues/` nem `SPRINT-*`
- [ ] wrappers locais do projecto apontam para `SESSION-IMPLEMENTAR-US`,
      `SESSION-REVISAR-US` e `SESSION-AUDITAR-FEATURE`
- [ ] `tests/test_criar_projeto.py` valida apenas a arvore canonica

## User Stories Planejadas

| US ID | Titulo | SP estimado | Depende de | Status | Documento previsto |
|---|---|---|---|---|---|
| US-4.1 | Migrar scripts/criar_projeto.py para scaffold canonico | 5 | US-3.4 | todo | `user-stories/US-4-01-MIGRAR-SCRIPTS-CRIAR-PROJETO-PY-PARA-SCAFFOLD-CANONICO/README.md` |
| US-4.2 | Reescrever wrappers locais do bootstrap do projecto | 3 | US-4.1 | todo | `user-stories/US-4-02-REESCREVER-WRAPPERS-LOCAIS-DO-BOOTSTRAP-DO-PROJECTO/README.md` |
| US-4.3 | Reescrever testes do scaffold para o formato canonico | 3 | US-4.1 | todo | `user-stories/US-4-03-REESCREVER-TESTES-DO-SCAFFOLD-PARA-O-FORMATO-CANONICO/README.md` |

## Dependencias

- [PRD do projeto](../../PRD-OPENCLAW-MIGRATION.md)
- [Intake do projeto](../../INTAKE-OPENCLAW-MIGRATION.md)
- [Spec de alinhamento end-to-end](../../openclaw-alignment-spec.md)

