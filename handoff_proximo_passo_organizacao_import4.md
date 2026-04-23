# Handoff 4 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao incremental de leads/importacao ja fechou cinco
movimentos:

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
- planejou em `FEATURE-5` o rename futuro de
  `app.modules.leads_publicidade` para `app.modules.lead_imports`, com camada
  temporaria de compatibilidade.

O objetivo macro continua sendo reduzir acoplamento estrutural em passos
pequenos, reversiveis e sem reabrir importacao/ETL funcional antes de existir
escopo proprio.

## Referencia ao plano atual

Fonte principal desta frente:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- todos os itens do frontmatter `todos` estao `done`, inclusive
  `rename-module`;
- o overview afirma que:
  - `frontend/src/features/leads` e a fonte preferencial para lista, analise
    etaria e hook compartilhado;
  - `DashboardLeads.tsx` e `services/dashboard_leads.ts` foram removidos em
    `FEATURE-4`;
  - o rename de `app.modules.leads_publicidade` foi planejado em `FEATURE-5`
    para o alvo `app.modules.lead_imports`, sem rename fisico ainda;
  - importacao/ETL seguem congelados;
- a secao "Backlog posterior, mas nao agora" lista como proximo tema tecnico:
  executar em feature propria o rename planejado de
  `app.modules.leads_publicidade` para `app.modules.lead_imports`, com
  alias/reexport temporario.

Conclusao direta: a proxima sessao nao deve voltar a planejar o nome do modulo.
A decisao ja existe. O proximo passo coerente e abrir uma feature de
implementacao controlada do rename, criando o pacote novo e preservando o
caminho antigo como compatibilidade temporaria.

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
- `backend/app/modules/leads_publicidade/**` continua sendo o pacote real de
  importacao/ETL de leads.
- `backend/app/modules/lead_imports` ainda nao existe.
- Nenhum import Python foi migrado para `app.modules.lead_imports`.

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

Decisao da `FEATURE-5`:

- nome alvo aprovado: `app.modules.lead_imports`;
- estrategia futura aprovada:
  - criar `backend/app/modules/lead_imports` como pacote real;
  - manter `backend/app/modules/leads_publicidade` como alias/reexport
    temporario;
  - migrar consumidores incrementalmente para `app.modules.lead_imports`;
  - remover o alias antigo apenas em rodada posterior, apos busca sem
    consumidores.

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
- `PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/`
- `handoff_proximo_passo_organizacao_import.md`
- `handoff_proximo_passo_organizacao_import2.md`
- `handoff_proximo_passo_organizacao_import3.md`

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
    usado para confirmar estrutura atual do pacote;
  - nenhuma suite funcional foi exigida porque a rodada foi documental.

Estado de arquitetura observado:

- `frontend/src/features/leads` e fonte real para lista, analise etaria e hook
  compartilhado.
- Wrappers legados continuam como borda de compatibilidade.
- `DashboardLeads.tsx` e `services/dashboard_leads.ts` nao existem mais.
- `dashboardManifest.ts` ainda contem `/dashboard/leads/conversao` com
  `enabled: false`.
- `backend/app/modules/leads_publicidade` ainda e o pacote real consumido por
  routers, servicos, scripts e testes.
- `backend/app/modules/lead_imports` ainda nao existe.

Consumidores atuais conhecidos de `app.modules.leads_publicidade`:

- producao:
  - `backend/app/routers/leads_routes/classic_import.py`
  - `backend/app/routers/leads_routes/etl_import.py`
  - `backend/app/services/lead_pipeline_service.py`
- scripts:
  - `backend/scripts/run_leads_worker.py`
- codigo interno do pacote:
  - `backend/app/modules/leads_publicidade/application/etl_import/preview_service.py`
  - `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`
- testes:
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
- docs/governanca historica:
  - `docs/adr/0001-lead-import-merge-policy.md`
  - `PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
  - `PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
  - `PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/**`
  - `PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/**`

Residual conhecido:

- Smoke manual em browser ainda nao foi executado nesta frente:
  - `/leads`
  - `/dashboard/leads/analise-etaria`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` continua fora do gate.

## Pendencias e lacunas

Pendencias abertas:

- Abrir feature propria de implementacao do rename planejado, provavelmente
  `FEATURE-6-*`.
- Criar fisicamente `backend/app/modules/lead_imports`.
- Fazer `backend/app/modules/leads_publicidade` virar alias/reexport
  temporario, preservando imports antigos.
- Migrar consumidores internos para `app.modules.lead_imports` em ordem
  controlada.
- Atualizar testes que importam ou patcham por string o caminho antigo.
- Planejar remocao futura dos wrappers temporarios frontend.
- Reabrir importacao/ETL somente em sessao separada, com escopo proprio.

Lacunas que nao devem ser inventadas:

- Nao ha decisao para habilitar `/dashboard/leads/conversao`.
- Nao ha decisao para recriar `DashboardLeads.tsx`.
- Nao ha decisao para reabrir importacao/ETL funcional.
- Nao ha decisao para remover wrappers legados de `pages/*` e `hooks/*`.
- Nao ha implementacao ainda de `app.modules.lead_imports`; existe apenas
  governanca/plano.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **abrir e executar uma
feature pequena de implementacao do rename planejado de
`backend/app/modules/leads_publicidade` para
`backend/app/modules/lead_imports`**, com alias/reexport temporario no caminho
antigo.

Motivo:

- O plano atual ja marcou `rename-module` como `done` no sentido de
  planejamento.
- `FEATURE-5` fixou nome alvo e estrategia de compatibilidade.
- O pacote antigo ainda e usado por producao, script worker, testes e imports
  absolutos internos.
- O rename fisico e a migracao de imports ainda nao aconteceram.
- A execucao agora reduz uma ambiguidade estrutural backend real sem reabrir
  comportamento de ETL.

O que nao deve ser o proximo passo:

- Nao reabrir `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao habilitar `/dashboard/leads/conversao`.
- Nao recriar `DashboardLeads.tsx`.
- Nao remover wrappers legados de frontend.
- Nao remover imediatamente `backend/app/modules/leads_publicidade`; ele deve
  sobreviver como alias/reexport temporario ate migracao completa e validada.

## Proxima acao recomendada

### Objetivo

Implementar a primeira rodada tecnica do rename planejado:

- criar `backend/app/modules/lead_imports` como pacote real;
- preservar `backend/app/modules/leads_publicidade` como compatibilidade
  temporaria;
- migrar imports de producao e testes focados para
  `app.modules.lead_imports`;
- manter contratos HTTP, rotas, schemas, persistencia e comportamento de ETL
  inalterados.

### Escopo

Dentro:

- Criar governanca propria de implementacao, preferencialmente:
  - `PROJETOS/NPBB/INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
  - `PROJETOS/NPBB/PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
  - `PROJETOS/NPBB/features/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS/`
- Criar o pacote novo `backend/app/modules/lead_imports`.
- Mover/copiar a implementacao real de `leads_publicidade` para `lead_imports`
  de forma controlada.
- Transformar `backend/app/modules/leads_publicidade` em camada de
  compatibilidade temporaria.
- Atualizar imports em:
  - `backend/app/routers/leads_routes/classic_import.py`
  - `backend/app/routers/leads_routes/etl_import.py`
  - `backend/app/services/lead_pipeline_service.py`
  - `backend/scripts/run_leads_worker.py`
  - testes backend diretamente relacionados.
- Atualizar `plano_organizacao_import.md` com resultado e validacoes.

Fora:

- Alterar regras de ETL, persistencia, validadores ou merge policy.
- Alterar contratos HTTP, schemas ou rotas.
- Alterar frontend, dashboard ou manifesto.
- Alterar `lead_pipeline/` ou `core/leads_etl/`.
- Remover o alias antigo nesta mesma rodada.
- Editar docs/governanca historica apenas para trocar referencias antigas; elas
  devem continuar como evidencia historica.

### Arquivos mais provaveis de alteracao

- `plano_organizacao_import.md`
- `backend/app/modules/lead_imports/**`
- `backend/app/modules/leads_publicidade/**`
- `backend/app/routers/leads_routes/classic_import.py`
- `backend/app/routers/leads_routes/etl_import.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/scripts/run_leads_worker.py`
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
- nova governanca `PROJETOS/NPBB/features/FEATURE-6-*/`

### Criterios de pronto

- `backend/app/modules/lead_imports` existe e e o pacote real.
- `backend/app/modules/leads_publicidade` continua importavel como alias/reexport
  temporario.
- Imports de producao e script worker usam `app.modules.lead_imports`.
- Testes focados usam `app.modules.lead_imports`, exceto quando houver teste
  explicito de compatibilidade do caminho antigo.
- Busca por `app.modules.leads_publicidade` em codigo ativo mostra apenas a
  camada de compatibilidade e testes/documentos que validam ou registram o
  legado.
- Rotas `/leads`, `/leads/importar`, `/dashboard/leads/analise-etaria` e
  `/dashboard/leads/relatorio` permanecem sem mudanca de contrato.
- `plano_organizacao_import.md` registra a implementacao, validacoes e o
  residual de remocao futura do alias.

### Riscos e validacoes necessarias

Riscos:

- Quebrar imports profundos como
  `app.modules.leads_publicidade.application.etl_import.persistence`.
- Quebrar patches por string em testes, especialmente
  `backend/tests/test_leads_import_etl_staging_repository.py`.
- Duplicar codigo entre pacote novo e antigo em vez de manter um unico pacote
  real com alias limpo.
- Alterar comportamento de ETL ao mover arquivos.
- Remover o pacote antigo cedo demais.
- Incluir `lead_pipeline/`, `core/leads_etl/`, frontend ou dashboard por drift
  de escopo.

Validacoes minimas:

- Antes/depois:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade|app\\.modules\\.lead_imports|lead_imports" backend docs PROJETOS plano_organizacao_import.md`
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/lead_imports`
- Testes backend focados:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_usecases.py backend/tests/test_etl_import_persistence.py backend/tests/test_lead_merge_policy.py backend/tests/test_etl_rejection_reasons.py backend/tests/test_etl_import_validators.py backend/tests/test_etl_csv_delimiter.py backend/tests/test_leads_import_etl_warning_policy.py backend/tests/test_leads_import_etl_staging_repository.py`
- Se routers/script forem alterados, incluir:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q backend/tests/test_leads_import_etl_endpoint.py backend/tests/test_lead_silver_mapping.py backend/tests/test_lead_ticketing_dedupe_postgres.py`

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler este handoff.
- [ ] Ler `PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md`.
- [ ] Ler `PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS.md`.
- [ ] Confirmar consumidores com `rg` antes de editar.
- [ ] Criar governanca de implementacao `FEATURE-6` ou equivalente.
- [ ] Criar `backend/app/modules/lead_imports` como pacote real.
- [ ] Manter `backend/app/modules/leads_publicidade` como alias/reexport
      temporario.
- [ ] Migrar imports de producao, script worker e testes focados para
      `app.modules.lead_imports`.
- [ ] Adicionar ou preservar teste de compatibilidade para o caminho antigo.
- [ ] Nao tocar em frontend, dashboard, `lead_pipeline/`, `core/leads_etl/` ou
      contratos HTTP.
- [ ] Rodar as validacoes backend focadas.
- [ ] Atualizar `plano_organizacao_import.md` com resultado, validacoes e
      residual de remocao futura do alias.
