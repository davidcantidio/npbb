---
doc_id: "PHASE-F2-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F2 Integracao Backend - Epicos

## Objetivo da Fase

Integrar o nucleo compartilhado ao backend com preview e commit ETL, contratos de resposta explicitos e coexistencia segura com o fluxo legado de importacao.

## Gate de Saida da Fase

`POST /leads/import/etl/preview` e `POST /leads/import/etl/commit` respondem corretamente para um XLSX fora do padrao, com testes de endpoint passando e sem regressao nos endpoints legados de `/leads/import`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F2-01` | Use Case ETL Import | Criar o use case `import_leads_with_etl(file, evento_id, db, strict)` para orquestrar extract, transform, validate e persist. | `todo` | [EPIC-F2-01-USECASE-ETL-IMPORT.md](./EPIC-F2-01-USECASE-ETL-IMPORT.md) |
| `EPIC-F2-02` | Endpoints Preview Commit | Expor `/leads/import/etl/preview` e `/leads/import/etl/commit` sem quebrar o router legado. | `todo` | [EPIC-F2-02-ENDPOINTS-PREVIEW-COMMIT.md](./EPIC-F2-02-ENDPOINTS-PREVIEW-COMMIT.md) |
| `EPIC-F2-03` | Schemas e Deprecacao Normalize | Definir os schemas ETL do backend e marcar o normalize legado como deprecated. | `todo` | [EPIC-F2-03-SCHEMAS-E-DEPRECACAO-NORMALIZE.md](./EPIC-F2-03-SCHEMAS-E-DEPRECACAO-NORMALIZE.md) |

## Escopo desta Entrega

Inclui use case, contratos de dados, endpoints novos e deprecacao controlada do normalize legado. Exclui adaptacoes de frontend, refatoracao do orchestrator CLI e remocao definitiva de compatibilizadores ainda necessarios.
