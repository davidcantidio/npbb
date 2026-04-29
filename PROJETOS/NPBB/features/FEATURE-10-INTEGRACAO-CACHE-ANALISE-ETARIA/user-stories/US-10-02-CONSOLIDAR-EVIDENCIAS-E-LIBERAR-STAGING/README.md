---
doc_id: "US-10-02-CONSOLIDAR-EVIDENCIAS-E-LIBERAR-STAGING"
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

# US-10-02 - Consolidar evidencias e liberar staging

## User Story

Como engenharia do NPBB, quero consolidar as evidencias e fechar a decisao de
staging da integracao do cache etario, para que a liberacao dependa de fatos
observados e nao apenas da existencia de codigo no tronco.

## Feature de Origem

- **Feature**: `FEATURE-10-INTEGRACAO-CACHE-ANALISE-ETARIA`
- **Comportamento coberto**: profiling, drill manual de invalidacao por Gold,
  gate `ci-quality`, checklist de staging e resumo PASS/FAIL

## Contexto Tecnico

Depois que a validacao local da `US-10-01` estabilizar o codigo, ainda falta
provar o bump persistido em `dashboard_cache_versions`, concentrar profiling e
explicar o resultado final separando regressao nova de legado conhecido.

## Criterios de Aceitacao (Given / When / Then)

- **Given** a `US-10-01` concluida,
  **when** um lote Gold for promovido com sucesso,
  **then** a versao de `leads_age_analysis` incrementa em
  `dashboard_cache_versions` com `reason` e `source_batch_id`.
- **Given** os scripts diagnosticos da trilha etaria,
  **when** forem executados para profiling e explain,
  **then** os artefatos ficam em `artifacts/phase-f4/evidence/`.
- **Given** o gate do repo,
  **when** `make ci-quality` for tentado,
  **then** o resumo final informa o que passou, o que falhou e a classificacao
  de cada falha.
- **Given** a tabela `dashboard_cache_versions` e o cache backend por processo,
  **when** houver incidente na rodada,
  **then** as notas de rollback deixam claro que a tabela e aditiva e que o
  cache em memoria pode ser limpo com restart do processo.

## Tasks

- [T1 - Executar drill de invalidao e consolidar profiling](./TASK-1.md)
- [T2 - Rodar gate final e emitir decisao de staging](./TASK-2.md)

## Arquivos Reais Envolvidos

- `backend/scripts/profile_dashboard_age_analysis.py`
- `backend/scripts/run_critical_explains.py`
- `backend/scripts/capture_pg_stat_statements.py`
- `Makefile`
- `render.yaml`
- `docs/SETUP.md`
- `artifacts/phase-f4/evidence/README.md`

## Dependencias

- [US-10-01](../US-10-01-VALIDAR-INTEGRACAO-LOCAL-E-REMEDIAR-REGRESSOES/README.md)
- [PRD integracao cache analise etaria](../../../../PRD-INTEGRACAO-CACHE-ANALISE-ETARIA.md)
