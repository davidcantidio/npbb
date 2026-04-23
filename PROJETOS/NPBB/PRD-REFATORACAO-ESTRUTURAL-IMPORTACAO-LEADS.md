---
doc_id: "PRD-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-22"
project: "NPBB"
intake_kind: "structural-remediation"
source_mode: "derived"
origin_project: "NPBB"
origin_phase: "FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD"
origin_audit_id: "RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS"
origin_report_path: "PROJETOS/NPBB/features/FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD/auditorias/RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS.md"
product_type: "platform-capability"
delivery_surface: "fullstack-module"
business_domain: "eventos-e-leads"
criticality: "alta"
data_sensitivity: "lgpd"
integrations:
  - "backend"
  - "frontend"
  - "docs-governance"
change_type: "refatoracao-estrutural"
audit_rigor: "elevated"
---

# PRD - Refatoracao estrutural da importacao de leads

> Origem:
> [INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md](INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)

## 0. Rastreabilidade

- intake de origem:
  [INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md](INTAKE-REFATORACAO-ESTRUTURAL-IMPORTACAO-LEADS.md)
- data de criacao: `2026-04-22`
- base funcional preservada:
  `FEATURE-1-PIPELINE-DE-LEADS-BRONZE-SILVER-GOLD`
- diagnostico de suporte:
  `RELATORIO-DIAGNOSTICO-OWNERSHIP-IMPORTACAO-LEADS`

## 1. Resumo Executivo

- nome do mini-projeto: refatoracao estrutural da importacao de leads
- tese em 1 frase: quebrar hotspots estruturais da trilha de leads em slices
  internos menores, mantendo a superficie externa intacta
- valor esperado:
  - router de leads modularizado por contexto
  - hook de referencia de eventos compartilhado entre dashboard e listagem
  - docs alinhadas com as rotas canonicas realmente suportadas

## 2. Objetivo do PRD

Executar uma primeira rodada de refatoracao incremental, com rollback trivial
por revert, sem migracao, sem rename de pacote e sem alterar contratos HTTP.

## 3. Requisitos Funcionais e Estruturais

1. `backend/app/routers/leads.py` deve permanecer como ponto de import publico e
   agregador fino.
2. O backend deve distribuir a implementacao interna em:
   `public_intake.py`, `lead_records.py`, `references.py`,
   `classic_import.py`, `etl_import.py` e `batches.py`, dentro de
   `backend/app/routers/leads_routes/`.
3. A ordem de registro de rotas, dependencias e decorators duplicados do router
   atual deve ser preservada.
4. As rotas frontend `/leads`, `/leads/importar`, `/leads/mapeamento` e
   `/leads/pipeline` devem permanecer disponiveis.
5. `/dashboard/leads` deve continuar apontando para
   `/dashboard/leads/analise-etaria`.
6. O hook `useReferenciaEventos` deve morar em
   `frontend/src/hooks/useReferenciaEventos.ts`.
7. A rota `/leads/importar` deve lazy-loadar diretamente
   `frontend/src/pages/leads/ImportacaoPage.tsx`, sem wrapper dedicado.
8. A documentacao operacional deve explicitar:
   - `/leads/importar` como shell canonico
   - `/leads/mapeamento` e `/leads/pipeline` como redirects legados
   - `/dashboard/leads/analise-etaria` como rota de tela atual
   - `/dashboard/leads/relatorio` como endpoint/script sem tela roteada

## 4. Escopo

### Dentro

- modularizacao do router de leads
- compartilhamento interno do hook de referencia de eventos
- simplificacao de roteamento para importacao
- alinhamento de docs e governanca para a rodada estrutural

### Fora

- alteracoes em `lead_pipeline/`
- alteracoes em `core/leads_etl/`
- rename de `app.modules.leads_publicidade`
- remediacoes funcionais de ownership
- qualquer mudanca de schema, response shape ou rota publica

## 5. Rollback e Guardrails

- rollback esperado: revert unico das alteracoes desta rodada
- proibido:
  - migracao de banco
  - mudanca de rota publica
  - mudanca de schema FastAPI/Pydantic
  - renames amplos de pacote
- aceitavel:
  - mover implementacao para modulos internos
  - reexportar funcoes/imports no agregador para compatibilidade de testes
  - atualizar docs e artefatos de governanca

## 6. Validacao Minima Obrigatoria

- backend:
  - `backend/tests/test_leads_list_endpoint.py`
  - `backend/tests/test_leads_public_create_endpoint.py`
  - `backend/tests/test_lead_batch_endpoints.py`
  - `backend/tests/test_leads_import_etl_endpoint.py`
  - `backend/tests/test_lead_silver_mapping.py`
- frontend:
  - `npm run typecheck`
  - suite impactada de `ImportacaoPage`, `LegacyLeadStepRedirect`,
    `MapeamentoPage`, `BatchMapeamentoPage`, `PipelineStatusPage`,
    `LeadsListPage`, `DashboardModule`, `LeadsAgeAnalysisPage.filters` e
    `LeadsAgeAnalysisPage.states`
- verificacao manual:
  - navegacao em `/leads` e `/leads/importar`
  - redirects legados de mapeamento e pipeline
  - filtro de eventos carregando em lista de leads e analise etaria

## 7. Decomposicao Aprovada

- `FEATURE-2-REFATORACAO-ESTRUTURAL-IMPORTACAO-DE-LEADS`
  - `US-2-01`: backend e documentacao
  - `US-2-02`: frontend incremental

## 8. Checklist de Prontidao

- [x] intake dedicado criado
- [x] escopo limitado a mudancas nao quebraveis
- [x] rollback definido por revert simples
- [x] feature e user stories separadas da `FEATURE-1`
- [x] follow-ups estruturais maiores mantidos fora da rodada
