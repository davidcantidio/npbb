---
doc_id: "FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "pending"
---

# FEATURE-4 - Decisao sobre DashboardLeads legado

## Objetivo de Negocio

Encerrar a ambiguidade sobre a tela frontend legada `DashboardLeads.tsx`,
removendo codigo sem rota publica e preservando a superficie atual de
dashboard de leads.

## Resultado de Negocio Mensuravel

O time deixa de carregar uma tela legada sem consumidor ativo, mantendo a rota
atual `/dashboard/leads/analise-etaria` e o endpoint/script
`GET /dashboard/leads/relatorio` intactos.

## Dependencias da Feature

- `PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-3`

## Estado Operacional

- status: `active`
- audit_gate: `pending`
- origem: follow-up deliberado da organizacao frontend nao-import
- contrato publico preservado: `sim`
- decisao escolhida: remover/arquivar a superficie frontend orfa

## Criterios de Aceite

- [x] governanca propria da decisao criada
- [x] `DashboardLeads.tsx` removido do frontend
- [x] `dashboard_leads.ts` removido do frontend
- [x] `AppRoutes.tsx` e `dashboardManifest.ts` seguem sem mudanca funcional
- [x] backend e scripts de relatorio permanecem fora do escopo
- [x] importacao/ETL e wrappers legados permanecem intactos

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-4-01 | Arquivar DashboardLeads legado | 1 | FEATURE-3 | active | [README](./user-stories/US-4-01-ARQUIVAR-DASHBOARD-LEADS-LEGADO/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- criar uma nova tela para `/dashboard/leads/conversao`
- alterar o endpoint/script `GET /dashboard/leads/relatorio`
- remover wrappers temporarios de `features/leads`
- reabrir importacao/ETL

## Dependencias

- [PRD decisao DashboardLeads legado](../../PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- [Intake decisao DashboardLeads legado](../../INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- [Feature 3](../FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
