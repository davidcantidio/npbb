# Handoff - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente de organizacao de leads/importacao ja executou duas rodadas seguras:

- a primeira reduziu acoplamento estrutural em backend, docs e shell canonico de importacao;
- a segunda moveu a superficie frontend nao-import de leads para `frontend/src/features/leads`, mantendo compatibilidade por wrappers legados.

O objetivo macro permanece: melhorar a estrutura com baixo risco, rollback simples e sem reabrir importacao/ETL antes da hora.

## Referencia ao plano atual

Fonte principal desta frente:

- `plano_organizacao_import.md`

Pontos do plano atual que governam a proxima sessao:

- O overview registra que a rodada frontend nao-import ja foi executada.
- `DashboardLeads.tsx` foi fixado como artefato legado nao roteado.
- Importacao/ETL seguem congelados.
- O backlog posterior recomenda estabilizar o slice inicial, planejar remocao futura de reexports temporarios e decidir `DashboardLeads.tsx` em feature propria.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- A implementacao interna foi quebrada em `backend/app/routers/leads_routes/`.
- Os contratos publicos sob `/leads` foram preservados.

### Frontend - shell de importacao

- `/leads/importar` continua apontando diretamente para `frontend/src/pages/leads/ImportacaoPage.tsx`.
- O shell de importacao, Bronze, ETL, mapeamento e pipeline continuam fora do escopo atual.

### Frontend - slice nao-import

A implementacao real da superficie nao-import de leads agora mora em:

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

Os caminhos legados continuam validos via reexports temporarios:

- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`

### Dashboard

- `frontend/src/app/AppRoutes.tsx` permanece funcionalmente igual.
- `frontend/src/config/dashboardManifest.ts` permanece igual.
- `/dashboard/leads/analise-etaria` segue como rota de tela atual.
- `/dashboard/leads/conversao` segue entrada desabilitada no manifesto.
- `frontend/src/pages/DashboardLeads.tsx` permanece intocado, sem rota publica e tratado como legado nao roteado.

### Governanca

Rodada anterior:

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

Arquivos relevantes explicitamente nao tocados nesta rodada:

- `frontend/src/pages/DashboardLeads.tsx`
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `lead_pipeline/`
- `core/leads_etl/`

## Estado atual do repositorio nesta frente

Validacoes registradas em `plano_organizacao_import.md`:

- `cd frontend && npm run typecheck`: passou.
- Suite focada frontend passou com `27 passed`:
  - `LeadsListPage.test.tsx`
  - `leadsListExport.test.ts`
  - `leadsListQuarterPresets.test.ts`
  - `DashboardModule.test.tsx`
  - `LeadsAgeAnalysisPage.filters.test.tsx`
  - `LeadsAgeAnalysisPage.states.test.tsx`
  - `dashboardManifest.test.ts`

Residual conhecido:

- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` continua fora do gate enquanto importacao/ETL estiverem congelados.
- Smoke manual em browser nao foi executado nesta rodada.

Estado de arquitetura:

- O slice `frontend/src/features/leads` existe e esta funcional.
- Os wrappers legados ainda sao necessarios para compatibilidade imediata.
- Ainda ha imports em testes e rotas via caminhos legados, por desenho.
- `DashboardLeads.tsx` ainda existe na raiz de `frontend/src/pages`, mas nao e importado por rotas de producao.

## Pendencias e lacunas

Pendencias abertas:

- Estabilizar o slice `features/leads` removendo dependencia interna de caminhos legados onde fizer sentido.
- Decidir em feature propria se `frontend/src/pages/DashboardLeads.tsx` sera:
  - reaproveitado como futura tela de `/dashboard/leads/conversao`;
  - arquivado/removido;
  - mantido como legado documentado por mais tempo.
- Planejar remocao dos wrappers temporarios somente depois que imports internos e testes estiverem consolidados.
- Executar smoke manual em browser para `/leads` e `/dashboard/leads/analise-etaria`.

Lacunas que nao devem ser inventadas:

- Nao ha decisao de produto para religar `DashboardLeads.tsx`.
- Nao ha decisao para reabrir importacao/ETL.
- Nao ha decisao para renomear `app.modules.leads_publicidade`.

## Proximo passo recomendado

O proximo passo mais coerente e de maior alavancagem e **estabilizar o slice `frontend/src/features/leads` reduzindo dependencia dos wrappers legados nos imports internos e nos testes**, sem remover os wrappers ainda.

Motivo:

- O slice ja foi criado e validado.
- Remover wrappers agora seria cedo demais, porque `AppRoutes.tsx` e alguns testes ainda usam caminhos legados como fronteira de compatibilidade.
- A limpeza de imports internos reduz custo futuro sem mudar rotas, manifesto ou comportamento.
- Isso prepara uma rodada posterior segura para decidir se os wrappers podem ser removidos.

O que nao deve ser o proximo passo:

- Nao reabrir `ImportacaoPage.tsx`.
- Nao mexer em `frontend/src/pages/leads/importacao/**`.
- Nao mexer em `lead_pipeline/` ou `core/leads_etl/`.
- Nao religar `DashboardLeads.tsx` a rota publica.
- Nao habilitar `/dashboard/leads/conversao` em `dashboardManifest.ts`.

## Proxima acao recomendada

### Objetivo

Consolidar o slice `frontend/src/features/leads` como fonte interna preferencial para lista, dashboard e hook compartilhado, mantendo wrappers legados apenas como borda de compatibilidade.

### Escopo

Dentro:

- Mapear imports atuais que ainda apontam para wrappers legados.
- Atualizar imports internos e testes para preferirem `frontend/src/features/leads` ou submodulos do slice quando isso nao alterar contrato publico.
- Manter wrappers legados existentes para rotas e compatibilidade externa.
- Atualizar governanca de `FEATURE-3` se a proxima sessao executar essa consolidacao.

Fora:

- Remover wrappers legados.
- Alterar `AppRoutes.tsx` se a mudanca nao for necessaria.
- Alterar `dashboardManifest.ts`.
- Alterar `DashboardLeads.tsx`.
- Alterar qualquer arquivo de importacao/ETL.

### Arquivos mais provaveis de alteracao

- `frontend/src/pages/__tests__/LeadsListPage.test.tsx`
- `frontend/src/pages/__tests__/leadsListExport.test.ts`
- `frontend/src/pages/__tests__/leadsListQuarterPresets.test.ts`
- `frontend/src/pages/dashboard/__tests__/DashboardModule.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.filters.test.tsx`
- `frontend/src/pages/dashboard/__tests__/LeadsAgeAnalysisPage.states.test.tsx`
- `frontend/src/features/leads/index.ts`
- `frontend/src/features/leads/list/index.ts`
- `frontend/src/features/leads/dashboard/index.ts`
- `frontend/src/features/leads/shared/index.ts`
- `PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/user-stories/US-3-01-SLICE-INICIAL-DE-LISTA-E-DASHBOARD/`
- `plano_organizacao_import.md`

Arquivos que provavelmente devem permanecer sem mudanca nesta proxima acao:

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/config/dashboardManifest.ts`
- `frontend/src/pages/DashboardLeads.tsx`
- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`

### Criterios de pronto

- Imports internos e testes relevantes passam a apontar diretamente para `features/leads` quando isso for seguro.
- Wrappers legados continuam existindo e funcionando.
- Rotas publicas permanecem iguais.
- `dashboardManifest.ts` permanece sem mudanca funcional.
- `DashboardLeads.tsx` segue sem rota.
- `cd frontend && npm run typecheck` passa.
- Suite focada passa:
  - `LeadsListPage.test.tsx`
  - `leadsListExport.test.ts`
  - `leadsListQuarterPresets.test.ts`
  - `DashboardModule.test.tsx`
  - `LeadsAgeAnalysisPage.filters.test.tsx`
  - `LeadsAgeAnalysisPage.states.test.tsx`
  - `dashboardManifest.test.ts`

### Riscos e validacoes necessarias

Riscos:

- Quebrar mocks de Vitest ao trocar o caminho real do hook compartilhado.
- Confundir wrappers legados com fonte principal e manter acoplamento desnecessario.
- Remover wrappers cedo demais e quebrar imports externos ao recorte.
- Puxar importacao/ETL acidentalmente por causa da pasta `pages/leads`.

Validacoes:

- Rodar `rg -n "pages/leads/LeadsListPage|pages/dashboard/LeadsAgeAnalysisPage|hooks/useReferenciaEventos|features/leads" frontend/src` antes e depois.
- Rodar `cd frontend && npm run typecheck`.
- Rodar a suite focada listada acima.
- Se houver tempo, executar smoke manual em browser:
  - `/leads`
  - `/dashboard/leads/analise-etaria`

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler este handoff.
- [ ] Confirmar com `rg` quais imports ainda usam wrappers legados.
- [ ] Atualizar apenas imports internos/testes que possam apontar para `features/leads` sem mudar comportamento.
- [ ] Manter wrappers legados intactos.
- [ ] Nao tocar em importacao/ETL.
- [ ] Nao tocar em `DashboardLeads.tsx` salvo para documentacao futura, sem rota.
- [ ] Rodar `cd frontend && npm run typecheck`.
- [ ] Rodar a suite focada de lista/dashboard/manifesto.
- [ ] Atualizar `plano_organizacao_import.md` e/ou `FEATURE-3` somente se a consolidacao for executada.
