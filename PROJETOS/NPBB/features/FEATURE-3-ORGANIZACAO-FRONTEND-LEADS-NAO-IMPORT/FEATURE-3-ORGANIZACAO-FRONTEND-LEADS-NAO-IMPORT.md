---
doc_id: "FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "pending"
---

# FEATURE-3 - Organizacao frontend de leads nao-import

## Objetivo de Negocio

Agrupar a superficie nao-import de leads do frontend em um slice interno mais
coeso, preservando rotas, manifesto e compatibilidade com imports legados.

## Resultado de Negocio Mensuravel

O time consegue evoluir lista e dashboard de leads a partir de uma vertical
`features/leads`, com rollback simples, menor acoplamento interno e sem tocar
na trilha de importacao/ETL.

## Dependencias da Feature

- `PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-2`

## Estado Operacional

- status: `active`
- audit_gate: `pending`
- origem: follow-up deliberado da rodada estrutural anterior
- contrato publico preservado: `sim`
- consolidacao de imports internos/testes executada em 2026-04-23

## Criterios de Aceite

- [x] `frontend/src/features/leads/` agrupa lista, dashboard e hook compartilhado
- [x] `pages/*` e `hooks/useReferenciaEventos.ts` permanecem validos via wrappers
- [x] `AppRoutes.tsx` e `dashboardManifest.ts` seguem funcionalmente iguais
- [x] `DashboardLeads.tsx` permanece legado nao roteado, fora desta rodada
- [x] validacao focada do recorte permanece verde

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-3-01 | Slice inicial de lista e dashboard | 2 | nenhuma | active | [README](./user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- remover wrappers temporarios
- decidir produto sobre reutilizar `DashboardLeads.tsx` para `/dashboard/leads/conversao`
- reabrir importacao/ETL

## Dependencias

- [PRD frontend nao-import](../../PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- [Intake frontend nao-import](../../INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- [Feature 2](../FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md)
