---
doc_id: "EPIC-F1-01-BASELINE-DE-MODELO-IMPORT-E-MIGRATION.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-01 - Baseline de modelo, import e migration

## Objetivo

Fechar a fundacao estrutural de `LeadEvento`, incluindo surface de import e migration versionada.

## Resultado de Negocio Mensuravel

O backend volta a subir e `lead_evento` passa a ter trilha Alembic explicita.

## Contexto Arquitetural

- reexport de `LeadEventoSourceKind` hoje esta incompleto em `app.models.models`
- servicos de landing, pipeline e dashboard ja importam o tipo via `app.models.models`
- a migration versionada de `lead_evento` nao foi localizada em `backend/alembic/versions/`

## Definition of Done do Epico

- [ ] `LeadEvento` e `LeadEventoSourceKind` importaveis via `app.models.models`
- [ ] migration versionada de `lead_evento` criada ou validada
- [ ] suite alvo coleta sem erro de import

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Corrigir surface de modelo e boot da app | Reexportar `LeadEvento` e `LeadEventoSourceKind` no agregado de modelos e remover o erro de import que hoje impede a coleta da suite. | 1 | todo | [README](./issues/ISSUE-F1-01-001-CORRIGIR-SURFACE-DE-MODELO-E-BOOT-DA-APP/README.md) |
| ISSUE-F1-01-002 | Versionar migration de lead_evento | Criar ou validar a migration Alembic da tabela `lead_evento` com FKs, indices e `UNIQUE (lead_id, evento_id)`. | 2 | todo | [README](./issues/ISSUE-F1-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO/README.md) |
| ISSUE-F1-01-003 | Exportar LeadEvento e LeadEventoSourceKind no agregado de modelos | Garantir que `LeadEvento` e `LeadEventoSourceKind` sejam exportados pelo agregado de modelos (`app.models.models`) para que a aplicacao suba sem `ImportError` e os modulos que dependem desses tipos possam importar pelo caminho canonico. | 1 | done | [README](./issues/ISSUE-F1-01-003-EXPORTAR-MODELEVENTOSOURCEKIND/README.md) |

## Artifact Minimo do Epico

- `backend/app/models/models.py`
- `backend/app/models/lead_public_models.py`
- `backend/alembic/versions/`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F1_DASHBOARD_LEADS_EPICS.md)
