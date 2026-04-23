---
doc_id: "PRD-DECISAO-DASHBOARD-LEADS-LEGADO.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT"
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
change_type: "limpeza-estrutural"
audit_rigor: "elevated"
---

# PRD - Decisao sobre DashboardLeads legado

> Origem:
> [INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md](INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md](INTAKE-DECISAO-DASHBOARD-LEADS-LEGADO.md)
- data de criacao: `2026-04-23`
- base estrutural preservada:
  `FEATURE-3-ORGANIZACAO-FRONTEND-LEADS-NAO-IMPORT`
- decisao operacional de suporte:
  `plano_organizacao_import.md`

## 1. Resumo Executivo

- nome do mini-projeto: decisao DashboardLeads legado
- tese em 1 frase: remover a tela frontend legada e seu servico exclusivo, sem
  alterar rotas publicas, manifesto, backend ou importacao/ETL
- valor esperado:
  - reduzir codigo morto e ambiguidade de produto
  - manter `/dashboard/leads/analise-etaria` como unica tela ativa de dashboard
    de leads
  - preservar `GET /dashboard/leads/relatorio` como endpoint/script sem tela
    roteada

## 2. Objetivo do PRD

Executar uma limpeza estrutural pequena e reversivel para fechar a decisao
sobre `DashboardLeads.tsx`, removendo apenas a superficie frontend orfa e
registrando a decisao na governanca.

## 3. Requisitos Funcionais e Estruturais

1. When a decisao sobre o legado for executada, o frontend shall remover
   `frontend/src/pages/DashboardLeads.tsx`.
2. When a decisao sobre o legado for executada, o frontend shall remover
   `frontend/src/services/dashboard_leads.ts`, pois o servico e exclusivo da
   tela removida.
3. Where dashboard routing is active, the system shall manter
   `/dashboard/leads/analise-etaria` como a unica rota publica habilitada de
   dashboard de leads.
4. Where dashboard manifest is evaluated, the system shall manter
   `/dashboard/leads/conversao` com `enabled: false`.
5. The system shall preserve `GET /dashboard/leads/relatorio` and related
   backend scripts without contract changes.
6. The system shall not change any importacao/ETL, Bronze, mapeamento,
   pipeline, wrappers legados or public HTTP contracts in this rodada.

## 4. Requisitos Nao Funcionais

- seguranca/LGPD: nenhuma nova superficie de exibicao de dados sera criada
- compatibilidade: rotas e manifesto devem permanecer funcionalmente iguais
- rollback: a mudanca deve ser revertivel por restauracao dos dois arquivos
  frontend e dos registros de governanca desta feature
- testabilidade: typecheck e suite focada de dashboard/manifesto devem passar

## 5. Escopo

### Dentro

- governanca da decisao
- remocao fisica dos dois arquivos frontend orfaos
- atualizacao do plano local com evidencia e validacao

### Fora

- nova tela de conversao
- alteracao de `AppRoutes.tsx` ou `dashboardManifest.ts`
- alteracao de backend, schemas ou scripts
- importacao/ETL e wrappers legados

## 6. Criterios de Aceite

- Given a base frontend,
  when `rg -n "DashboardLeads|dashboard_leads" frontend/src` for executado,
  then nao deve haver referencias aos arquivos removidos.
- Given o manifesto de dashboard,
  when a suite focada rodar,
  then `/dashboard/leads/conversao` continua desabilitada.
- Given as rotas atuais,
  when o typecheck rodar,
  then nao ha import quebrado para a tela removida.
- Given a API de relatorio,
  when a limpeza terminar,
  then o backend e scripts associados permanecem fora do diff desta rodada.

## 7. Validacao Minima Obrigatoria

- `rg -n "DashboardLeads|dashboard_leads|/dashboard/leads/conversao" frontend/src docs PROJETOS plano_organizacao_import.md`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run test -- DashboardModule.test.tsx LeadsAgeAnalysisPage.filters.test.tsx LeadsAgeAnalysisPage.states.test.tsx dashboardManifest.test.ts --run`

## 8. Decomposicao Aprovada

- `FEATURE-4-DECISAO-DASHBOARD-LEADS-LEGADO`
  - `US-4-01`: arquivar DashboardLeads legado

## 9. Checklist de Prontidao

- [x] decisao de destino escolhida: remover/arquivar frontend
- [x] backend explicitamente fora do escopo
- [x] manifesto e rotas explicitamente fora de mudanca funcional
- [x] importacao/ETL preservados
- [x] rollback simples definido
