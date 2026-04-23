---
doc_id: "TASK-1.md"
user_story_id: "US-4-01-ARQUIVAR-DASHBOARD-LEADS-LEGADO"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/pages/DashboardLeads.tsx"
  - "frontend/src/services/dashboard_leads.ts"
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md"
  - "PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md"
  - "PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/**"
tdd_aplicavel: false
---

# T1 - Remover superficie frontend orfa de DashboardLeads

## objetivo

Remover a tela frontend legada `DashboardLeads.tsx` e seu servico exclusivo
`dashboard_leads.ts`, mantendo rotas, manifesto, backend e importacao/ETL fora
de alteracao funcional.

## passos_atomicos

1. confirmar usos com `rg`
2. criar governanca propria da decisao
3. remover `frontend/src/pages/DashboardLeads.tsx`
4. remover `frontend/src/services/dashboard_leads.ts`
5. atualizar `plano_organizacao_import.md`
6. rodar typecheck e suite focada de dashboard/manifesto

## comandos_permitidos

- `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS plano_organizacao_import.md`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`

## stop_conditions

- parar se aparecer consumidor de codigo fonte alem dos dois arquivos removidos
- parar se a validacao exigir alteracao em `AppRoutes.tsx`,
  `dashboardManifest.ts`, backend ou importacao/ETL

## resultado

- 2026-04-23: `frontend/src/pages/DashboardLeads.tsx` removido.
- 2026-04-23: `frontend/src/services/dashboard_leads.ts` removido.
- `rg -n "DashboardLeads|dashboard_leads" frontend/src`: sem resultados apos a remocao.
- `cd frontend && npm run typecheck`: passou.
- `cd frontend && npm run test -- DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`: passou com `17 passed`.
- `AppRoutes.tsx`, `dashboardManifest.ts`, backend, wrappers legados e
  importacao/ETL permaneceram fora de alteracao funcional.
