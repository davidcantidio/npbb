---
doc_id: "US-5-01-MAPEAR-E-PLANEJAR-RENAME-MODULO-LEAD-IMPORTS"
version: "1.0"
status: "ready_for_review"
owner: "PM"
last_updated: "2026-04-23"
task_instruction_mode: "required"
feature_id: "FEATURE-5-RENAME-MODULO-LEAD-IMPORTS"
decision_refs:
  - "plano_organizacao_import.md"
  - "PRD-RENAME-MODULO-LEAD-IMPORTS.md"
---

# US-5-01 - Mapear e planejar rename do modulo lead imports

## User Story

Como engenharia do NPBB, quero mapear os consumidores de
`app.modules.leads_publicidade` e registrar a estrategia de compatibilidade
para `app.modules.lead_imports`, para que o rename futuro seja executado sem
quebrar routers, worker, testes ou referencias historicas.

## Feature de Origem

- **Feature**: `FEATURE-5-RENAME-MODULO-LEAD-IMPORTS`
- **Comportamento coberto**: planejamento estrutural do rename do modulo
  backend de importacao de leads

## Contexto Tecnico

`backend/app/modules/leads_publicidade` continua sendo o pacote real de
importacao/ETL de leads. A busca atual confirmou consumidores em:

- producao: routers de importacao e `lead_pipeline_service.py`
- scripts: `run_leads_worker.py`
- testes: imports diretos e patches por string
- codigo interno: imports absolutos dentro do proprio pacote
- docs/governanca historica: ADRs, PRDs, intakes, features e auditorias

Esta US nao executa o rename fisico. Ela fixa `lead_imports` como nome alvo e
define que o pacote antigo deve permanecer como alias temporario em uma rodada
posterior.

## Criterios de Aceitacao (Given / When / Then)

- **Given** o plano de rename,
  **when** a governanca for revisada,
  **then** o nome alvo `app.modules.lead_imports` esta registrado.
- **Given** os consumidores atuais,
  **when** a busca por `leads_publicidade` for executada,
  **then** o mapa de impacto esta classificado por categoria.
- **Given** a rodada documental,
  **when** a task terminar,
  **then** nenhum import Python, script, rota, schema, frontend ou dashboard foi
  alterado.
- **Given** a estrategia futura,
  **when** o rename for implementado em outra feature,
  **then** `app.modules.leads_publicidade` deve continuar temporariamente como
  alias/reexport de compatibilidade.

## Tasks

- [T1 - Registrar mapa tecnico e estrategia de rename](./TASK-1.md)

## Arquivos Reais Envolvidos

- `plano_organizacao_import.md`
- `PROJETOS/NPBB/INTAKE-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/PRD-RENAME-MODULO-LEAD-IMPORTS.md`
- `PROJETOS/NPBB/features/FEATURE-5-RENAME-MODULO-LEAD-IMPORTS/**`

## Mapa de Consumidores

### Producao

- `backend/app/routers/leads_routes/classic_import.py`
- `backend/app/routers/leads_routes/etl_import.py`
- `backend/app/services/lead_pipeline_service.py`

### Scripts

- `backend/scripts/run_leads_worker.py`

### Testes

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

### Codigo interno do pacote

- `backend/app/modules/leads_publicidade/application/etl_import/preview_service.py`
- `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`

### Docs e governanca historica

- referencias anteriores em `docs/`, `PROJETOS/NPBB/features/FEATURE-1-*`,
  `FEATURE-2-*`, intakes e PRDs antigos permanecem como evidencias historicas

## Dependencias

- [PRD rename modulo lead imports](../../../../PRD-RENAME-MODULO-LEAD-IMPORTS.md)
- [Intake rename modulo lead imports](../../../../INTAKE-RENAME-MODULO-LEAD-IMPORTS.md)
- [Plano operacional](../../../../../plano_organizacao_import.md)
