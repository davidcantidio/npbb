---
doc_id: "US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-04-27"
task_instruction_mode: "required"
feature_id: "FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA"
decision_refs:
  - "PLANO-INTEGRACAO-GERAL-CACHE-ANALISE-ETARIA.md"
  - "PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md"
---

# US-10-01 - Validar integracao local e remediar regressoes

## User Story

Como engenharia do NPBB, quero validar localmente a integracao do cache da
analise etaria e corrigir regressoes diretas, para que a entrega atual chegue a
uma base confiavel antes da consolidacao de evidencias e da decisao de staging.

## Feature de Origem

- **Feature**: `FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA`
- **Comportamento coberto**: migration, validacao backend, validacao frontend e
  smoke local do fluxo etario sem mudanca de contrato publico

## Contexto Tecnico

O codigo ja contem o cache em `backend/app/services/dashboard_service.py`,
versionamento persistido em `backend/app/models/dashboard_cache.py` e
`backend/app/services/dashboard_cache_version_service.py`, bump por pipeline em
`backend/app/services/lead_pipeline_service.py` e cache compartilhado no
frontend em `frontend/src/hooks/useAgeAnalysis.ts` e `frontend/src/main.tsx`.
Esta US fecha a rodada local de validacao e remediacao desses pontos.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a migration do cache aplicada,
  **when** a API subir no ambiente local de desenvolvimento,
  **then** `GET /dashboard/leads/analise-etaria` continua disponivel com o
  contrato atual.
- **Given** a tabela `dashboard_cache_versions`,
  **when** a validacao estrutural rodar,
  **then** a tabela existe sem conflito de schema e pode ser consultada.
- **Given** o hook `useAgeAnalysis`,
  **when** o mesmo escopo repetir filtros e dia de referencia dentro do
  `staleTime`,
  **then** a UI nao faz request redundante fora do fluxo de `refetch()`.
- **Given** dois escopos distintos de usuario,
  **when** a tela for acessada por admin e agencia,
  **then** o placeholder e os dados nao vazam de um escopo para o outro.
- **Given** a suite local,
  **when** aparecer falha fora do diff da integracao do cache,
  **then** ela e classificada como `legacy-known` ou `environment`, e nao como
  regressao direta desta US.

## Tasks

- [T1 - Executar pre-voo, migration e startup limpo](./TASK-1.md)
- [T2 - Validar backend e corrigir regressoes diretas do cache](./TASK-2.md)
- [T3 - Validar frontend e smoke local full-stack](./TASK-3.md)

## Arquivos Reais Envolvidos

- `backend/app/services/dashboard_service.py`
- `backend/app/services/dashboard_cache_version_service.py`
- `backend/app/core/dashboard_cache.py`
- `backend/app/models/dashboard_cache.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/alembic/versions/0c1d2e3f4a5b_create_dashboard_cache_versions.py`
- `backend/tests/test_dashboard_age_analysis_service.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_cache_version_service.py`
- `backend/tests/test_lead_gold_pipeline.py`
- `frontend/src/main.tsx`
- `frontend/src/hooks/useAgeAnalysis.ts`
- `frontend/src/services/dashboard_age_analysis.ts`
- `frontend/src/hooks/__tests__/useAgeAnalysis.test.tsx`
- `frontend/src/services/__tests__/dashboard_age_analysis.test.ts`

## Dependencias

- [Feature 10](../../FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
- [PRD integracao cache analise etaria](../../../../PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
