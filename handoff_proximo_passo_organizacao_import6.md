# Handoff 6 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao incremental de leads/importacao fechou a trilha
estrutural iniciada no plano:

- `backend/app/routers/leads.py` foi reduzido a agregador fino e as rotas reais
  foram separadas em `backend/app/routers/leads_routes/`;
- a superficie frontend nao-import de leads foi consolidada em
  `frontend/src/features/leads`;
- a tela/frontend legado `frontend/src/pages/DashboardLeads.tsx` e o servico
  `frontend/src/services/dashboard_leads.ts` foram removidos;
- o pacote backend de importacao foi renomeado para
  `backend/app/modules/lead_imports`;
- o alias temporario `backend/app/modules/leads_publicidade` foi removido em
  `FEATURE-7`;
- importacao/ETL funcional continua congelada.

O estado atual deixa uma proxima frente estrutural clara: **reduzir os wrappers
frontend legados que ainda apontam para `features/leads`**, sem mexer em
importacao/ETL nem nos componentes de importacao.

## Referencia ao plano atual

Fonte principal:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- todos os itens do frontmatter `todos` estao `done`, incluindo:
  - `rename-module`
  - `rename-module-implementation`
  - `remove-legacy-alias`
- o overview afirma que:
  - `app.modules.lead_imports` e o unico caminho backend real;
  - `app.modules.leads_publicidade` foi limpo em `FEATURE-7`;
  - lista, analise etaria e hook compartilhado moram em
    `frontend/src/features/leads`;
  - wrappers legados em `pages/*` e `hooks/*` ainda existem;
  - importacao/ETL seguem congelados.
- a secao "Backlog posterior, mas nao agora" lista como primeiro item:
  mover o restante do frontend de leads para `features/leads`.

Conclusao direta: o proximo passo coerente nao e reabrir ETL/importacao nem
criar nova limpeza backend. E abrir uma feature pequena para **eliminar ou
reduzir a dependencia das rotas e imports no frontend sobre wrappers legados
nao-import**, validando por busca que os consumidores ja usam o slice real.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- Implementacao real das rotas de leads esta em:
  - `backend/app/routers/leads_routes/public_intake.py`
  - `backend/app/routers/leads_routes/lead_records.py`
  - `backend/app/routers/leads_routes/references.py`
  - `backend/app/routers/leads_routes/classic_import.py`
  - `backend/app/routers/leads_routes/etl_import.py`
  - `backend/app/routers/leads_routes/batches.py`
- Contratos publicos sob `/leads` foram preservados.
- `backend/app/modules/lead_imports` e o pacote real.
- `backend/app/modules/leads_publicidade` foi removido.
- `backend/tests/test_lead_imports_compat.py` foi removido.
- Consumidores ativos usam `app.modules.lead_imports`, incluindo:
  - `backend/app/routers/leads_routes/classic_import.py`
  - `backend/app/routers/leads_routes/etl_import.py`
  - `backend/app/services/lead_pipeline_service.py`
  - `backend/scripts/run_leads_worker.py`
  - testes focados de ETL/importacao.

### Frontend nao-import

Implementacao real consolidada em:

- `frontend/src/features/leads/index.ts`
- `frontend/src/features/leads/list/LeadsListPage.tsx`
- `frontend/src/features/leads/list/leadsListExport.ts`
- `frontend/src/features/leads/list/leadsListQuarterPresets.ts`
- `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/features/leads/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/features/leads/shared/useReferenciaEventos.ts`

Wrappers legados ainda existem:

- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`

Busca atual confirma que `frontend/src/app/AppRoutes.tsx` ainda lazy-loada:

- `../pages/dashboard/LeadsAgeAnalysisPage`
- `../pages/leads/LeadsListPage`

Enquanto isso, testes focados ja importam a implementacao real por
`frontend/src/features/leads`.

### Dashboard

- `/dashboard/leads/analise-etaria` segue como rota de tela atual.
- `/dashboard/leads/conversao` segue sem decisao para habilitacao.
- `frontend/src/pages/DashboardLeads.tsx` foi removido.
- `frontend/src/services/dashboard_leads.ts` foi removido.
- Endpoint backend `GET /dashboard/leads/relatorio` segue preservado como
  API/script sem tela roteada.
- O ultimo commit tambem alterou arquivos de dashboard/analise etaria fora do
  escopo original deste handoff, mas eles ja estao commitados:
  - `backend/app/schemas/dashboard.py`
  - `backend/app/services/dashboard_service.py`
  - `backend/tests/test_dashboard_age_analysis_service.py`
  - `frontend/src/components/dashboard/AgeAnalysisKpiGrid.tsx`
  - `frontend/src/components/dashboard/__tests__/AgeAnalysisKpiGrid.test.tsx`
  - `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`
  - `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
  - `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
  - `frontend/src/pages/dashboard/__tests__/ageAnalysisFixtures.ts`
  - `frontend/src/types/dashboard.ts`

### Governanca

Rodadas abertas/concluidas nesta frente:

- `PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/`
- `PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/`
- `PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/`
- `PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/`
- `PROJETOS/NPBB/INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/features/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS/`
- `PROJETOS/NPBB/INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
- `PROJETOS/NPBB/PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
- `PROJETOS/NPBB/features/FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE/`

## Arquivos ja tocados

Arquivos/pastas relevantes ja alterados nesta frente:

- `plano_organizacao_import.md`
- `backend/app/routers/leads.py`
- `backend/app/routers/leads_routes/`
- `backend/app/modules/lead_imports/**`
- `backend/app/modules/leads_publicidade/**` (removido)
- `backend/app/services/lead_pipeline_service.py`
- `backend/scripts/run_leads_worker.py`
- `backend/tests/test_lead_imports_compat.py` (removido)
- testes backend focados de ETL/importacao, incluindo:
  - `backend/tests/test_etl_rejection_reasons.py`
  - `backend/tests/test_etl_import_validators.py`
  - `backend/tests/test_etl_import_persistence.py`
  - `backend/tests/test_etl_csv_delimiter.py`
  - `backend/tests/test_lead_ticketing_dedupe_postgres.py`
  - `backend/tests/test_lead_silver_mapping.py`
  - `backend/tests/test_lead_merge_policy.py`
  - `backend/tests/test_leads_import_etl_warning_policy.py`
  - `backend/tests/test_leads_import_etl_usecases.py`
  - `backend/tests/test_leads_import_etl_staging_repository.py`
  - `backend/tests/test_leads_import_etl_endpoint.py`
- `docs/WORKFLOWS.md`
- `docs/MANUAL-NPBB.md`
- `docs/tela-inicial/menu/Dashboard/leads_dashboard.md`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/features/leads/**`
- `frontend/src/hooks/useReferenciaEventos.ts`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- testes frontend focados de lista/dashboard/manifesto.

Arquivos que devem continuar fora do proximo passo, salvo nova decisao
explicita:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `lead_pipeline/`
- `core/leads_etl/`
- contratos HTTP, schemas e rotas publicas
- regras de ETL, persistencia, validadores e merge policy

## Estado atual do repositorio nesta frente

- Worktree estava limpo antes da criacao deste handoff.
- Ultimo commit observado:
  - `39ed978 Finalize lead import cleanup`
- Branch atual observada:
  - `audit/leads-import-enterprise-hardening`
- Push anterior realizado para:
  - `origin/audit/leads-import-enterprise-hardening`
- Validacoes registradas no plano:
  - `FEATURE-7`: suite backend focada com `134 passed, 1 skipped`.
  - `FEATURE-6`: suite backend focada com `136 passed, 1 skipped`.
  - frontend consolidacao/lista/dashboard: `npm run typecheck` passou e suite
    focada registrou `27 passed`.
- Busca atual para consumidores ativos do caminho backend legado:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests -g "!backend/app/modules/leads_publicidade/**" -g "!backend/tests/test_lead_imports_compat.py"`
  - resultado: sem ocorrencias.
- `Test-Path backend/app/modules/leads_publicidade`: `False`.
- `Test-Path backend/tests/test_lead_imports_compat.py`: `False`.

## Pendencias e lacunas

Pendencias abertas:

- Abrir feature propria, provavelmente `FEATURE-8-*`, para reduzir wrappers
  frontend legados nao-import.
- Confirmar por busca se ainda ha consumidores reais dos wrappers:
  - `frontend/src/pages/leads/LeadsListPage.tsx`
  - `frontend/src/pages/leads/leadsListExport.ts`
  - `frontend/src/pages/leads/leadsListQuarterPresets.ts`
  - `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
  - `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
  - `frontend/src/hooks/useReferenciaEventos.ts`
- Atualizar `frontend/src/app/AppRoutes.tsx` para lazy-loadar diretamente de
  `frontend/src/features/leads`, se a busca confirmar que isso e seguro.
- Decidir, na propria feature, se wrappers nao roteados podem ser removidos ou
  se devem permanecer por compatibilidade externa.
- Atualizar testes focados se algum teste ainda importar wrapper legado.
- Atualizar `plano_organizacao_import.md` com o resultado da rodada.

Lacunas que nao devem ser inventadas:

- Nao ha decisao para mover `ImportacaoPage.tsx` para `features/leads`.
- Nao ha decisao para mexer em `frontend/src/pages/leads/importacao/**`.
- Nao ha decisao para reabrir ETL funcional.
- Nao ha decisao para habilitar `/dashboard/leads/conversao`.
- Nao ha decisao para recriar `DashboardLeads.tsx`.
- Nao ha evidencia no plano de smoke manual em browser para `/leads` ou
  `/dashboard/leads/analise-etaria`.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **abrir uma feature
pequena para remover a dependencia das rotas e imports internos do frontend
nao-import sobre wrappers legados**, mantendo a implementacao real em
`frontend/src/features/leads`.

Motivo:

- O backend estrutural ja esta limpo: `app.modules.lead_imports` e unico caminho
  real e `leads_publicidade` foi removido.
- O plano lista como backlog seguinte "mover o restante do frontend de leads
  para `features/leads`".
- A implementacao real de lista, analise etaria e hook compartilhado ja esta no
  slice `features/leads`.
- As rotas ainda entram por wrappers em `pages/*`, especialmente:
  - `frontend/src/app/AppRoutes.tsx` -> `../pages/leads/LeadsListPage`
  - `frontend/src/app/AppRoutes.tsx` -> `../pages/dashboard/LeadsAgeAnalysisPage`
- Essa rodada pode ser pequena, reversivel e sem tocar em importacao/ETL.

O que nao deve ser o proximo passo:

- Nao mover `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao alterar contratos HTTP, schemas ou rotas publicas.
- Nao habilitar `/dashboard/leads/conversao`.
- Nao recriar `DashboardLeads.tsx`.
- Nao recriar `app.modules.leads_publicidade`.

## Proxima acao recomendada

### Objetivo

Executar uma rodada controlada de organizacao frontend nao-import:

- abrir governanca `FEATURE-8` ou equivalente;
- confirmar consumidores dos wrappers legados por busca;
- fazer `AppRoutes.tsx` importar as telas diretamente de
  `frontend/src/features/leads`;
- remover wrappers nao roteados se a busca confirmar ausencia de consumidores;
- manter `/leads`, `/dashboard/leads/analise-etaria` e `/leads/importar`
  funcionalmente iguais.

### Escopo

Dentro:

- Governanca nova, provavelmente:
  - `PROJETOS/NPBB/INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
  - `PROJETOS/NPBB/PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
  - `PROJETOS/NPBB/features/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS/`
- Busca antes de editar:
  - `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src`
- Possivel ajuste em:
  - `frontend/src/app/AppRoutes.tsx`
  - wrappers legados nao-import em `frontend/src/pages/leads/`,
    `frontend/src/pages/dashboard/` e `frontend/src/hooks/`
  - testes focados que ainda dependam de caminhos legados
  - `plano_organizacao_import.md`

Fora:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- ETL funcional, Bronze, mapeamento e pipeline
- backend de importacao, `lead_pipeline/`, `core/leads_etl/`
- contratos HTTP, schemas e rotas publicas

### Arquivos mais provaveis de alteracao

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`
- testes focados em:
  - `frontend/src/pages/__tests__/LeadsListPage.test.tsx`
  - `frontend/src/pages/__tests__/leadsListExport.test.ts`
  - `frontend/src/pages/__tests__/leadsListQuarterPresets.test.ts`
  - `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
  - `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
  - `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
- `plano_organizacao_import.md`
- nova governanca `PROJETOS/NPBB/features/FEATURE-8-*/`

### Criterios de pronto

- Busca confirma que rotas e testes internos preferem `frontend/src/features/leads`.
- `AppRoutes.tsx` nao depende mais dos wrappers de lista e analise etaria, se a
  feature decidir removelos.
- Wrappers legados nao-import foram removidos ou mantidos por motivo objetivo
  registrado na feature.
- `/leads`, `/leads/importar` e `/dashboard/leads/analise-etaria` preservam o
  mesmo contrato de rota.
- Nenhum arquivo de importacao/ETL funcional foi alterado.
- `plano_organizacao_import.md` registra resultado, validacoes e residual.

### Riscos e validacoes necessarias

Riscos:

- Remover wrapper ainda usado por rota, teste ou import externo nao mapeado.
- Confundir wrappers nao-import com o shell de importacao.
- Puxar `ImportacaoPage.tsx`, `MapeamentoPage`, `BatchMapeamentoPage` ou
  `PipelineStatusPage` para dentro da rodada.
- Alterar dashboard funcional em vez de apenas origem de import/rota.
- Quebrar lazy loading por falta de default export no slice `features/leads`.

Validacoes minimas:

- Antes/depois:
  - `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src`
  - `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- Frontend:
  - `cd frontend && npm run typecheck`
  - suite focada lista/dashboard/manifesto usada nas rodadas anteriores.
- Se `AppRoutes.tsx` passar a importar direto de `features/leads`, validar que
  o modulo exporta default ou ajustar com import nomeado via `then`.

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler este handoff.
- [ ] Conferir `git status --short`.
- [ ] Confirmar que `backend/app/modules/leads_publicidade` continua ausente.
- [ ] Rodar a busca de wrappers frontend antes de editar.
- [ ] Abrir governanca `FEATURE-8` para a limpeza frontend nao-import.
- [ ] Ajustar `frontend/src/app/AppRoutes.tsx` somente se o slice
      `features/leads` suportar lazy import com seguranca.
- [ ] Remover wrappers legados nao-import apenas se busca confirmar ausencia de
      consumidores relevantes.
- [ ] Nao tocar em `ImportacaoPage.tsx`, `frontend/src/pages/leads/importacao/**`,
      `lead_pipeline/`, `core/leads_etl/` ou contratos HTTP.
- [ ] Rodar `cd frontend && npm run typecheck`.
- [ ] Rodar suites focadas de lista/dashboard/manifesto.
- [ ] Atualizar `plano_organizacao_import.md` com resultado e residual.
