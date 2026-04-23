# Handoff 5 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao incremental de leads/importacao ja fechou seis
movimentos principais:

- modularizou o router backend de leads, mantendo `backend/app/routers/leads.py`
  como agregador fino e preservando contratos sob `/leads`;
- consolidou a superficie frontend nao-import em
  `frontend/src/features/leads`, mantendo wrappers legados em `pages/*` e
  `hooks/*`;
- consolidou testes focados de lista/dashboard para importarem a implementacao
  real em `features/leads`;
- removeu o legado frontend nao roteado `frontend/src/pages/DashboardLeads.tsx`
  e o servico exclusivo `frontend/src/services/dashboard_leads.ts`, preservando
  o endpoint backend `/dashboard/leads/relatorio`;
- planejou em `FEATURE-5` o rename de `app.modules.leads_publicidade` para
  `app.modules.lead_imports`;
- implementou em `FEATURE-6` o rename backend, tornando
  `app.modules.lead_imports` o caminho real e mantendo
  `app.modules.leads_publicidade` como camada temporaria de compatibilidade.

O objetivo macro continua sendo reduzir acoplamento estrutural em passos
pequenos, reversiveis e sem reabrir importacao/ETL funcional antes de existir
escopo proprio.

## Referencia ao plano atual

Fonte principal desta frente:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- todos os itens do frontmatter `todos` estao `done`, incluindo:
  - `rename-module`
  - `rename-module-implementation`
- o overview afirma que:
  - `frontend/src/features/leads` e a fonte preferencial para lista, analise
    etaria e hook compartilhado;
  - `DashboardLeads.tsx` e `services/dashboard_leads.ts` foram removidos em
    `FEATURE-4`;
  - o rename backend foi planejado em `FEATURE-5` e implementado em
    `FEATURE-6`;
  - `app.modules.lead_imports` e o pacote real;
  - `app.modules.leads_publicidade` segue como compatibilidade temporaria;
  - importacao/ETL seguem congelados.
- a secao "Backlog posterior, mas nao agora" lista como proximo tema tecnico:
  planejar a remocao dos shims temporarios de
  `app.modules.leads_publicidade` quando a busca confirmar ausencia de
  consumidores legados.

Conclusao direta: a proxima sessao nao deve replanejar nem reexecutar o rename.
O rename ja aconteceu. O proximo passo coerente e abrir uma feature pequena para
remover o alias antigo `app.modules.leads_publicidade`, mas somente se uma busca
confirmar que nao ha consumidores ativos fora da propria compatibilidade, testes
de compatibilidade e docs/governanca historicas.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- A implementacao real das rotas de leads foi quebrada em
  `backend/app/routers/leads_routes/`:
  - `public_intake.py`
  - `lead_records.py`
  - `references.py`
  - `classic_import.py`
  - `etl_import.py`
  - `batches.py`
- Os contratos publicos sob `/leads` foram preservados.
- `backend/app/modules/lead_imports` e o pacote real de importacao/ETL.
- `backend/app/modules/leads_publicidade` permanece como compatibilidade
  temporaria por shims.
- Os imports ativos de producao, script worker e testes focados foram migrados
  para `app.modules.lead_imports`.
- Imports absolutos internos no pacote real usam `app.modules.lead_imports`,
  por exemplo:
  - `backend/app/modules/lead_imports/application/etl_import/preview_service.py`
  - `backend/app/modules/lead_imports/application/etl_import/persistence.py`
- O teste `backend/tests/test_lead_imports_compat.py` cobre:
  - import profundo legado por `app.modules.leads_publicidade...`;
  - monkeypatch por string no caminho legado atingindo o modulo real.

### Compatibilidade temporaria backend

O pacote antigo continua existindo por design:

- `backend/app/modules/leads_publicidade/_compat.py`
- `backend/app/modules/leads_publicidade/__init__.py`
- `backend/app/modules/leads_publicidade/application/__init__.py`
- `backend/app/modules/leads_publicidade/application/etl_import/__init__.py`
- modulos folha em `backend/app/modules/leads_publicidade/application/**`

Cada modulo folha antigo aponta para o modulo real correspondente em
`app.modules.lead_imports` via helper de compatibilidade. Essa camada nao deve
receber funcionalidade nova.

### Frontend - importacao congelada

- `/leads/importar` continua apontando para
  `frontend/src/pages/leads/ImportacaoPage.tsx`.
- `frontend/src/pages/leads/importacao/**`, Bronze, ETL, mapeamento e pipeline
  continuam fora desta frente.
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` segue fora do gate
  enquanto o freeze de importacao/ETL estiver ativo.

### Frontend - slice nao-import consolidado

A implementacao real da superficie nao-import de leads esta em:

- `frontend/src/features/leads/index.ts`
- `frontend/src/features/leads/list/LeadsListPage.tsx`
- `frontend/src/features/leads/list/leadsListExport.ts`
- `frontend/src/features/leads/list/leadsListQuarterPresets.ts`
- `frontend/src/features/leads/list/index.ts`
- `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/features/leads/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/features/leads/dashboard/index.ts`
- `frontend/src/features/leads/shared/useReferenciaEventos.ts`
- `frontend/src/features/leads/shared/index.ts`

Wrappers legados ainda existem e devem permanecer por enquanto:

- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`

### Dashboard

- `frontend/src/app/AppRoutes.tsx` permanece funcionalmente igual para esta
  frente.
- `/dashboard/leads/analise-etaria` segue como rota de tela atual.
- `/dashboard/leads/conversao` segue apenas como entrada desabilitada em
  `frontend/src/config/dashboardManifest.ts` e teste associado.
- `frontend/src/pages/DashboardLeads.tsx` foi removido.
- `frontend/src/services/dashboard_leads.ts` foi removido.
- O endpoint backend `GET /dashboard/leads/relatorio` segue vivo como
  API/script sem tela roteada.

### Governanca

Rodadas ja abertas:

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

Decisao da `FEATURE-6`:

- caminho real: `app.modules.lead_imports`;
- caminho legado temporario: `app.modules.leads_publicidade`;
- compatibilidade profunda preservada por shims;
- remocao do alias antigo adiada para feature posterior;
- importacao/ETL funcional, contratos HTTP, frontend, dashboard,
  `lead_pipeline/` e `core/leads_etl/` ficaram fora do escopo.

## Arquivos ja tocados

Arquivos/pastas relevantes ja alterados nesta frente:

- `plano_organizacao_import.md`
- `backend/app/routers/leads.py`
- `backend/app/routers/leads_routes/`
- `backend/app/modules/lead_imports/**`
- `backend/app/modules/leads_publicidade/**`
- `backend/app/services/lead_pipeline_service.py`
- `backend/scripts/run_leads_worker.py`
- `backend/tests/test_lead_imports_compat.py`
- testes backend focados migrados para `app.modules.lead_imports`:
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
- `frontend/src/features/leads/`
- `frontend/src/hooks/useReferenciaEventos.ts`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/pages/__tests__/LeadsListPage.test.tsx`
- `frontend/src/pages/__tests__/leadsListExport.test.ts`
- `frontend/src/pages/__tests__/leadsListQuarterPresets.test.ts`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
- `frontend/src/config/__tests__/dashboardManifest.test.ts`
- `frontend/src/pages/DashboardLeads.tsx` (removido)
- `frontend/src/services/dashboard_leads.ts` (removido)
- governanca `FEATURE-5` e `FEATURE-6`
- handoffs anteriores:
  - `handoff_proximo_passo_organizacao_import.md`
  - `handoff_proximo_passo_organizacao_import2.md`
  - `handoff_proximo_passo_organizacao_import3.md`
  - `handoff_proximo_passo_organizacao_import4.md`

Arquivos/pastas que devem continuar sem alteracao funcional no proximo passo,
salvo decisao explicita nova:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/config/dashboardManifest.ts`
- `lead_pipeline/`
- `core/leads_etl/`
- contratos HTTP, schemas e rotas publicas
- regras de ETL, persistencia, validadores e merge policy

## Estado atual do repositorio nesta frente

Validacoes registradas em `plano_organizacao_import.md`:

- Backend da rodada estrutural anterior:
  - testes focados com `142 passed`;
  - validacao adicional de `backend/tests/test_lead_gold_pipeline.py` com
    `75 passed`.
- Frontend:
  - `cd frontend && npm run typecheck`: passou;
  - suite focada lista/dashboard/manifesto: `27 passed`;
  - suite focada dashboard/manifesto na `FEATURE-4`: `17 passed`.
- Rodada `FEATURE-5`:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
    usado para mapear consumidores;
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
    usado para confirmar estrutura do pacote antigo;
  - nenhuma suite funcional foi exigida porque a rodada foi documental.
- Rodada `FEATURE-6`:
  - `backend/app/modules/lead_imports` criado como pacote real;
  - `backend/app/modules/leads_publicidade` transformado em compatibilidade;
  - imports ativos migrados para `app.modules.lead_imports`;
  - `backend/tests/test_lead_imports_compat.py` adicionado;
  - suite focada backend executada com `136 passed, 1 skipped`.

Estado observado por busca apos `FEATURE-6`:

- `app.modules.lead_imports` aparece em routers, worker, servicos, testes e no
  pacote real.
- `app.modules.leads_publicidade` aparece em:
  - shims de `backend/app/modules/leads_publicidade/**`;
  - `backend/tests/test_lead_imports_compat.py`;
  - docs/governanca historicas;
  - `plano_organizacao_import.md` como registro de contexto e residual.
- Nao ha evidencia no plano de que o alias antigo ja possa ser removido sem
  uma rodada propria de verificacao.

Estado de worktree relevante no momento da criacao deste handoff:

- Existem alteracoes backend/governanca da `FEATURE-6` ainda no worktree.
- Tambem aparecem alteracoes frontend fora do escopo desta frente no `git
  status`, incluindo:
  - `frontend/src/components/dashboard/ConsolidatedPanel.tsx` (deleted)
  - `frontend/src/components/dashboard/__tests__/ConsolidatedPanel.test.tsx`
    (deleted)
  - `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`
  - `frontend/src/utils/ageAnalysisViewModel.ts`
- Este handoff nao assume autoria nem validade dessas alteracoes frontend. A
  proxima sessao deve tratar esses arquivos como mudancas possivelmente
  paralelas do usuario e nao deve revertê-las sem instrucao explicita.

## Pendencias e lacunas

Pendencias abertas:

- Abrir feature propria para remocao do alias temporario
  `app.modules.leads_publicidade`, provavelmente `FEATURE-7-*`.
- Confirmar por busca que nao ha consumidores ativos do caminho antigo fora de:
  - shims de compatibilidade;
  - teste explicito de compatibilidade;
  - docs/governanca historicas;
  - plano/handoff.
- Remover `backend/app/modules/leads_publicidade/**` apenas apos essa
  confirmacao e validacao focada.
- Remover ou adaptar `backend/tests/test_lead_imports_compat.py` na mesma
  rodada em que o alias for removido.
- Atualizar `plano_organizacao_import.md` para registrar a remocao do alias,
  caso ela seja executada.
- Planejar remocao futura dos wrappers temporarios frontend.
- Reabrir importacao/ETL somente em sessao separada, com escopo proprio.

Lacunas que nao devem ser inventadas:

- Nao ha decisao para habilitar `/dashboard/leads/conversao`.
- Nao ha decisao para recriar `DashboardLeads.tsx`.
- Nao ha decisao para reabrir importacao/ETL funcional.
- Nao ha decisao para remover wrappers legados de `pages/*` e `hooks/*`.
- Nao ha decisao para mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao ha evidencia de smoke manual em browser para `/leads` ou
  `/dashboard/leads/analise-etaria` nas rodadas recentes.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **abrir e executar uma
feature pequena de limpeza do alias legado `app.modules.leads_publicidade`**,
desde que a busca inicial confirme que nao ha consumidores ativos fora da
compatibilidade e do teste dedicado.

Motivo:

- `FEATURE-5` ja planejou o rename.
- `FEATURE-6` ja implementou o rename e migrou consumidores ativos para
  `app.modules.lead_imports`.
- O plano atual explicitamente lista como backlog posterior a remocao dos shims
  temporarios quando a busca confirmar ausencia de consumidores legados.
- Manter o alias antigo por muito tempo reabre a ambiguidade estrutural que o
  rename resolveu.
- Remover o alias agora deve ser uma rodada propria porque envolve deletar uma
  superficie importavel e ajustar o teste de compatibilidade.

O que nao deve ser o proximo passo:

- Nao reabrir `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao alterar regras de ETL, persistencia, validadores ou merge policy.
- Nao habilitar `/dashboard/leads/conversao`.
- Nao recriar `DashboardLeads.tsx`.
- Nao remover wrappers legados de frontend.
- Nao mexer nas alteracoes frontend atualmente pendentes sem escopo proprio.

## Proxima acao recomendada

### Objetivo

Executar uma rodada controlada de remocao da compatibilidade temporaria:

- confirmar que `app.modules.leads_publicidade` nao tem consumidores ativos;
- remover `backend/app/modules/leads_publicidade/**`;
- remover ou substituir o teste de compatibilidade legado;
- preservar `backend/app/modules/lead_imports` como unico caminho backend real;
- manter contratos HTTP, rotas, schemas, persistencia e comportamento de ETL
  inalterados.

### Escopo

Dentro:

- Criar governanca propria, provavelmente:
  - `PROJETOS/NPBB/INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
  - `PROJETOS/NPBB/PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
  - `PROJETOS/NPBB/features/FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE/`
- Confirmar consumidores com `rg` antes de editar.
- Remover `backend/app/modules/leads_publicidade/**` se a busca estiver limpa.
- Remover `backend/tests/test_lead_imports_compat.py` ou trocar por teste que
  garanta ausencia do caminho antigo, conforme a decisao da feature.
- Atualizar `plano_organizacao_import.md` com resultado, validacoes e residual.

Fora:

- Alterar `backend/app/modules/lead_imports/**` funcionalmente.
- Alterar regras de ETL, persistencia, validadores ou merge policy.
- Alterar contratos HTTP, schemas ou rotas.
- Alterar frontend, dashboard ou manifesto.
- Alterar `lead_pipeline/` ou `core/leads_etl/`.
- Editar docs/governanca historicas antigas apenas para trocar referencias
  historicas.
- Tocar em mudancas frontend pendentes no worktree sem decisao explicita.

### Arquivos mais provaveis de alteracao

- `plano_organizacao_import.md`
- `backend/app/modules/leads_publicidade/**` (remocao)
- `backend/tests/test_lead_imports_compat.py`
- nova governanca `PROJETOS/NPBB/features/FEATURE-7-*/`
- possivelmente novos documentos:
  - `PROJETOS/NPBB/INTAKE-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`
  - `PROJETOS/NPBB/PRD-REMOCAO-ALIAS-LEADS-PUBLICIDADE.md`

Arquivos que provavelmente nao devem ser alterados:

- `backend/app/modules/lead_imports/**`, salvo ajuste documental minimo se
  aparecer referencia antiga inesperada.
- `backend/app/routers/leads_routes/**`, se a busca ja estiver limpa.
- `backend/app/services/lead_pipeline_service.py`, se a busca ja estiver limpa.
- `backend/scripts/run_leads_worker.py`, se a busca ja estiver limpa.
- `frontend/**`.

### Criterios de pronto

- Busca por `app.modules.leads_publicidade` em codigo ativo nao mostra
  consumidores de producao, scripts ou testes funcionais.
- `backend/app/modules/leads_publicidade` foi removido ou teve remocao
  deliberadamente adiada por consumidor encontrado.
- `backend/tests/test_lead_imports_compat.py` foi removido/adaptado de acordo
  com a decisao da rodada.
- `app.modules.lead_imports` permanece importavel e usado por consumidores
  ativos.
- Rotas `/leads`, `/leads/importar`, `/dashboard/leads/analise-etaria` e
  `/dashboard/leads/relatorio` permanecem sem mudanca de contrato.
- `plano_organizacao_import.md` registra a remocao ou o motivo objetivo para
  adiar a remocao.

### Riscos e validacoes necessarias

Riscos:

- Algum consumidor legado nao mapeado ainda importar
  `app.modules.leads_publicidade`.
- Patches por string antigos existirem fora de `backend/tests` ou em scripts
  nao cobertos pela busca inicial.
- Remover docs historicas que deveriam permanecer como evidencia.
- Misturar esta limpeza backend com alteracoes frontend pendentes no worktree.
- Reabrir ETL funcional por acidente.

Validacoes minimas:

- Antes/depois:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
  - `rg -n "app\\.modules\\.lead_imports|lead_imports" backend/app backend/scripts backend/tests`
  - `Test-Path backend/app/modules/leads_publicidade`
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/lead_imports`
- Testes backend focados apos remocao:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`
- Se a remocao de alias for adiada por consumidor encontrado, registrar no
  plano o caminho exato do consumidor e nao remover parcialmente o pacote
  legado.

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler este handoff.
- [ ] Ler `PROJETOS/NPBB/PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`.
- [ ] Ler `PROJETOS/NPBB/features/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`.
- [ ] Conferir `git status --short` e separar mudancas frontend pendentes do
      escopo backend.
- [ ] Confirmar consumidores antigos com `rg` antes de editar.
- [ ] Se a busca estiver limpa, abrir governanca `FEATURE-7` ou equivalente.
- [ ] Remover `backend/app/modules/leads_publicidade/**` somente em rodada
      propria.
- [ ] Remover/adaptar `backend/tests/test_lead_imports_compat.py`.
- [ ] Nao tocar em frontend, dashboard, `lead_pipeline/`, `core/leads_etl/` ou
      contratos HTTP.
- [ ] Rodar validacoes backend focadas.
- [ ] Atualizar `plano_organizacao_import.md` com resultado e residual.
