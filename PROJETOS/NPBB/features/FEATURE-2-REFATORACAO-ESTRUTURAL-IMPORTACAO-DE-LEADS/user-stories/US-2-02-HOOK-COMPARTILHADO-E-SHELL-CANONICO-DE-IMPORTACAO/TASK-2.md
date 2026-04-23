---
doc_id: "TASK-2.md"
user_story_id: "US-2-02-HOOK-COMPARTILHADO-E-SHELL-CANONICO-DE-IMPORTACAO"
task_id: "T2"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "frontend/src/app/AppRoutes.tsx"
  - "frontend/src/pages/LeadsImport.tsx"
tdd_aplicavel: false
---

# T2 - Simplificar o lazy-load da rota de importacao e validar a trilha impactada

## objetivo

Eliminar o wrapper `LeadsImport.tsx` e fazer o shell canonico carregar
`ImportacaoPage` diretamente, mantendo `LegacyLeadStepRedirect` e os query
params atuais.

## passos_atomicos

1. trocar o lazy-load de `AppRoutes.tsx` para `pages/leads/ImportacaoPage`
2. remover o wrapper sem uso
3. validar typecheck e a suite impactada da trilha de leads/dashboard

## comandos_permitidos

- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- ImportacaoPage.test.tsx LegacyLeadStepRedirect.test.tsx MapeamentoPage.test.tsx BatchMapeamentoPage.test.tsx PipelineStatusPage.test.tsx LeadsListPage.test.tsx DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx --run`

## stop_conditions

- parar se os redirects legados deixarem de preservar `step`, `batch_id` ou
  query params suportados
