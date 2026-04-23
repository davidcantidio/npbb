---
doc_id: "PRD-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS"
origin_audit_id: "plano_organizacao_import"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "frontend-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "frontend"
  - "docs-governance"
change_type: "refatoracao-estrutural"
audit_rigor: "elevated"
---

# PRD - Organizacao frontend de leads nao-import

> Origem:
> [INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md](INTAKE-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT.md)
- data de criacao: `2026-04-22`
- base estrutural preservada:
  `FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS`
- decisao operacional de suporte:
  `plano_organizacao_import.md`

## 1. Resumo Executivo

- nome do mini-projeto: organizacao frontend de leads nao-import
- tese em 1 frase: criar um slice `features/leads` para lista e dashboard sem
  tocar no shell de importacao nem alterar rotas publicas
- valor esperado:
  - lista e dashboard de leads passam a morar na mesma vertical interna
  - hooks e helpers compartilhados deixam de ficar espalhados em `pages/*`
  - `DashboardLeads.tsx` fica formalmente documentado como legado nao roteado

## 2. Objetivo do PRD

Executar uma rodada incremental de organizacao do frontend de leads, com
rollback simples, sem mudanca funcional e sem reabrir importacao/ETL.

## 3. Requisitos Funcionais e Estruturais

1. O frontend deve criar `frontend/src/features/leads/` com as subpastas
   `list/`, `dashboard/` e `shared/`.
2. A implementacao atual de `LeadsListPage`, `LeadsAgeAnalysisPage`,
   `useAgeAnalysisFilters`, `useReferenciaEventos`, `leadsListExport` e
   `leadsListQuarterPresets` deve passar a morar nesse novo slice.
3. Os caminhos legados em `frontend/src/pages/*` e
   `frontend/src/hooks/useReferenciaEventos.ts` devem permanecer validos via
   reexports temporarios.
4. `frontend/src/app/AppRoutes.tsx` deve permanecer funcionalmente igual.
5. `dashboardManifest.ts` deve permanecer igual, com
   `/dashboard/leads/analise-etaria` habilitada e `/dashboard/leads/conversao`
   desabilitada.
6. `frontend/src/pages/DashboardLeads.tsx` deve permanecer sem rota,
   sem alteracao de manifesto e documentado como legado fora desta rodada.
7. Nenhum contrato de servico ou shape tipado em `services/*` pode mudar.

## 4. Escopo

### Dentro

- reorganizacao interna da superficie nao-import de leads no frontend
- compatibilidade temporaria por wrappers finos
- registro de governanca da rodada e do status legado de `DashboardLeads.tsx`

### Fora

- `ImportacaoPage.tsx` e `pages/leads/importacao/**`
- `PipelineStatusPage.tsx`, `MapeamentoPage.tsx`, `BatchMapeamentoPage.tsx`
- backend, `lead_pipeline/` e `core/leads_etl/`
- remocao dos wrappers temporarios
- religar `/dashboard/leads/conversao`

## 5. Rollback e Guardrails

- rollback esperado: revert unico das alteracoes desta rodada
- proibido:
  - mudar rota publica
  - mudar query params suportados
  - mudar manifesto de dashboard
  - mover o shell de importacao para `features/leads`
- aceitavel:
  - mover implementacao para o novo slice
  - criar reexports finos nos caminhos legados
  - abrir nova feature de governanca para esta rodada

## 6. Validacao Minima Obrigatoria

- frontend:
  - `npm run typecheck`
  - `npm run test -- LeadsListPage.test.tsx leadsListExport.test.ts leadsListQuarterPresets.test.ts DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`
- verificacao manual:
  - abrir `/leads`
  - abrir `/dashboard/leads/analise-etaria`
  - confirmar carregamento de eventos e renderizacao sem regressao visivel

## 7. Decomposicao Aprovada

- `FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT`
  - `US-3-01`: slice inicial de lista e dashboard

## 8. Checklist de Prontidao

- [x] escopo limitado ao frontend nao-import
- [x] freeze de importacao/ETL preservado
- [x] politica para `DashboardLeads.tsx` fixada como legado nao roteado
- [x] governanca separada de `FEATURE-2`
- [x] rollback definido por revert simples
