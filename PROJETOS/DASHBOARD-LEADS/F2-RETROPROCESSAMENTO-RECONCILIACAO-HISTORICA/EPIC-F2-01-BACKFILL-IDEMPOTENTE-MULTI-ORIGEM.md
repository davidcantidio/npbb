---
doc_id: "EPIC-F2-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-01 - Backfill idempotente multi-origem

## Objetivo

Expor execucao controlada do backfill de `LeadEvento` a partir das tres fontes previstas no PRD.

## Resultado de Negocio Mensuravel

Historico resolvivel fica materializado em `LeadEvento` sem duplicidades.

## Contexto Arquitetural

- o servico `backfill_lead_event_links` ja existe parcialmente no runtime
- falta transformar a logica em execucao controlada, coberta e rastreavel

## Definition of Done do Epico

- [ ] runner controlado disponivel
- [ ] precedencia e upgrade de `source_kind` testados
- [ ] idempotencia comprovada

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Implementar runner idempotente de backfill | Transformar a logica de backfill em execucao controlada e rastreavel para `AtivacaoLead`, `LeadBatch` e `evento_nome` deterministico. | 3 | todo | [README](./issues/ISSUE-F2-01-001-IMPLEMENTAR-RUNNER-IDEMPOTENTE-DE-BACKFILL/README.md) |
| ISSUE-F2-01-002 | Testar precedencia e idempotencia do backfill | Cobrir precedencia de `source_kind`, upgrade de fonte e idempotencia do backfill. | 2 | todo | [README](./issues/ISSUE-F2-01-002-TESTAR-PRECEDENCIA-E-IDEMPOTENCIA-DO-BACKFILL/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/lead_event_service.py`
- `backend/scripts/`
- `backend/tests/`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F2_DASHBOARD_LEADS_EPICS.md)
