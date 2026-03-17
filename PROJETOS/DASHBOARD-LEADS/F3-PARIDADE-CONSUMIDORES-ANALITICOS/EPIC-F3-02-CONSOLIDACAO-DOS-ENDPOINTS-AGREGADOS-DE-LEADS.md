---
doc_id: "EPIC-F3-02-CONSOLIDACAO-DOS-ENDPOINTS-AGREGADOS-DE-LEADS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F3-02 - Consolidacao dos endpoints agregados de leads

## Objetivo

Fechar `/dashboard/leads` e `/dashboard/leads/relatorio` sobre a mesma semantica canonica.

## Resultado de Negocio Mensuravel

KPIs, rankings e relatorios agregados compartilham a mesma base de leitura por `LeadEvento`.

## Contexto Arquitetural

- os endpoints agregados ja usam `LeadEvento` em partes centrais
- falta consolidar cobertura, fixtures e remover drift semantico residual

## Definition of Done do Epico

- [ ] `/dashboard/leads` consolidado
- [ ] `/dashboard/leads/relatorio` consolidado
- [ ] rankings e filtros cobertos

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Consolidar /dashboard/leads e rankings | Garantir que KPIs, series e rankings de `/dashboard/leads` usem `LeadEvento` de forma consistente e testavel. | 2 | todo | [README](./issues/ISSUE-F3-02-001-CONSOLIDAR-DASHBOARD-LEADS-E-RANKINGS/README.md) |
| ISSUE-F3-02-002 | Consolidar /dashboard/leads/relatorio | Fechar o endpoint de relatorio agregado sobre a mesma semantica canonica de `LeadEvento`. | 1 | todo | [README](./issues/ISSUE-F3-02-002-CONSOLIDAR-DASHBOARD-LEADS-RELATORIO/README.md) |

## Artifact Minimo do Epico

- `backend/app/routers/dashboard_leads.py`
- `backend/app/services/dashboard_leads_report.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F3_DASHBOARD_LEADS_EPICS.md)
