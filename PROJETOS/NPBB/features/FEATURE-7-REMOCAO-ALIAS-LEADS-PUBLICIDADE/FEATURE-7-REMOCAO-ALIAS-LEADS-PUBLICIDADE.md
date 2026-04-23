---
doc_id: "FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "not_ready"
---

# FEATURE-7 - Remocao do alias leads_publicidade

## Objetivo de Negocio

Reduzir ambiguidade estrutural no backend de importacao de leads ao remover o
alias temporario `app.modules.leads_publicidade` e manter
`app.modules.lead_imports` como unico caminho real.

## Resultado de Negocio Mensuravel

O backend deixa de expor o caminho interno legado, mantendo os consumidores
ativos no caminho neutro `app.modules.lead_imports` e preservando testes focados
de ETL/importacao.

## Dependencias da Feature

- `PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
- `PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-2`, `FEATURE-3`, `FEATURE-4`,
  `FEATURE-5` e `FEATURE-6`

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up deliberado da `FEATURE-6`
- contrato publico preservado: `sim`
- decisao escolhida: remover `app.modules.leads_publicidade` e manter apenas
  `app.modules.lead_imports`

## Criterios de Aceite

- [x] governanca propria da remocao criada
- [x] busca inicial sem consumidores ativos fora dos shims e do teste dedicado
- [x] pacote legado `backend/app/modules/leads_publicidade` removido
- [x] teste de compatibilidade temporaria removido
- [x] `app.modules.lead_imports` preservado como caminho real
- [x] contratos HTTP, schemas, frontend, dashboard, `lead_pipeline/` e
  `core/leads_etl/` permanecem fora do escopo

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-7-01 | Remover alias leads publicidade | 1 | FEATURE-6 | ready_for_review | [README](./user-stories/US-7-01-REMOVER-ALIAS-LEADS-PUBLICIDADE/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- limpar referencias historicas antigas
- reabrir importacao/ETL funcional
- mover frontend restante de leads para `features/leads`
- remover wrappers legados frontend

## Dependencias

- [PRD remocao alias leads publicidade](../../PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)
- [Intake remocao alias leads publicidade](../../INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md)
- [Plano operacional](../../../plano_organizacao_import.md)
