---
doc_id: "INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md"
version: "1.0"
status: "approved"
owner: "PM"
last_updated: "2026-04-23"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-7-REMOCAO-ALIAS-LEADS-PUBLICIDADE"
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

# INTAKE - Remocao de wrappers frontend de leads

> Intake derivado do plano incremental de organizacao de leads/importacao para
> reduzir a dependencia interna do frontend sobre wrappers legados nao-import.

## 0. Rastreabilidade de Origem

- projeto de origem: `NPBB`
- unidade de origem: `plano_organizacao_import.md`
- decisao de origem: backlog posterior da organizacao frontend nao-import
- slice real aprovado: `frontend/src/features/leads`
- wrappers legados a remover: `frontend/src/pages/leads/*`,
  `frontend/src/pages/dashboard/*` e `frontend/src/hooks/*` apenas nos arquivos
  nao-import listados nesta rodada

## 1. Resumo Executivo

- nome curto da iniciativa: remocao wrappers frontend leads
- tese em 1 frase: fazer as rotas internas consumirem o slice real
  `features/leads` e remover reexports legados sem consumidores
- valor esperado:
  - reduzir indirecao no frontend de leads nao-import
  - manter rotas publicas e comportamento sem mudanca
  - preservar o congelamento de importacao/ETL

## 2. Problema ou Oportunidade

- problema atual: `AppRoutes.tsx` ainda lazy-loada wrappers em `pages/*`, mesmo
  com lista, analise etaria e hook compartilhado consolidados em
  `frontend/src/features/leads`
- evidencia: busca inicial aponta consumidores internos preferindo o slice real,
  restando os wrappers e duas lazy routes como dependencia legada
- oportunidade: remover uma camada temporaria pequena e validada por typecheck e
  testes focados

## 3. Escopo Inicial

### Dentro

- confirmar consumidores dos wrappers legados nao-import por busca
- alterar `frontend/src/app/AppRoutes.tsx` para lazy-loadar de
  `frontend/src/features/leads`
- remover wrappers nao-import sem consumidores relevantes
- registrar a rodada na governanca `FEATURE-8`
- atualizar `plano_organizacao_import.md`

### Fora

- mover ou alterar `ImportacaoPage.tsx`
- alterar `frontend/src/pages/leads/importacao/**`
- alterar `MapeamentoPage`, `BatchMapeamentoPage` ou `PipelineStatusPage`
- alterar ETL funcional, backend de importacao, contratos HTTP, schemas ou
  rotas publicas
- habilitar `/dashboard/leads/conversao`

## 4. Interfaces e Contratos que Devem Permanecer Estaticos

- rota `/leads`
- rota `/leads/importar`
- rota `/dashboard/leads/analise-etaria`
- contratos HTTP e payloads existentes
- comportamento funcional de lista, analise etaria e importacao

## 5. Riscos Relevantes

- remover wrapper ainda usado por consumidor nao mapeado
- quebrar lazy loading por usar modulo sem default export
- confundir wrappers nao-import com o shell de importacao
- misturar a limpeza com alteracoes funcionais de dashboard ou ETL

## 6. Resultado Esperado e Metricas de Sucesso

- `AppRoutes.tsx` nao importa mais wrappers de lista e analise etaria
- wrappers legados nao-import removidos ou justificados na feature
- testes internos seguem importando `frontend/src/features/leads`
- typecheck e suites focadas passam
- nenhum arquivo de importacao/ETL funcional e alterado

## 7. Follow-ups Deliberadamente Adiados

- mover o shell de importacao para `features/leads`
- reabrir importacao/ETL funcional
- habilitar `/dashboard/leads/conversao`
