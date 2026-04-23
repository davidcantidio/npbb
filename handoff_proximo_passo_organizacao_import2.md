# Handoff 2 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao de leads/importacao ja completou tres movimentos seguros:

- reduziu o acoplamento do backend ao transformar `backend/app/routers/leads.py`
  em agregador fino e mover a implementacao para `backend/app/routers/leads_routes/`;
- moveu a superficie frontend nao-import de leads para `frontend/src/features/leads`,
  mantendo wrappers legados em `pages/*` e `hooks/*`;
- consolidou os testes focados de lista e dashboard para importarem a
  implementacao real via `frontend/src/features/leads`, sem remover wrappers.

O objetivo macro continua sendo organizar a area de leads/importacao em passos
pequenos, reversiveis e sem reabrir importacao/ETL antes de existir escopo
proprio.

## Referencia ao plano atual

Fonte principal desta frente:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- o overview afirma que `frontend/src/features/leads` ja e a fonte preferencial
  para testes internos;
- `DashboardLeads.tsx` permanece artefato legado nao roteado;
- importacao/ETL seguem congelados;
- a remocao dos wrappers temporarios ainda nao foi feita;
- o backlog posterior lista como proximos temas:
  1. mover o restante do frontend de leads para `features/leads`;
  2. planejar remocao futura dos reexports temporarios;
  3. decidir o destino de `DashboardLeads.tsx`;
  4. planejar rename de `app.modules.leads_publicidade`;
  5. reabrir importacao/ETL apenas em sessao separada.

Como a consolidacao de imports internos/testes ja foi executada, o proximo
passo de maior alavancagem e **decidir e documentar o destino de
`frontend/src/pages/DashboardLeads.tsx` em feature propria**, antes de remover
wrappers ou mover mais codigo.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- A implementacao real do router foi quebrada em `backend/app/routers/leads_routes/`:
  - `public_intake.py`
  - `lead_records.py`
  - `references.py`
  - `classic_import.py`
  - `etl_import.py`
  - `batches.py`
- Os contratos publicos sob `/leads` foram preservados.

### Frontend - importacao congelada

- `/leads/importar` continua apontando para
  `frontend/src/pages/leads/ImportacaoPage.tsx`.
- `frontend/src/pages/leads/importacao/**`, Bronze, ETL, mapeamento e pipeline
  continuam fora do escopo desta frente.
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

Os testes focados agora exercitam `features/leads` diretamente:

- `frontend/src/pages/__tests__/LeadsListPage.test.tsx`
- `frontend/src/pages/__tests__/leadsListExport.test.ts`
- `frontend/src/pages/__tests__/leadsListQuarterPresets.test.ts`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`

### Dashboard

- `frontend/src/app/AppRoutes.tsx` permanece funcionalmente igual.
- As lazy routes ainda usam wrappers:
  - `../pages/dashboard/LeadsAgeAnalysisPage`
  - `../pages/leads/LeadsListPage`
  - `../pages/leads/ImportacaoPage`
- `/dashboard/leads/analise-etaria` segue como rota de tela atual.
- `frontend/src/config/dashboardManifest.ts` nao foi alterado nesta consolidacao.
- `frontend/src/pages/DashboardLeads.tsx` continua sem rota publica.
- `frontend/src/services/dashboard_leads.ts` ainda existe e e consumido por
  `DashboardLeads.tsx`.

### Governanca

Rodada estrutural anterior:

- `PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md`

Rodada frontend nao-import:

- `PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/README.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/TASK-1.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/TASK-2.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/TASK-3.md`

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
- `PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/`
- `handoff_proximo_passo_organizacao_import.md`

Arquivos relevantes que devem continuar sem alteracao funcional no proximo
passo, salvo decisao explicita:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `lead_pipeline/`
- `core/leads_etl/`
- `frontend/src/config/dashboardManifest.ts`
- `frontend/src/app/AppRoutes.tsx`

## Estado atual do repositorio nesta frente

Validacoes registradas no plano:

- Backend da rodada estrutural anterior: `142 passed` nos testes focados.
- Frontend:
  - `cd frontend && npm run typecheck`: passou.
  - Suite focada passou com `27 passed`:
    - `LeadsListPage.test.tsx`
    - `leadsListExport.test.ts`
    - `leadsListQuarterPresets.test.ts`
    - `DashboardModule.test.tsx`
    - `LeadsAgeAnalysisPage.filters.test.tsx`
    - `LeadsAgeAnalysisPage.states.test.tsx`
    - `dashboardManifest.test.ts`

Estado de arquitetura observado:

- O slice `frontend/src/features/leads` existe e e fonte real para lista,
  analise etaria e hook compartilhado.
- Os wrappers legados continuam necessarios para compatibilidade e rotas.
- Os testes focados de lista/dashboard ja importam `features/leads`.
- `AppRoutes.tsx` ainda usa wrappers por desenho.
- `DashboardLeads.tsx` ainda existe como tela antiga nao roteada e consome
  `frontend/src/services/dashboard_leads.ts`.
- Nao ha evidencia no plano de decisao de produto para habilitar
  `/dashboard/leads/conversao`.

Residual conhecido:

- Smoke manual em browser nao foi executado nesta frente:
  - `/leads`
  - `/dashboard/leads/analise-etaria`
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` continua fora do gate.
- O worktree pode conter muitas alteracoes nao relacionadas; nao reverter nada
  que nao faca parte do recorte.

## Pendencias e lacunas

Pendencias abertas:

- Decidir em feature propria o destino de `frontend/src/pages/DashboardLeads.tsx`.
- Definir se `frontend/src/services/dashboard_leads.ts` segue vivo, muda de dono
  ou entra em arquivamento junto com `DashboardLeads.tsx`.
- Planejar remocao dos wrappers temporarios somente depois de resolver o destino
  da superficie legacy de dashboard e confirmar que nao ha consumidores externos.
- Executar smoke manual em browser para `/leads` e `/dashboard/leads/analise-etaria`.
- Planejar rename de `backend/app/modules/leads_publicidade` segue `deferred`.

Lacunas que nao devem ser inventadas:

- Nao ha decisao de produto para religar `DashboardLeads.tsx`.
- Nao ha decisao para habilitar `/dashboard/leads/conversao` em
  `frontend/src/config/dashboardManifest.ts`.
- Nao ha decisao para reabrir importacao/ETL.
- Nao ha decisao para remover wrappers legados nesta rodada.
- Nao ha decisao para renomear `app.modules.leads_publicidade`.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **abrir e executar uma
feature pequena de decisao/limpeza para `frontend/src/pages/DashboardLeads.tsx`**,
sem alterar rotas publicas ainda.

Motivo:

- O slice `features/leads` ja esta criado, validado e consolidado nos testes.
- A maior incerteza restante na superficie frontend nao-import e a tela antiga
  `DashboardLeads.tsx`, que ainda tem servico proprio (`dashboard_leads.ts`) mas
  nao tem rota publica.
- Remover wrappers agora ainda e cedo: `AppRoutes.tsx` usa wrappers como borda
  de compatibilidade e `DashboardLeads.tsx` ainda precisa de decisao.
- Reabrir importacao/ETL ou renomear modulo backend ampliaria o risco antes de
  fechar a pendencia de dashboard legacy.

Resultado esperado da proxima rodada:

- uma decisao documentada sobre `DashboardLeads.tsx`;
- governanca propria para essa decisao;
- se a decisao for arquivar/remover, uma mudanca pequena e testada;
- se a decisao for manter/reaproveitar, uma anotacao clara do dono futuro,
  sem habilitar rota publica ainda.

O que nao deve ser o proximo passo:

- Nao reabrir `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao habilitar `/dashboard/leads/conversao` sem decisao de produto.
- Nao remover wrappers legados antes de confirmar consumidores.
- Nao iniciar rename de `app.modules.leads_publicidade`.

## Proxima acao recomendada

### Objetivo

Decidir e registrar o destino de `frontend/src/pages/DashboardLeads.tsx` como
artefato legado nao roteado, tratando tambem seu servico associado
`frontend/src/services/dashboard_leads.ts`, sem alterar rotas publicas nem
reabrir importacao/ETL.

### Escopo

Dentro:

- Mapear usos reais de `DashboardLeads.tsx` e `dashboard_leads.ts`.
- Confirmar que `DashboardLeads.tsx` nao e importado por `AppRoutes.tsx` nem
  pelo manifesto atual.
- Criar governanca propria para a decisao, preferencialmente uma nova feature
  em `PROJETOS/NPBB/features/FEATURE-4-*`.
- Escolher uma das tres saidas e documentar explicitamente:
  - arquivar/remover `DashboardLeads.tsx` e, se seguro, o servico exclusivo;
  - manter como legado documentado por tempo determinado;
  - preservar para futura tela de `/dashboard/leads/conversao`, sem religar rota.
- Atualizar `plano_organizacao_import.md` com a decisao e validacoes.

Fora:

- Habilitar `/dashboard/leads/conversao`.
- Alterar `frontend/src/config/dashboardManifest.ts` funcionalmente.
- Alterar `frontend/src/app/AppRoutes.tsx` para religar tela.
- Remover wrappers de `pages/leads/*`, `pages/dashboard/*` ou
  `hooks/useReferenciaEventos.ts`.
- Alterar qualquer arquivo de importacao/ETL.
- Alterar contratos HTTP, schemas ou backend.

### Arquivos mais provaveis de alteracao

- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-*.md`
- `PROJETOS/NPBB/PRD-*.md`
- `PROJETOS/NPBB/features/FEATURE-4-*/`
- possivelmente `frontend/src/pages/DashboardLeads.tsx`, apenas se a decisao for
  arquivar/remover ou adicionar anotacao minima de legado
- possivelmente `frontend/src/services/dashboard_leads.ts`, apenas se ficar
  comprovado que e exclusivo de `DashboardLeads.tsx`
- possivelmente este novo handoff, se a proxima sessao quiser registrar resultado

Arquivos que devem permanecer sem mudanca funcional:

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/config/dashboardManifest.ts`
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/features/leads/**`, salvo ajuste documental inevitavel
- `lead_pipeline/`
- `core/leads_etl/`

### Criterios de pronto

- A decisao sobre `DashboardLeads.tsx` esta registrada em governanca e em
  `plano_organizacao_import.md`.
- `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src`
  foi usado para embasar a decisao.
- Rotas publicas permanecem iguais.
- `dashboardManifest.ts` permanece sem habilitar `/dashboard/leads/conversao`.
- Importacao/ETL permanecem intocados.
- Wrappers legados permanecem intactos.
- `cd frontend && npm run typecheck` passa.
- Suite focada de dashboard/manifesto passa, no minimo:
  - `DashboardModule.test.tsx`
  - `LeadsAgeAnalysisPage.filters.test.tsx`
  - `LeadsAgeAnalysisPage.states.test.tsx`
  - `dashboardManifest.test.ts`
- Se houver remocao de arquivo, rodar tambem `rg` para garantir que nao restam
  imports quebrados.

### Riscos e validacoes necessarias

Riscos:

- Remover `DashboardLeads.tsx` sem perceber uso indireto em docs, testes ou
  imports nao cobertos.
- Habilitar rota ou manifesto sem decisao de produto.
- Confundir `DashboardLeads.tsx` com a rota atual
  `/dashboard/leads/analise-etaria`; sao superficies diferentes.
- Puxar `dashboardManifest.ts`, rotas ou importacao/ETL para um escopo que
  deveria ser apenas decisao/limpeza de legado.
- Remover `frontend/src/services/dashboard_leads.ts` se houver consumidor alem
  de `DashboardLeads.tsx`.

Validacoes:

- Rodar antes de qualquer edicao:
  - `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS`
  - `rg -n "pages/leads/LeadsListPage|pages/dashboard/LeadsAgeAnalysisPage|hooks/useReferenciaEventos|features/leads" frontend/src`
- Rodar depois:
  - `cd frontend && npm run typecheck`
  - `cd frontend && npm run test -- DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`
- Smoke manual opcional, se houver servidor:
  - `/dashboard/leads/analise-etaria`
  - `/leads`

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler `handoff_proximo_passo_organizacao_import2.md`.
- [ ] Confirmar usos com `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS`.
- [ ] Confirmar que `AppRoutes.tsx` e `dashboardManifest.ts` nao roteiam `DashboardLeads.tsx`.
- [ ] Abrir governanca propria para a decisao de `DashboardLeads.tsx`.
- [ ] Escolher e registrar: remover/arquivar, manter legado documentado ou preservar para futura conversao.
- [ ] Nao habilitar `/dashboard/leads/conversao` nesta rodada.
- [ ] Nao tocar em importacao/ETL.
- [ ] Nao remover wrappers legados.
- [ ] Rodar `cd frontend && npm run typecheck`.
- [ ] Rodar suite focada de dashboard/manifesto.
- [ ] Atualizar `plano_organizacao_import.md` com decisao, validacoes e residual.
