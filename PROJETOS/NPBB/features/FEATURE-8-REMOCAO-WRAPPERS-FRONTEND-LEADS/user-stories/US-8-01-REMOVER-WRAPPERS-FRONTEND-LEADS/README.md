---
doc_id: "US-8-01-REMOVER-WRAPPERS-FRONTEND-LEADS"
version: "1.0"
status: "ready_for_review"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS"
decision_refs:
  - "plano_organizacao_import.md"
  - "PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md"
---

# US-8-01 - Remover wrappers frontend leads nao-import

## User Story

Como engenharia do NPBB, quero remover wrappers legados nao-import de leads,
para que as rotas internas usem o slice real `frontend/src/features/leads` sem
alterar as rotas publicas.

## Feature de Origem

- **Feature**: `FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS`
- **Comportamento coberto**: limpeza estrutural de wrappers frontend depois da
  consolidacao de lista, analise etaria e hook compartilhado em `features/leads`

## Contexto Tecnico

`FEATURE-3` consolidou a superficie frontend nao-import em
`frontend/src/features/leads`, preservando wrappers legados como borda de
compatibilidade. A busca atual confirma que testes internos ja importam o slice
real, restando os wrappers e duas lazy routes como dependencias legadas.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a rota `/leads`,
  **when** `AppRoutes.tsx` for revisado,
  **then** `LeadsListPage` e carregada de `frontend/src/features/leads/list`.
- **Given** a rota `/dashboard/leads/analise-etaria`,
  **when** `AppRoutes.tsx` for revisado,
  **then** `LeadsAgeAnalysisPage` e carregada de
  `frontend/src/features/leads/dashboard`.
- **Given** os wrappers legados nao-import,
  **when** a busca final for executada,
  **then** nao ha consumidores ativos dos caminhos removidos.
- **Given** a rota `/leads/importar`,
  **when** a rodada terminar,
  **then** o shell de importacao permanece em `frontend/src/pages/leads`.
- **Given** o escopo da rodada,
  **when** a task terminar,
  **then** nenhum contrato HTTP, schema, backend, ETL funcional,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado pela feature.

## Tasks

- [T1 - Remover wrappers frontend leads nao-import](./TASK-1.md)

## Arquivos Reais Envolvidos

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/leads/LeadsListPage.tsx`
- `frontend/src/pages/leads/leadsListExport.ts`
- `frontend/src/pages/leads/leadsListQuarterPresets.ts`
- `frontend/src/pages/dashboard/LeadsAgeAnalysisPage.tsx`
- `frontend/src/pages/dashboard/useAgeAnalysisFilters.ts`
- `frontend/src/hooks/useReferenciaEventos.ts`
- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `PROJETOS/NPBB/PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md`
- `PROJETOS/NPBB/features/FEATURE-8-REMOCAO-WRAPPERS-FRONTEND-LEADS/**`

## Dependencias

- [PRD remocao wrappers frontend leads](../../../../PRD-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)
- [Intake remocao wrappers frontend leads](../../../../INTAKE-REMOCAO-WRAPPERS-FRONTEND-LEADS.md)
- [Plano operacional](../../../../../plano_organizacao_import.md)
