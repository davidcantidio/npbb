---
doc_id: "TASK-1.md"
user_story_id: "US-8-01-REMOVER-WRAPPERS-FRONTEND-LEADS"
task_id: "T1"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-04-23"
depends_on: []
parallel_safe: false
write_scope:
  - "frontend/src/app/AppRoutes.tsx"
  - "frontend/src/pages/leads/LeadsListPage.tsx"
  - "frontend/src/pages/leads/leadsListExport.ts"
  - "frontend/src/pages/leads/leadsListQuarterPresets.ts"
  - "frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx"
  - "frontend/src/pages/dashboard/useAgeAnalysisFilters.ts"
  - "frontend/src/hooks/useReferenciaEventos.ts"
  - "plano_organizacao_import.md"
  - "PROJETOS/NPBB/INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md"
  - "PROJETOS/NPBB/PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md"
  - "PROJETOS/NPBB/features/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS/**"
tdd_aplicavel: true
---

# T1 - Remover wrappers frontend leads nao-import

## objetivo

Remover wrappers legados nao-import de leads, mantendo lista e analise etaria
carregadas pelo slice `features/leads` e sem mudar comportamento funcional.

## passos_atomicos

1. confirmar consumidores dos wrappers legados com `rg`
2. ajustar `AppRoutes.tsx` para lazy imports nomeados do slice real
3. remover wrappers nao-import sem consumidores relevantes
4. atualizar governanca e `plano_organizacao_import.md`
5. executar buscas finais
6. executar validacoes focadas

## comandos_permitidos

- `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src`
- `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- `cd frontend && npm run typecheck`
- `cd frontend && npm test -- --run src/pages/__tests__/LeadsListPage.test.tsx src/pages/__tests__/leadsListExport.test.ts src/pages/__tests__/leadsListQuarterPresets.test.ts src/pages/dashboard/__tests__/DashboardModule.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx src/pages/dashboard/__tests__/dashboardManifest.test.ts`

## stop_conditions

- parar se aparecer consumidor ativo dos wrappers fora dos proprios wrappers e
  das rotas migradas
- parar se a rodada exigir alteracao em importacao/ETL funcional
- parar se houver necessidade de alterar contratos HTTP, schemas, backend,
  `lead_pipeline/` ou `core/leads_etl/`

## resultado

- 2026-04-23: busca inicial confirmou que os consumidores internos ja preferem
  `frontend/src/features/leads`, restando wrappers e duas lazy routes.
- 2026-04-23: `AppRoutes.tsx` passou a lazy-loadar `LeadsListPage` e
  `LeadsAgeAnalysisPage` a partir de `features/leads`.
- 2026-04-23: wrappers legados nao-import sem consumidores relevantes foram
  removidos.
- 2026-04-23: `/leads`, `/leads/importar` e
  `/dashboard/leads/analise-etaria` preservadas.
