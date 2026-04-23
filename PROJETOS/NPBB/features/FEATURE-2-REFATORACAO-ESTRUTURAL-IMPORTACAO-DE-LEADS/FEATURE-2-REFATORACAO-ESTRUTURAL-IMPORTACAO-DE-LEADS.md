---
doc_id: "FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
audit_gate: "pending"
---

# FEATURE-2 - Refatoracao estrutural da importacao de leads

## Objetivo de Negocio

Aplicar uma rodada incremental de reducao de acoplamento na trilha de leads sem
reabrir a feature funcional ja auditada e sem alterar contratos externos.

## Resultado de Negocio Mensuravel

O time consegue evoluir backend, frontend e docs da trilha de leads com
rollback simples, menor hotspot estrutural e validacao focada preservando os
fluxos existentes.

## Dependencias da Feature

- `PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- baseline funcional ja auditada em `FEATURE-1`

## Estado Operacional

- status: `active`
- audit_gate: `pending`
- origem: mini-projeto de remediacao estrutural derivado da trilha de leads
- contrato publico preservado: `sim`

## Criterios de Aceite

- [ ] `backend/app/routers/leads.py` virou agregador fino
- [ ] novos subrouters internos foram abertos em `backend/app/routers/leads_routes/`
- [ ] hook de referencia de eventos foi centralizado em `frontend/src/hooks`
- [ ] `/leads/importar` faz lazy-load direto de `ImportacaoPage`
- [ ] docs operacionais descrevem o shell canonico e a divergencia do dashboard
- [ ] follow-ups maiores ficaram explicitamente fora desta rodada

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-2-01 | Modularizacao do router de leads e alinhamento documental | 3 | nenhuma | active | [README](./user-stories/US-2-01-MODULARIZACAO-DO-ROUTER-DE-LEADS-E-ALINHAMENTO-DOCUMENTAL/README.md) |
| US-2-02 | Hook compartilhado e shell canonico de importacao | 2 | US-2-01 | active | [README](./user-stories/US-2-02-HOOK-COMPARTILHADO-E-SHELL-CANONICO-DE-IMPORTACAO/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- mexer em `lead_pipeline/`
- mexer em `core/leads_etl/`
- rename amplo de `app.modules.leads_publicidade`
- mover toda a vertical para `frontend/src/features/leads`
- decidir produto sobre `DashboardLeads.tsx`

## Dependencias

- [PRD estrutural](../../PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
- [Intake estrutural](../../INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
- [Feature 1](../FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD.md)
