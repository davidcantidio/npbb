---
doc_id: "TASK-3.md"
user_story_id: "US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD"
task_id: "T3"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
depends_on:
  - "T1"
parallel_safe: false
write_scope: []
tdd_aplicavel: false
---

# T3 - Validar typecheck e suites focadas do recorte

## objetivo

Confirmar que o novo slice `features/leads` preserva compilacao e o recorte de
testes combinado para lista, dashboard e manifesto.

## passos_atomicos

1. rodar `npm run typecheck`
2. rodar a suite focada do recorte
3. registrar que `ImportacaoPage.test.tsx` permanece fora do gate enquanto o
   freeze de importacao/ETL estiver ativo

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- LeadsListPage.test.tsx leadsListExport.test.ts leadsListQuarterPresets.test.ts DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`

## stop_conditions

- parar se os testes apontarem regressao funcional fora do recorte acordado

## resultado

- 2026-04-23: imports dos testes focados foram consolidados para
  `frontend/src/features/leads`.
- `cd frontend && npm run typecheck`: passou.
- `cd frontend && npm run test -- LeadsListPage.test.tsx leadsListExport.test.ts leadsListQuarterPresets.test.ts DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`: passou com `27 passed`.
- Wrappers legados, rotas, manifesto, `DashboardLeads.tsx` e importacao/ETL
  permaneceram fora de alteracao funcional.
