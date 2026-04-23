---
name: Plano incremental de organizacao de leads/importacao
overview: "Estado atualizado em 2026-04-23: o slice frontend nao-import foi consolidado como fonte preferencial para testes internos. Lista, analise etaria e hook compartilhado moram em frontend/src/features/leads com wrappers legados em pages/* e hooks/*; DashboardLeads.tsx e services/dashboard_leads.ts foram removidos em FEATURE-4; o rename de app.modules.leads_publicidade foi planejado em FEATURE-5 para o alvo app.modules.lead_imports, sem rename fisico ainda; importacao/ETL seguem congelados."
todos:
  - id: doc-align
    content: Alinhar docs com as rotas reais de leads e dashboard.
    status: done
  - id: router-split
    content: Extrair sub-routers de backend/app/routers/leads.py sem mudar contratos HTTP.
    status: done
  - id: shared-hooks
    content: Relocalizar useReferenciaEventos para modulo partilhado.
    status: done
  - id: import-shell-route
    content: Remover wrapper de rota e lazy-loadar ImportacaoPage diretamente.
    status: done
  - id: import-etl-freeze
    content: Congelar importacao/ETL como fora do proximo passo.
    status: done
  - id: dashboard-orphan-decision
    content: Fixar DashboardLeads.tsx como artefato legado nao roteado, sem religar rota sem decisao de produto.
    status: done
  - id: fe-feature-slice-non-import
    content: Executar a fatia frontend features/leads apenas para lista + dashboard, sem tocar no shell de importacao.
    status: done
  - id: feature-3-governance
    content: Abrir intake, PRD e FEATURE-3 dedicados para a rodada frontend nao-import.
    status: done
  - id: fe-feature-slice-stabilize-imports
    content: Consolidar imports internos/testes para preferirem frontend/src/features/leads sem remover wrappers legados.
    status: done
  - id: dashboard-legacy-feature-4
    content: Remover DashboardLeads.tsx e services/dashboard_leads.ts em FEATURE-4, preservando backend, rotas e manifesto.
    status: done
  - id: rename-module
    content: Planejar rename de app.modules.leads_publicidade para app.modules.lead_imports com camada de compatibilidade.
    status: done
isProject: false
---

# Plano atualizado: organizacao incremental de leads

## 1. Estado atual confirmado

Esta parte do plano ja foi implementada:

- Backend:
  - [backend/app/routers/leads.py](backend/app/routers/leads.py) virou agregador fino.
  - O router foi quebrado em `backend/app/routers/leads_routes/` com:
    - `public_intake.py`
    - `lead_records.py`
    - `references.py`
    - `classic_import.py`
    - `etl_import.py`
    - `batches.py`
  - Os contratos publicos sob `/leads` foram preservados.

- Frontend:
  - O shell canonico `/leads/importar` continua direto em
    [frontend/src/pages/leads/ImportacaoPage.tsx](frontend/src/pages/leads/ImportacaoPage.tsx).
  - A superficie nao-import de leads agora mora em
    [frontend/src/features/leads/index.ts](frontend/src/features/leads/index.ts),
    com implementacao real em:
    - [frontend/src/features/leads/list/LeadsListPage.tsx](frontend/src/features/leads/list/LeadsListPage.tsx)
    - [frontend/src/features/leads/list/leadsListExport.ts](frontend/src/features/leads/list/leadsListExport.ts)
    - [frontend/src/features/leads/list/leadsListQuarterPresets.ts](frontend/src/features/leads/list/leadsListQuarterPresets.ts)
    - [frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx](frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx)
    - [frontend/src/features/leads/dashboard/useAgeAnalysisFilters.ts](frontend/src/features/leads/dashboard/useAgeAnalysisFilters.ts)
    - [frontend/src/features/leads/shared/useReferenciaEventos.ts](frontend/src/features/leads/shared/useReferenciaEventos.ts)
  - Os caminhos legados continuam validos via wrappers finos:
    - [frontend/src/pages/leads/LeadsListPage.tsx](frontend/src/pages/leads/LeadsListPage.tsx)
    - [frontend/src/pages/leads/leadsListExport.ts](frontend/src/pages/leads/leadsListExport.ts)
    - [frontend/src/pages/leads/leadsListQuarterPresets.ts](frontend/src/pages/leads/leadsListQuarterPresets.ts)
    - [frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx](frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx)
    - [frontend/src/pages/dashboard/useAgeAnalysisFilters.ts](frontend/src/pages/dashboard/useAgeAnalysisFilters.ts)
    - [frontend/src/hooks/useReferenciaEventos.ts](frontend/src/hooks/useReferenciaEventos.ts)
  - [frontend/src/app/AppRoutes.tsx](frontend/src/app/AppRoutes.tsx) permanece funcionalmente igual.
  - `frontend/src/pages/DashboardLeads.tsx` e
    `frontend/src/services/dashboard_leads.ts` foram removidos em `FEATURE-4`
    por serem superficie frontend orfa sem rota publica.
  - O endpoint backend `/dashboard/leads/relatorio` permanece vivo como
    API/script sem tela roteada.
  - Os testes focados de lista e dashboard agora importam a implementacao real
    pelo slice `frontend/src/features/leads`, mantendo os wrappers legados
    apenas como borda de compatibilidade para rotas/imports externos.

- Documentacao:
  - [docs/WORKFLOWS.md](docs/WORKFLOWS.md) segue alinhado com:
    - `/leads/importar` como shell canonico
    - `/leads/mapeamento` e `/leads/pipeline` como redirects legados
    - `/dashboard/leads/analise-etaria` como rota de tela atual
    - `/dashboard/leads/relatorio` como endpoint/script sem tela roteada

- Governanca:
  - A rodada estrutural anterior segue em:
    - [PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md](PROJETOS/NPBB/INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
    - [PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md](PROJETOS/NPBB/PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
    - [PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md](PROJETOS/NPBB/features/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS/FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS.md)
  - A nova rodada frontend nao-import foi aberta em:
    - [PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](PROJETOS/NPBB/INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
    - [PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
    - [PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
  - A decisao sobre o legado `DashboardLeads.tsx` foi aberta em:
    - [PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md](PROJETOS/NPBB/INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md)
    - [PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md](PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md)
    - [PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO.md](PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO.md)
  - O planejamento do rename de `app.modules.leads_publicidade` foi aberto em:
    - [PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md](PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md)
    - [PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md](PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md)
    - [PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS.md](PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS.md)
  - A decisao registrada foi:
    - nome alvo: `app.modules.lead_imports`
    - estrategia futura: criar `backend/app/modules/lead_imports` como pacote
      real, manter `backend/app/modules/leads_publicidade` como alias/reexport
      temporario, migrar consumidores incrementalmente e remover o alias antigo
      apenas apos busca sem consumidores
    - escopo desta rodada: planejamento/governanca, sem rename fisico e sem
      alteracao de imports de producao, scripts ou testes

## 2. Validacao executada

### Backend

- Mantem-se valido o resultado da rodada estrutural anterior:
  - `backend/tests/test_leads_list_endpoint.py`
  - `backend/tests/test_leads_public_create_endpoint.py`
  - `backend/tests/test_lead_batch_endpoints.py`
  - `backend/tests/test_leads_import_etl_endpoint.py`
  - `backend/tests/test_lead_silver_mapping.py`
- Resultado registrado anteriormente: `142 passed`
- Validacao adicional em 2026-04-23:
  - `backend/tests/test_lead_gold_pipeline.py` cobre harnesses legados que
    ainda patcham simbolos em `app.routers.leads`.
  - Foi preservada a compatibilidade para `disparar_pipeline`,
    `load_batch_without_bronze_for_update` e `queue_pipeline_batch` no
    agregador fino.
  - Resultado: `75 passed`.

### Frontend

- `cd frontend && npm run typecheck`: passou
- Suites focadas desta rodada:
  - `LeadsListPage.test.tsx`
  - `leadsListExport.test.ts`
  - `leadsListQuarterPresets.test.ts`
  - `DashboardModule.test.tsx`
  - `LeadsAgeAnalysisPage.filters.test.tsx`
  - `LeadsAgeAnalysisPage.states.test.tsx`
  - `dashboardManifest.test.ts`
- Resultado desta rodada: `27 passed`
- Rodada de consolidacao de imports em 2026-04-23:
  - `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src` usado antes/depois para conferir o recorte.
  - `cd frontend && npm run typecheck`: passou.
  - Suite focada de lista/dashboard/manifesto: passou com `27 passed`.
- Rodada de decisao do legado `DashboardLeads.tsx` em 2026-04-23:
  - `rg -n "DashboardLeads|dashboard_leads" frontend/src`: sem resultados apos a remocao.
  - `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS plano_organizacao_import.md` usado antes/depois para conferir que as referencias restantes sao manifesto/teste, docs ou governanca.
  - `cd frontend && npm run typecheck`: passou.
  - Suite focada de dashboard/manifesto: passou com `17 passed`.
- Rodada de planejamento do rename `leads_publicidade` em 2026-04-23:
  - `rg -n "app\\.modules\\.leads_publicidade|leads_publicidade" backend docs PROJETOS plano_organizacao_import.md` usado antes/depois para mapear consumidores.
  - `Get-ChildItem -Recurse -Depth 3 backend/app/modules/leads_publicidade`
    usado para confirmar a estrutura atual do pacote.
  - Como a rodada foi documental, nenhuma suite funcional foi exigida.
  - Nenhum arquivo Python, script, rota, schema, frontend, dashboard,
    `lead_pipeline/` ou `core/leads_etl/` foi alterado por esta rodada.

### Residual conhecido

- [frontend/src/pages/__tests__/ImportacaoPage.test.tsx](frontend/src/pages/__tests__/ImportacaoPage.test.tsx)
  continua fora do gate enquanto o freeze de importacao/ETL estiver ativo.
- As rodadas recentes nao incluem smoke manual executado em browser; a validacao
  feita aqui foi `typecheck` + suites focadas.

## 3. O que continua explicitamente fora deste escopo

Enquanto o objetivo for seguir com muito cuidado, **nao mexer agora** em:

- [frontend/src/pages/leads/ImportacaoPage.tsx](frontend/src/pages/leads/ImportacaoPage.tsx)
- `frontend/src/pages/leads/importacao/**`
- [frontend/src/pages/leads/PipelineStatusPage.tsx](frontend/src/pages/leads/PipelineStatusPage.tsx)
- [frontend/src/pages/leads/MapeamentoPage.tsx](frontend/src/pages/leads/MapeamentoPage.tsx)
- [frontend/src/pages/leads/BatchMapeamentoPage.tsx](frontend/src/pages/leads/BatchMapeamentoPage.tsx)
- fluxos de ETL no frontend
- `lead_pipeline/`
- `core/leads_etl/`
- qualquer contrato HTTP, schema ou rota publica
- rename fisico de `backend/app/modules/leads_publicidade` para
  `backend/app/modules/lead_imports`

Em outras palavras: o shell `/leads/importar`, Bronze, ETL, mapeamento e
pipeline ficam **congelados** por enquanto.

## 4. Guardrails para o proximo agente

- Fazer mudancas pequenas e reversiveis.
- Preferir ajustar imports internos antes de remover wrappers temporarios.
- Nao mover o shell de importacao para `features/leads` nesta etapa.
- Nao tocar em `ImportacaoPage.test.tsx` enquanto o freeze de importacao/ETL estiver ativo.
- Nao recriar `DashboardLeads.tsx` ou `services/dashboard_leads.ts` sem nova
  decisao de produto e feature propria.
- Nao confundir a remocao da tela frontend legada com remocao do endpoint
  backend `/dashboard/leads/relatorio`, que continua preservado.
- Nao executar o rename fisico de `app.modules.leads_publicidade` sem feature
  propria de implementacao, pacote `lead_imports` real e alias/reexport
  temporario no caminho antigo.
- Se uma alteracao comecar a puxar `MapeamentoPage`, `BatchMapeamentoPage`,
  `PipelineStatusPage` ou ETL junto, parar e reduzir o escopo.

## 5. Backlog posterior, mas nao agora

Depois de estabilizar este slice inicial, ai sim considerar:

1. mover o restante do frontend de leads para `features/leads`
2. planejar a remocao dos reexports temporarios quando os imports estiverem consolidados
3. se produto reabrir `/dashboard/leads/conversao`, criar nova tela em feature
   propria sem recuperar automaticamente o legado removido
4. executar em feature propria o rename planejado de `app.modules.leads_publicidade`
   para `app.modules.lead_imports`, com alias/reexport temporario
5. reabrir importacao/ETL em uma sessao separada, com escopo proprio e gate proprio

## 6. Leitura minima para o proximo agente

Antes de mexer em qualquer coisa, ler:

- [plano_organizacao_import.md](plano_organizacao_import.md)
- [PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](PROJETOS/NPBB/PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- [PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](PROJETOS/NPBB/features/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT/FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- [PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md](PROJETOS/NPBB/PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- [PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO.md](PROJETOS/NPBB/features/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO/FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- [PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md](PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md)
- [PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS.md](PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS.md)
- [frontend/src/features/leads/list/LeadsListPage.tsx](frontend/src/features/leads/list/LeadsListPage.tsx)
- [frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx](frontend/src/features/leads/dashboard/LeadsAgeAnalysisPage.tsx)
- [frontend/src/features/leads/shared/useReferenciaEventos.ts](frontend/src/features/leads/shared/useReferenciaEventos.ts)

## Conclusao direta

O estado atual ja resolveu duas rodadas seguras do problema estrutural: primeiro
o router monolitico, o hook mal localizado, as docs desalinhadas e a indirecao
de rota de importacao; depois a organizacao da superficie nao-import de leads
em `features/leads` com compatibilidade legada preservada; por fim, fechou a
decisao sobre `DashboardLeads.tsx` removendo a superficie frontend orfa e
mantendo o endpoint de relatorio como API/script sem tela roteada. O passo
seguinte tambem planejou o rename de `app.modules.leads_publicidade` para
`app.modules.lead_imports` com compatibilidade temporaria, sem executar o
rename fisico. Se a ordem for seguir com muito cuidado, **nao e** reabrir
importacao/ETL; o proximo passo tecnico para backend e uma feature propria de
implementacao do rename com alias/reexport e migracao incremental de imports.
