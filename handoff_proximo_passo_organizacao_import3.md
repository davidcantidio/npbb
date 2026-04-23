# Handoff 3 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao de leads/importacao ja fechou quatro movimentos
incrementais:

- modularizou o router backend de leads, mantendo `backend/app/routers/leads.py`
  como agregador fino e preservando contratos sob `/leads`;
- consolidou a superficie frontend nao-import de leads em
  `frontend/src/features/leads`, mantendo wrappers legados em `pages/*` e
  `hooks/*`;
- consolidou os testes focados de lista/dashboard para importarem a
  implementacao real em `features/leads`;
- decidiu e executou a remocao do legado frontend nao roteado
  `frontend/src/pages/DashboardLeads.tsx` e do servico exclusivo
  `frontend/src/services/dashboard_leads.ts`, preservando o endpoint backend
  `/dashboard/leads/relatorio`.

O objetivo macro segue sendo reduzir acoplamento estrutural em passos pequenos,
reversiveis e sem reabrir importacao/ETL antes de existir escopo proprio.

## Referencia ao plano atual

Fonte principal desta frente:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- o overview afirma que `frontend/src/features/leads` ja e a fonte preferencial
  para lista, analise etaria e hook compartilhado;
- `DashboardLeads.tsx` e `services/dashboard_leads.ts` ja foram removidos em
  `FEATURE-4`;
- importacao/ETL seguem congelados;
- `rename-module` e o unico item ainda marcado como `deferred`:
  planejar rename de `app.modules.leads_publicidade` para nome de dominio
  neutro com camada de compatibilidade;
- o backlog posterior ainda lista:
  1. mover o restante do frontend de leads para `features/leads`;
  2. planejar remocao futura dos reexports temporarios;
  3. criar nova tela para `/dashboard/leads/conversao` somente se produto
     reabrir a pauta;
  4. planejar rename de `app.modules.leads_publicidade`;
  5. reabrir importacao/ETL apenas em sessao separada.

Como as pendencias de `features/leads` e do dashboard legado ja foram
resolvidas, o proximo passo mais coerente e **abrir uma rodada de governanca e
planejamento tecnico para o rename de `backend/app/modules/leads_publicidade`**,
sem executar o rename fisico ainda.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- A implementacao real foi quebrada em `backend/app/routers/leads_routes/`:
  - `public_intake.py`
  - `lead_records.py`
  - `references.py`
  - `classic_import.py`
  - `etl_import.py`
  - `batches.py`
- Os contratos publicos sob `/leads` foram preservados.
- `backend/app/modules/leads_publicidade/**` continua existindo e ainda e o
  modulo real consumido por routers, servicos, scripts e testes.

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

Rodada estrutural:

- `PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/`

Rodada frontend nao-import:

- `PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/`

Rodada dashboard legado:

- `PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/`

## Arquivos ja tocados

Arquivos/pastas relevantes ja alterados nesta frente:

- `plano_organizacao_import.md`
- `backend/app/routers/leads.py`
- `backend/app/routers/leads_routes/`
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
- `PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/`
- `PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/`
- `PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md`
- `PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/`
- `handoff_proximo_passo_organizacao_import.md`
- `handoff_proximo_passo_organizacao_import2.md`

Arquivos/pastas que devem continuar sem alteracao funcional no proximo passo:

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

## Estado atual do repositorio nesta frente

Validacoes registradas no plano:

- Backend da rodada estrutural anterior: `142 passed` nos testes focados.
- Frontend:
  - `cd frontend && npm run typecheck`: passou.
  - Suite focada lista/dashboard/manifesto: `27 passed`.
  - Rodada FEATURE-4:
    - `rg -n "DashboardLeads|dashboard_leads" frontend/src`: sem resultados.
    - `cd frontend && npm run typecheck`: passou.
    - suite focada dashboard/manifesto: `17 passed`.

Estado de arquitetura observado:

- `frontend/src/features/leads` e fonte real para lista, analise etaria e hook
  compartilhado.
- Wrappers legados continuam como borda de compatibilidade.
- `DashboardLeads.tsx` e `services/dashboard_leads.ts` nao existem mais em
  `frontend/src`.
- `dashboardManifest.ts` ainda contem `/dashboard/leads/conversao` com
  `enabled: false`.
- `backend/app/modules/leads_publicidade` ainda e o nome real do modulo de
  importacao/ETL de leads.
- Busca atual por `app.modules.leads_publicidade|leads_publicidade` mostra
  consumidores em:
  - `backend/app/routers/leads_routes/etl_import.py`
  - `backend/app/routers/leads_routes/classic_import.py`
  - `backend/app/services/lead_pipeline_service.py`
  - `backend/scripts/run_leads_worker.py`
  - varios testes backend de ETL, persistencia, warning policy, merge policy e
    endpoints
  - docs e governanca historica sob `docs/` e `PROJETOS/`

Residual conhecido:

- Smoke manual em browser ainda nao foi executado nesta frente:
  - `/leads`
  - `/dashboard/leads/analise-etaria`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` continua fora do gate.
- O worktree pode conter muitas alteracoes nao relacionadas; nao reverter nada
  que nao faca parte do recorte.

## Pendencias e lacunas

Pendencias abertas:

- Planejar rename de `backend/app/modules/leads_publicidade` para nome de
  dominio neutro com camada de compatibilidade.
- Definir nome alvo do modulo. O plano exige nome neutro, mas nao escolhe o
  identificador. Candidatos plausiveis a decidir em governanca:
  - `backend/app/modules/leads`
  - `backend/app/modules/lead_imports`
  - `backend/app/modules/leads_importacao`
- Definir estrategia de compatibilidade:
  - criar pacote novo e manter `leads_publicidade` como alias/reexport
    temporario;
  - ou apenas planejar a migracao em uma primeira rodada e executar em outra.
- Planejar quando remover wrappers temporarios de frontend.
- Reabrir importacao/ETL somente em sessao separada, com escopo proprio.

Lacunas que nao devem ser inventadas:

- Nao ha decisao de produto para habilitar `/dashboard/leads/conversao`.
- Nao ha decisao para recriar `DashboardLeads.tsx`.
- Nao ha decisao para reabrir importacao/ETL.
- Nao ha decisao registrada no plano sobre o nome alvo exato do rename de
  `app.modules.leads_publicidade`.
- Nao ha decisao para remover wrappers legados de `pages/*` e `hooks/*`.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **abrir uma feature
pequena de governanca e mapa tecnico para o rename de
`backend/app/modules/leads_publicidade`**, sem executar o rename fisico ainda.

Motivo:

- O item `rename-module` e o unico `deferred` explicito no topo de
  `plano_organizacao_import.md`.
- O frontend nao-import ja foi consolidado e o legado de dashboard ja foi
  removido.
- `leads_publicidade` aparece em caminhos de import reais de backend, scripts e
  testes; um rename direto e transversal e pode quebrar muita coisa.
- O proprio plano pede "planejar rename ... com camada de compatibilidade", o
  que indica que a proxima rodada deve decidir nome, superficie e estrategia de
  compat antes da execucao.

O que nao deve ser o proximo passo:

- Nao reabrir `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao habilitar `/dashboard/leads/conversao`.
- Nao recriar `DashboardLeads.tsx`.
- Nao remover wrappers legados de frontend.
- Nao executar rename fisico amplo sem feature propria, mapa de consumidores e
  estrategia de compatibilidade.

## Proxima acao recomendada

### Objetivo

Criar governanca propria e mapa de impacto para o rename de
`backend/app/modules/leads_publicidade`, escolhendo nome alvo e estrategia de
compatibilidade sem alterar ainda imports de producao.

### Escopo

Dentro:

- Mapear consumidores reais de `app.modules.leads_publicidade`.
- Decidir nome alvo do modulo de dominio neutro.
- Definir camada de compatibilidade temporaria para o caminho antigo.
- Criar governanca propria, provavelmente `FEATURE-5-*`, com intake, PRD,
  user story e tasks.
- Atualizar `plano_organizacao_import.md` para registrar que o rename foi
  planejado e qual sera a estrategia.

Fora:

- Executar o rename fisico do pacote nesta rodada de planejamento.
- Alterar contratos HTTP, schemas ou rotas.
- Alterar `lead_pipeline/` ou `core/leads_etl/`.
- Alterar frontend/importacao/ETL.
- Alterar `AppRoutes.tsx` ou `dashboardManifest.ts`.
- Recriar ou reabilitar qualquer dashboard legado.

### Arquivos mais provaveis de alteracao

- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-*.md`
- `PROJETOS/NPBB/PRD-*.md`
- `PROJETOS/NPBB/features/FEATURE-5-*/`
- possivelmente este handoff, apenas se a proxima sessao registrar resultado

Arquivos a mapear, mas preferencialmente nao alterar ainda:

- `backend/app/modules/leads_publicidade/**`
- `backend/app/routers/leads_routes/etl_import.py`
- `backend/app/routers/leads_routes/classic_import.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/scripts/run_leads_worker.py`
- `backend/tests/test_leads_import_etl_*.py`
- `backend/tests/test_etl_*.py`
- `backend/tests/test_lead_merge_policy.py`
- `backend/tests/test_lead_silver_mapping.py`
- `backend/tests/test_lead_ticketing_dedupe_postgres.py`

### Criterios de pronto

- Existe governanca propria para o rename (`FEATURE-5` ou equivalente).
- O nome alvo foi escolhido e registrado.
- A estrategia de compatibilidade foi registrada explicitamente.
- O mapa de consumidores de `leads_publicidade` foi anexado/resumido.
- `plano_organizacao_import.md` foi atualizado.
- Nenhum import de producao foi alterado ainda, salvo decisao explicita.
- Importacao/ETL, rotas, schemas, frontend e dashboard permanecem sem mudanca
  funcional.

### Riscos e validacoes necessarias

Riscos:

- Subestimar o alcance do rename: ha imports em routers, servicos, scripts e
  muitos testes.
- Quebrar patches/mocks de testes que usam paths string como
  `app.modules.leads_publicidade...`.
- Confundir planejamento do rename com refatoracao funcional de ETL.
- Mexer em `lead_pipeline/` ou `core/leads_etl/` sem escopo proprio.
- Criar pacote novo sem camada de compatibilidade e quebrar consumidores
  externos/internos ainda nao mapeados.

Validacoes:

- Antes de planejar, rodar:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
- Se qualquer arquivo de codigo for alterado por engano, rodar no minimo:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py`
- Se a rodada ficar apenas em governanca/plano, nao e necessario rodar suite
  funcional completa, mas registrar os comandos de mapeamento executados.

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler `handoff_proximo_passo_organizacao_import3.md`.
- [ ] Rodar `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md`.
- [ ] Mapear consumidores por categoria: producao, scripts, testes, docs e
      governanca historica.
- [ ] Escolher nome alvo neutro para o modulo.
- [ ] Definir camada de compatibilidade para o caminho antigo.
- [ ] Criar intake, PRD e FEATURE-5 dedicada ao rename.
- [ ] Atualizar `plano_organizacao_import.md` com decisao e estrategia.
- [ ] Nao executar rename fisico amplo nesta rodada, a menos que a sessao mude
      explicitamente o escopo e aceite o risco.
- [ ] Nao tocar em importacao/ETL funcional, frontend, rotas ou dashboard.
