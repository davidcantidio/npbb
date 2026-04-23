---
doc_id: "US-6-01-IMPLEMENTAR-RENAME-MODULO-LEAD-IMPORTS"
version: "1.0"
status: "ready_for_review"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS"
decision_refs:
  - "plano_organizacao_import.md"
  - "PRD-RENAME-MODULO-LEAD-IMPORTS.md"
  - "PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md"
---

# US-6-01 - Implementar rename do modulo lead imports

## User Story

Como engenharia do NPBB, quero executar o rename planejado de
`app.modules.leads_publicidade` para `app.modules.lead_imports` com
compatibilidade temporaria, para reduzir ambiguidade estrutural sem quebrar
routers, worker, testes ou imports legados.

## Feature de Origem

- **Feature**: `FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS`
- **Comportamento coberto**: rename fisico do pacote backend de importacao de
  leads com shims de compatibilidade

## Contexto Tecnico

`FEATURE-5` escolheu `app.modules.lead_imports` como nome alvo e definiu que
`app.modules.leads_publicidade` deveria continuar temporariamente como
compatibilidade. Esta US executa essa decisao sem reabrir comportamento
funcional de ETL.

## Criterios de Aceitacao (Given / When / Then)

- **Given** o pacote backend,
  **when** a implementacao for revisada,
  **then** `backend/app/modules/lead_imports` e o pacote real.
- **Given** consumidores ativos,
  **when** os imports forem revisados,
  **then** routers, worker, servicos e testes focados preferem
  `app.modules.lead_imports`.
- **Given** consumidores legados,
  **when** `app.modules.leads_publicidade.application...` for importado,
  **then** o import continua funcionando como alias temporario.
- **Given** um monkeypatch por string no caminho legado,
  **when** o patch for aplicado,
  **then** ele atinge o mesmo modulo real usado por `lead_imports`.
- **Given** o escopo da rodada,
  **when** a task terminar,
  **then** nenhum contrato HTTP, schema, rota, frontend, dashboard,
  `lead_pipeline/` ou `core/leads_etl/` foi alterado pela feature.

## Tasks

- [T1 - Implementar pacote lead_imports e compatibilidade legada](./TASK-1.md)

## Arquivos Reais Envolvidos

- `backend/app/modules/lead_imports/**`
- `backend/app/modules/leads_publicidade/**`
- `backend/app/routers/leads_routes/classic_import.py`
- `backend/app/routers/leads_routes/etl_import.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/scripts/run_leads_worker.py`
- testes backend focados de importacao/ETL
- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/features/FEATURE-6-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS/**`

## Dependencias

- [PRD implementacao rename modulo lead imports](../../../../PRD-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- [Intake implementacao rename modulo lead imports](../../../../INTAKE-IMPLEMENTACAO-RENAME-MODULO-LEAD-IMPORTS.md)
- [Plano operacional](../../../../../plano_organizacao_import.md)
