---
doc_id: "TASK-1.md"
user_story_id: "US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD"
task_id: "T1"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/features/leads/"
  - "frontend/src/pages/leads/LeadsListPage.tsx"
  - "frontend/src/pages/leads/leadsListExport.ts"
  - "frontend/src/pages/leads/leadsListQuarterPresets.ts"
  - "frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx"
  - "frontend/src/pages/dashboard/useAgeAnalysisFilters.ts"
  - "frontend/src/hooks/useReferenciaEventos.ts"
tdd_aplicavel: false
---

# T1 - Criar o slice `features/leads` e mover a implementacao nao-import

## objetivo

Abrir `frontend/src/features/leads/` e mover para la a implementacao atual da
lista, analise etaria, hook compartilhado e helpers da lista, mantendo
wrappers finos nos caminhos legados.

## passos_atomicos

1. criar `features/leads/list`, `features/leads/dashboard` e
   `features/leads/shared`
2. mover a implementacao atual para o novo slice
3. substituir os caminhos legados por reexports temporarios

## comandos_permitidos

- `rg -n "LeadsListPage|LeadsAgeAnalysisPage|useReferenciaEventos" frontend/src`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o move exigir mudar comportamento, textos, query params ou rotas
