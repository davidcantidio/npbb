---
doc_id: "FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
audit_gate: "not_ready"
---

# FEATURE-9 - Decisao sobre shell de importacao de leads

## Objetivo de Negocio

Evitar uma migracao funcional ampla e arriscada do shell `/leads/importar`,
registrando a fronteira atual e preparando uma decisao segura para trabalho
posterior.

## Resultado de Negocio Mensuravel

O time passa a ter uma decisao explicita: `ImportacaoPage.tsx` permanece em
`frontend/src/pages/leads` nesta rodada, e qualquer migracao para
`features/leads/importacao` dependera de nova feature.

## Dependencias da Feature

- `PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `plano_organizacao_import.md`
- baseline estrutural preservada em `FEATURE-8`

## Estado Operacional

- status: `active`
- audit_gate: `not_ready`
- origem: follow-up deliberado do backlog do plano operacional
- contrato publico preservado: `sim`
- decisao escolhida: manter o shell atual e documentar fronteiras

## Criterios de Aceite

- [x] governanca propria da decisao criada
- [x] busca inicial de fronteira executada
- [x] `ImportacaoPage.tsx` registrado como shell canonico atual
- [x] `frontend/src/pages/leads/importacao/**`, `MapeamentoPage`,
  `BatchMapeamentoPage` e `PipelineStatusPage` registrados como acoplamentos
- [x] proxima migracao condicionada a feature posterior
- [x] nenhum arquivo funcional de frontend, backend, ETL ou pipeline alterado

## User Stories da Feature

| US ID | Titulo | SP | Depende de | Status | Documento |
|---|---|---|---|---|---|
| US-9-01 | Decidir shell de importacao de leads | 1 | FEATURE-8 | ready_for_review | [README](./user-stories/US-9-01-DECIDIR-SHELL-IMPORTACAO-LEADS/README.md) |

## Follow-ups Deliberadamente Fora do Escopo

- migrar componentes puros para `features/leads/importacao`
- migrar o shell completo em fases
- reabrir importacao/ETL funcional
- habilitar `/dashboard/leads/conversao`

## Dependencias

- [PRD decisao shell importacao leads](../../PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md)
- [Intake decisao shell importacao leads](../../INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md)
- [Plano operacional](../../../plano_organizacao_import.md)
