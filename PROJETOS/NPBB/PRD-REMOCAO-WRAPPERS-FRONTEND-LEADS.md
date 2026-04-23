---
doc_id: "PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS"
origin_audit_id: "remove-frontend-leads-wrappers"
origin_report_path: "plano_organizacao_import.md"
product_type: "platform-capability"
delivery_surface: "frontend"
business_domain: "eventos-e-leads"
criticality: "media"
data_sensitivity: "lgpd"
integrations:
  - "frontend"
  - "tests"
  - "docs-governance"
change_type: "limpeza-estrutural"
audit_rigor: "elevated"
---

# PRD - Remocao de wrappers frontend de leads

> Origem:
> [INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md](INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md](INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)
- plano operacional: [plano_organizacao_import.md](../../plano_organizacao_import.md)
- data de criacao: `2026-04-23`
- slice real aprovado: `frontend/src/features/leads`
- rotas preservadas: `/leads`, `/leads/importar`,
  `/dashboard/leads/analise-etaria`

## 1. Resumo Executivo

- nome do mini-projeto: remocao wrappers frontend leads
- tese em 1 frase: remover reexports legados nao-import depois de migrar as
  rotas internas para o slice real
- valor esperado:
  - menor ambiguidade de ownership no frontend
  - rotas publicas preservadas
  - validacao focada sem mexer em importacao/ETL

## 2. Objetivo do PRD

Fazer `frontend/src/app/AppRoutes.tsx` lazy-loadar lista de leads e analise
etaria diretamente de `frontend/src/features/leads`, removendo wrappers legados
nao-import sem consumidores relevantes.

## 3. Requisitos Funcionais e Estruturais

1. When a limpeza for iniciada, the system shall confirmar consumidores dos
   wrappers legados nao-import por busca.
2. When `AppRoutes.tsx` carregar `/leads`, the system shall lazy-load
   `LeadsListPage` a partir de `frontend/src/features/leads/list`.
3. When `AppRoutes.tsx` carregar `/dashboard/leads/analise-etaria`, the system
   shall lazy-load `LeadsAgeAnalysisPage` a partir de
   `frontend/src/features/leads/dashboard`.
4. Where wrappers nao-import nao tiverem consumidores relevantes, the system
   shall remove-los.
5. The system shall preserve `/leads`, `/leads/importar` and
   `/dashboard/leads/analise-etaria`.
6. The system shall not change importacao/ETL, backend contracts, schemas,
   public routes, `lead_pipeline/` or `core/leads_etl/`.

## 4. Requisitos Nao Funcionais

- compatibilidade: rotas publicas continuam iguais
- testabilidade: buscas, typecheck e suites focadas devem validar o recorte
- rollback: wrappers podem ser restaurados se aparecer consumidor externo nao
  mapeado
- seguranca/LGPD: nenhuma nova superficie de dados e criada

## 5. Escopo

### Dentro

- `frontend/src/app/AppRoutes.tsx`
- wrappers legados nao-import de lista, analise etaria e hook compartilhado
- testes focados que ainda dependam de caminhos legados
- governanca `FEATURE-8`
- atualizacao do plano operacional

### Fora

- `frontend/src/pages/leads/ImportacaoPage.tsx`
- `frontend/src/pages/leads/importacao/**`
- `frontend/src/pages/leads/MapeamentoPage.tsx`
- `frontend/src/pages/leads/BatchMapeamentoPage.tsx`
- `frontend/src/pages/leads/PipelineStatusPage.tsx`
- ETL funcional, backend, contratos HTTP, schemas e rotas publicas

## 6. Criterios de Aceite

- Given as rotas de leads,
  when `AppRoutes.tsx` for revisado,
  then lista e analise etaria sao lazy-loaded de `features/leads`.
- Given os wrappers legados nao-import,
  when a busca final for executada,
  then nao ha consumidores ativos desses caminhos removidos.
- Given a rota `/leads/importar`,
  when a rodada terminar,
  then ela continua carregando `ImportacaoPage.tsx`.
- Given o escopo da rodada,
  when a task terminar,
  then nenhum arquivo de importacao/ETL funcional foi alterado pela feature.
- Given as validacoes,
  when typecheck e suites focadas forem executadas,
  then o comportamento existente permanece preservado.

## 7. Validacao Minima Obrigatoria

- `rg -n "pages/leads/LeadsListPage|pages/leads/leadsListExport|pages/leads/leadsListQuarterPresets|pages/dashboard/LeadsAgeAnalysisPage|pages/dashboard/useAgeAnalysisFilters|hooks/useReferenciaEventos|features/leads" frontend/src`
- `rg -n "ImportacaoPage|pages/leads/importacao|PipelineStatusPage|MapeamentoPage|BatchMapeamentoPage" frontend/src`
- `cd frontend && npm run typecheck`
- suite focada de lista/dashboard/manifesto usada nas rodadas anteriores

## 8. Decomposicao Aprovada

- `FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS`
  - `US-8-01`: remover wrappers frontend leads nao-import

## 9. Checklist de Prontidao

- [x] `frontend/src/features/leads` ja e o slice real
- [x] testes internos focados ja preferem o slice real
- [x] importacao/ETL funcional preservada como fora de escopo
