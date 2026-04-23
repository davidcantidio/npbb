# Handoff 7 - proximo passo da organizacao de leads/importacao

## Contexto resumido

A frente incremental de organizacao de leads/importacao chegou ao fim do ciclo
estrutural seguro que estava aberto no plano:

- o backend foi reorganizado e `backend/app/routers/leads.py` virou agregador
  fino;
- o pacote backend real de importacao/ETL passou a ser
  `backend/app/modules/lead_imports`;
- o alias temporario `backend/app/modules/leads_publicidade` foi removido em
  `FEATURE-7`;
- a superficie frontend nao-import de leads foi consolidada em
  `frontend/src/features/leads`;
- as rotas internas `/leads` e `/dashboard/leads/analise-etaria` agora carregam
  diretamente o slice `features/leads`;
- wrappers legados nao-import em `frontend/src/pages/*` e `frontend/src/hooks/*`
  foram removidos em `FEATURE-8`;
- importacao/ETL funcional, shell de importacao, mapeamento e pipeline seguem
  congelados.

O plano atual nao deixa mais uma limpeza estrutural simples pendente. O proximo
passo logico e **abrir uma feature propria para decidir e preparar o
descongelamento controlado do shell frontend de importacao**, sem mover arquivos
nem alterar ETL funcional na primeira passada.

## Referencia ao plano atual

Fonte principal:

- `plano_organizacao_import.md`

Estado registrado no plano em 2026-04-23:

- todos os itens do frontmatter `todos` estao `done`, incluindo:
  - `remove-legacy-alias`
  - `remove-fe-leads-wrappers`
- o overview afirma que:
  - `frontend/src/features/leads` e fonte preferencial para rotas e testes
    internos nao-import;
  - wrappers legados nao-import foram removidos em `FEATURE-8`;
  - `app.modules.lead_imports` e o unico caminho backend real;
  - importacao/ETL seguem congelados.
- a secao "Backlog posterior, mas nao agora" lista como primeiro item:
  mover o shell de importacao de leads para `features/leads`, somente em feature
  propria e depois de destravar o escopo de importacao/ETL.

Conclusao direta: o proximo passo coerente **nao e** executar uma mudanca direta
em `ImportacaoPage.tsx` ou nos fluxos ETL. E abrir uma rodada de decisao e
preparacao de escopo para o shell de importacao, definindo se e como a
importacao frontend deve migrar para `features/leads/importacao`.

## O que ja foi implementado

### Backend

- `backend/app/routers/leads.py` virou agregador fino.
- Implementacao real das rotas de leads foi separada em:
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
- Consumidores ativos usam `app.modules.lead_imports`, incluindo routers,
  `backend/app/services/lead_pipeline_service.py`,
  `backend/scripts/run_leads_worker.py` e testes focados.

### Frontend nao-import

Implementacao real consolidada em:

- `frontend/src/features/leads/index.ts`
- `frontend/src/features/leads/list/LeadsListPage.tsx`
- `frontend/src/features/leads/list/leadsListExport.ts`
- `frontend/src/features/leads/list/leadsListQuarterPresets.ts`
- `frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/features/leads/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/features/leads/shared/useReferenciaEventos.ts`

`frontend/src/app/AppRoutes.tsx` agora lazy-loada diretamente:

- `../features/leads/list` para `/leads`
- `../features/leads/dashboard` para `/dashboard/leads/analise-etaria`

Wrappers legados nao-import removidos:

- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`

Busca atual confirma que as referencias restantes sao ao slice real:

- `frontend/src/app/AppRoutes.tsx`
- testes de lista em `frontend/src/pages/__tests__/`
- testes de dashboard em `frontend/src/pages/dashboard/__tests__/`

### Dashboard

- `/dashboard/leads/analise-etaria` segue como rota de tela atual.
- `/dashboard/leads/conversao` segue sem decisao para habilitacao.
- `frontend/src/pages/DashboardLeads.tsx` foi removido em `FEATURE-4`.
- `frontend/src/services/dashboard_leads.ts` foi removido em `FEATURE-4`.
- Endpoint backend `GET /dashboard/leads/relatorio` segue preservado como
  API/script sem tela roteada.
- Ultimo commit observado:
  - `68ec496 fix(dashboard): altura alinhada proponente/confiança, chips à esquerda, KPIs centralizados`
  - Esse commit e posterior ao registro de `FEATURE-8` e indica ajustes visuais
    de dashboard ja integrados.

### Importacao e ETL

Continuam no local atual e fora do escopo das rodadas recentes:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `lead_pipeline/`
- `core/leads_etl/`

Busca atual confirma que `AppRoutes.tsx` ainda carrega:

- `../pages/leads/ImportacaoPage` para `/leads/importar`

E `ImportacaoPage.tsx` ainda importa localmente:

- `./BatchMapeamentoPage`
- `./MapeamentoPage`
- `./PipelineStatusPage`

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
- `frontend/src/pages/leads/LeadsListPage.tsx` (removido)
- `frontend/src/pages/leads/leadsListExport.ts` (removido)
- `frontend/src/pages/leads/leadsListQuarterPresets.ts` (removido)
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx` (removido)
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts` (removido)
- `frontend/src/hooks/useReferenciaEventos.ts` (removido)
- `frontend/src/pages/DashboardLeads.tsx` (removido)
- `frontend/src/services/dashboard_leads.ts` (removido)
- testes frontend focados de lista/dashboard/manifesto.

Governanca criada/concluida nesta frente:

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
- `PROJETOS/NPBB/INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `PROJETOS/NPBB/PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS/`

## Estado atual do repositorio nesta frente

- Worktree atual observado: limpo.
- Ultimo commit observado:
  - `68ec496 fix(dashboard): altura alinhada proponente/confiança, chips à esquerda, KPIs centralizados`
- Busca atual de wrappers frontend removidos:
  - `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src`
  - resultado: apenas referencias ao slice real `features/leads` em rotas e
    testes.
- Existencia atual:
  - `Test-Path backend/app/modules/leads_publicidade`: `False`
  - `Test-Path frontend/src/pages/leads/LeadsListPage.tsx`: `False`
  - `Test-Path frontend/src/hooks/useReferenciaEventos.ts`: `False`
- Validacoes registradas no plano para `FEATURE-8`:
  - `cd frontend && npm run typecheck`: passou
  - suite focada lista/dashboard: `25 passed`
  - manifesto em `src/config/__tests__/dashboardManifest.test.ts`: `2 passed`
- Validacoes registradas no plano para `FEATURE-7`:
  - suite backend focada: `134 passed, 1 skipped`

## Pendencias e lacunas

Pendencias abertas:

- Nao existe ainda governanca para descongelar ou mover o shell frontend de
  importacao.
- `frontend/src/pages/leads/ImportacaoPage.tsx` continua como shell canonico da
  rota `/leads/importar`.
- `frontend/src/pages/leads/importacao/**`, `MapeamentoPage`,
  `BatchMapeamentoPage` e `PipelineStatusPage` continuam fora de
  `features/leads`.
- `frontend/src/pages/__tests__/ImportacaoPage.test.tsx` continua fora do gate
  principal enquanto o freeze de importacao/ETL estiver ativo.
- Nao ha decisao no plano para alterar comportamento de Bronze, ETL, mapeamento,
  merge policy, validadores ou persistencia.
- Nao ha decisao para habilitar `/dashboard/leads/conversao`.
- Nao ha smoke manual em browser registrado para `/leads`, `/leads/importar` ou
  `/dashboard/leads/analise-etaria`; as validacoes recentes foram typecheck e
  testes focados.

Lacunas que nao devem ser inventadas:

- Nao assumir que todo o shell de importacao pode ser movido de uma vez.
- Nao assumir que `ImportacaoPage.test.tsx` esta saudavel ou dentro do gate.
- Nao assumir que mapeamento/pipeline pertencem ao mesmo slice sem decisao de
  arquitetura.
- Nao assumir que o backend de importacao precisa mudar para mover frontend.
- Nao assumir mudancas de produto para `/dashboard/leads/conversao`.

## Proximo passo recomendado

O proximo passo de maior alavancagem e **abrir `FEATURE-9` para decisao e
preparacao da reorganizacao do shell frontend de importacao de leads**.

Motivo:

- As limpezas estruturais seguras ja foram concluidas: router backend, pacote
  backend real, frontend nao-import, wrappers legados e dashboard orfao.
- O unico bloco relevante ainda fora do slice `features/leads` e justamente o
  bloco congelado de importacao.
- O plano diz explicitamente que mover o shell de importacao para
  `features/leads` deve ocorrer apenas em feature propria e depois de destravar
  o escopo de importacao/ETL.
- Como `ImportacaoPage.tsx` puxa `BatchMapeamentoPage`, `MapeamentoPage` e
  `PipelineStatusPage`, mover arquivos agora sem decisao pode arrastar ETL,
  Bronze e pipeline para uma rodada grande demais.

Recomendacao concreta:

1. abrir governanca `FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS`;
2. fazer inventario sem mudanca funcional dos arquivos e dependencias do shell
   `/leads/importar`;
3. decidir entre:
   - manter o shell em `frontend/src/pages/leads` por enquanto, documentando a
     fronteira;
   - mover apenas componentes puros de UI/importacao para
     `frontend/src/features/leads/importacao`;
   - planejar migracao completa do shell em fases, com gate proprio para ETL.
4. somente apos essa decisao criar uma feature de implementacao.

O que nao deve ser o proximo passo:

- mover `ImportacaoPage.tsx` imediatamente;
- mover `frontend/src/pages/leads/importacao/**` imediatamente;
- mexer em `lead_pipeline/` ou `core/leads_etl/`;
- alterar contratos HTTP, schemas, rotas publicas ou persistencia;
- habilitar `/dashboard/leads/conversao`;
- recriar wrappers removidos em `FEATURE-8`;
- recriar `app.modules.leads_publicidade`.

## Proxima acao recomendada

### Objetivo

Abrir uma rodada de decisao/preparacao para o shell de importacao de leads:

- mapear dependencias reais de `/leads/importar`;
- definir fronteira entre `pages/leads` e futuro `features/leads/importacao`;
- decidir se a proxima implementacao sera documental, migracao parcial de UI ou
  migracao completa em fases;
- manter comportamento de importacao/ETL congelado ate existir decisao
  explicita.

### Escopo

Dentro:

- Nova governanca, provavelmente:
  - `PROJETOS/NPBB/INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md`
  - `PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
  - `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/`
- Inventario por busca/leitura de:
  - `frontend/src/pages/leads/ImportacaoPage.tsx`
  - `frontend/src/pages/leads/importacao/**`
  - `frontend/src/pages/leads/MapeamentoPage.tsx`
  - `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
  - `frontend/src/pages/leads/PipelineStatusPage.tsx`
  - testes relacionados em `frontend/src/pages/__tests__/`
  - servicos frontend consumidos por esses componentes
- Atualizacao de `plano_organizacao_import.md` com a decisao tomada.

Fora:

- alteracao funcional de upload, Bronze, ETL, mapeamento, pipeline, validadores,
  persistencia ou merge policy;
- alteracao de backend, `lead_pipeline/`, `core/leads_etl/`;
- alteracao de contratos HTTP, schemas ou rotas publicas;
- remocao ou recriacao de rotas existentes;
- habilitacao de `/dashboard/leads/conversao`.

### Arquivos mais provaveis de alteracao

Se a proxima rodada for apenas decisao/preparacao:

- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/PRD-DECISAO-SHELL-IMPORTACAO-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-9-DECISAO-SHELL-IMPORTACAO-LEADS/**`

Se a decisao autorizar uma migracao parcial posterior, os provaveis arquivos da
feature de implementacao seriam:

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- possivel novo slice `frontend/src/features/leads/importacao/**`
- testes em `frontend/src/pages/__tests__/ImportacaoPage.test.tsx`,
  `MapeamentoPage.test.tsx`, `BatchMapeamentoPage.test.tsx` e
  `PipelineStatusPage.test.tsx`

### Criterios de pronto

- Governanca da `FEATURE-9` criada com escopo fechado.
- Inventario documentado das dependencias de `ImportacaoPage.tsx` e subfluxos.
- Decisao explicita registrada:
  - manter como esta;
  - migrar parcialmente UI;
  - ou planejar migracao completa em fases.
- `plano_organizacao_import.md` atualizado com a decisao e o residual.
- Nenhum comportamento de importacao/ETL alterado sem feature de implementacao.
- Nenhum contrato HTTP, schema, rota publica, backend, `lead_pipeline/` ou
  `core/leads_etl/` alterado nesta rodada de decisao.

### Riscos e validacoes necessarias

Riscos:

- transformar uma feature de decisao em refactor funcional grande;
- mover `ImportacaoPage.tsx` e quebrar imports relativos profundos;
- tocar em testes instaveis de importacao sem ter definido gate;
- misturar frontend de importacao com backend ETL, Bronze ou pipeline;
- reintroduzir wrappers frontend removidos em `FEATURE-8`;
- alterar rotas publicas usadas por usuarios.

Validacoes minimas para a proxima sessao:

- Estado inicial:
  - `git status --short`
  - `git log -1 --oneline`
- Buscas de fronteira:
  - `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
  - `rg -n "features/leads|pages/leads/LeadsListPage|hooks/useReferenciaEventos|pages/dashboard/LeadsAgeAnalysisPage" frontend/src`
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend/app backend/scripts backend/tests`
- Se a rodada for documental, nao exigir suite funcional.
- Se qualquer arquivo frontend for alterado:
  - `cd frontend && npm run typecheck`
  - testes focados correspondentes ao arquivo alterado.
- Se algum backend de importacao for tocado, parar e abrir nova feature com
  gate backend proprio.

## Checklist para a proxima sessao

- [ ] Ler `plano_organizacao_import.md`.
- [ ] Ler este handoff.
- [ ] Conferir `git status --short` e `git log -1 --oneline`.
- [ ] Confirmar que wrappers removidos continuam ausentes:
      `frontend/src/pages/leads/LeadsListPage.tsx` e
      `frontend/src/hooks/useReferenciaEventos.ts`.
- [ ] Confirmar que `backend/app/modules/leads_publicidade` continua ausente.
- [ ] Inventariar `ImportacaoPage.tsx` e subcomponentes de importacao antes de
      propor qualquer move.
- [ ] Abrir governanca `FEATURE-9` para decisao do shell de importacao.
- [ ] Nao mover `ImportacaoPage.tsx` na mesma rodada sem decisao registrada.
- [ ] Nao tocar em `lead_pipeline/`, `core/leads_etl/`, contratos HTTP, schemas
      ou rotas publicas.
- [ ] Atualizar `plano_organizacao_import.md` com a decisao tomada.
- [ ] Registrar explicitamente validacoes executadas ou justificar por que a
      rodada foi apenas documental.
