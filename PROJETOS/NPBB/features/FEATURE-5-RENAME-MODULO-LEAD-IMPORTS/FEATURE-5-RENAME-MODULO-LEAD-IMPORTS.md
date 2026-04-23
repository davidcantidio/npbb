---
doc_id: "FEATURE-5-RENAME-MODULO-LEAD-IMPORTS"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "not_ready"
---

# FEATURE-5 - Rename do modulo leads_publicidade para lead_imports

## Objetivo de Negocio

Reduzir ambiguidade estrutural no backend de importacao de leads ao planejar a
migracao futura de `app.modules.leads_publicidade` para o nome neutro
`app.modules.lead_imports`.

## Resultado de Negocio Mensuravel

O time passa a ter uma decisao registrada de nome, impacto e compatibilidade
antes de executar um rename transversal em routers, worker, servicos e testes.

## Dependencias da Feature

- `PRD-RENAME-MODULO-LEAD-IMPORTS.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-2`, `FEATURE-3` e `FEATURE-4`

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up deliberado da organizacao incremental de leads
- contrato publico preservado: `sim`
- decisao escolhida: planejar rename para `app.modules.lead_imports` com alias
  temporario para `app.modules.leads_publicidade`

## Criterios de Aceite

- [x] governanca propria da decisao criada
- [x] nome alvo `app.modules.lead_imports` registrado
- [x] mapa de consumidores de `leads_publicidade` registrado por categoria
- [x] estrategia de compatibilidade futura registrada
- [x] rename fisico e alteracoes de imports permanecem fora desta rodada
- [x] `plano_organizacao_import.md` atualizado

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-5-01 | Mapear e planejar rename do modulo lead imports | 1 | FEATURE-4 | ready_for_review | [README](./user-stories/US-5-01-MAPEAR-E-PLANEJAR-RENAME-MODULO-LEAD-IMPORTS/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- criar fisicamente `backend/app/modules/lead_imports`
- migrar imports internos para `app.modules.lead_imports`
- manter `backend/app/modules/leads_publicidade` como alias/reexport temporario
- remover o alias antigo apos busca sem consumidores
- reabrir importacao/ETL funcional

## Dependencias

- [PRD rename modulo lead imports](../../PRD-RENAME-MODULO-LEAD-IMPORTS.md)
- [Intake rename modulo lead imports](../../INTAKE-RENAME-MODULO-LEAD-IMPORTS.md)
- [Plano operacional](../../../plano_organizacao_import.md)
