---
doc_id: "FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "not_ready"
---

# FEATURE-6 - Implementacao do rename do modulo lead imports

## Objetivo de Negocio

Reduzir ambiguidade estrutural no backend de importacao de leads ao tornar
`app.modules.lead_imports` o caminho real e preferencial, preservando
compatibilidade temporaria para `app.modules.leads_publicidade`.

## Resultado de Negocio Mensuravel

O backend passa a usar o nome de dominio neutro nos consumidores ativos, com
teste automatizado garantindo que imports legados profundos continuam
funcionando durante a janela de migracao.

## Dependencias da Feature

- `PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `PRD-RENAME-MODULO-LEAD-IMPORTS.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-2`, `FEATURE-3`, `FEATURE-4` e
  decisao de nome em `FEATURE-5`

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up deliberado da `FEATURE-5`
- contrato publico preservado: `sim`
- decisao escolhida: implementar `app.modules.lead_imports` como pacote real e
  manter `app.modules.leads_publicidade` como alias temporario

## Criterios de Aceite

- [x] governanca propria da implementacao criada
- [x] pacote real `backend/app/modules/lead_imports` criado
- [x] pacote antigo transformado em shims de compatibilidade
- [x] consumers ativos migrados para `app.modules.lead_imports`
- [x] teste de compatibilidade para import profundo legado e monkeypatch por
  string adicionado
- [x] contratos HTTP, schemas, frontend, dashboard, `lead_pipeline/` e
  `core/leads_etl/` permanecem fora do escopo

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-6-01 | Implementar rename do modulo lead imports | 2 | FEATURE-5 | ready_for_review | [README](./user-stories/US-6-01-IMPLEMENTAR-RENAME-MODULO-LEAD-IMPORTS/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- remover `backend/app/modules/leads_publicidade`
- limpar referencias historicas antigas
- reabrir importacao/ETL funcional
- mover frontend restante de leads para `features/leads`

## Dependencias

- [PRD implementacao rename modulo lead imports](../../PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- [Intake implementacao rename modulo lead imports](../../INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- [Plano operacional](../../../plano_organizacao_import.md)
