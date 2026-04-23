---
doc_id: "FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "not_ready"
---

# FEATURE-8 - Remocao de wrappers frontend de leads

## Objetivo de Negocio

Reduzir ambiguidade estrutural no frontend de leads nao-import ao fazer as
rotas internas consumirem diretamente o slice `frontend/src/features/leads`.

## Resultado de Negocio Mensuravel

As telas `/leads` e `/dashboard/leads/analise-etaria` continuam funcionais, mas
sem dependencia interna dos wrappers legados de `pages/*` e `hooks/*`.

## Dependencias da Feature

- `PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-3`, `FEATURE-4`, `FEATURE-6` e
  `FEATURE-7`

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up deliberado do backlog do plano operacional
- contrato publico preservado: `sim`
- decisao escolhida: remover wrappers nao-import sem consumidores relevantes

## Criterios de Aceite

- [x] governanca propria da remocao criada
- [x] busca inicial de consumidores executada
- [x] `AppRoutes.tsx` lazy-loada lista e analise etaria de `features/leads`
- [x] wrappers legados nao-import sem consumidores relevantes removidos
- [x] `/leads`, `/leads/importar` e `/dashboard/leads/analise-etaria`
  preservadas
- [x] importacao/ETL, backend, contratos HTTP, schemas e rotas publicas fora do
  escopo

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-8-01 | Remover wrappers frontend leads nao-import | 1 | FEATURE-7 | ready_for_review | [README](./user-stories/US-8-01-REMOVER-WRAPPERS-FRONTEND-LEADS/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- mover o shell de importacao para `features/leads`
- reabrir importacao/ETL funcional
- habilitar `/dashboard/leads/conversao`

## Dependencias

- [PRD remocao wrappers frontend leads](../../PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)
- [Intake remocao wrappers frontend leads](../../INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)
- [Plano operacional](../../../plano_organizacao_import.md)
