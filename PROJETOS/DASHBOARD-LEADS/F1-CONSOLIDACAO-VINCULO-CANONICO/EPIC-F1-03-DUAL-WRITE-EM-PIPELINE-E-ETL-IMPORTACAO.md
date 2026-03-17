---
doc_id: "EPIC-F1-03-DUAL-WRITE-EM-PIPELINE-E-ETL-IMPORTACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-03 - Dual-write em pipeline e ETL/importacao

## Objetivo

Garantir `LeadEvento` nos caminhos batch e de ETL/importacao, com resolucao deterministica quando o evento vier apenas por nome.

## Resultado de Negocio Mensuravel

Os writers de lote passam a materializar a fonte canonica sem inferencia silenciosa.

## Contexto Arquitetural

- `LeadBatch.evento_id` ja oferece referencia explicita para parte do pipeline
- o ETL por `evento_nome` precisa respeitar apenas matches unicos
- casos ambiguos devem parar na reconciliacao futura, nao virar vinculo silencioso

## Definition of Done do Epico

- [ ] pipeline Gold assegura `LeadEvento` via `LeadBatch.evento_id`
- [ ] ETL por `evento_nome` cria vinculo apenas em match deterministico
- [ ] casos ambiguos permanecem sem vinculo e ficam rastreaveis para F2

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Garantir LeadEvento no pipeline Gold | Fechar o caminho `LeadBatch.evento_id -> LeadEvento` no pipeline Gold com idempotencia clara. | 1 | done | [README](./issues/ISSUE-F1-03-001-GARANTIR-LEAD-EVENTO-NO-PIPELINE-GOLD/README.md) |
| ISSUE-F1-03-002 | Garantir LeadEvento no ETL por evento_nome | Consolidar resolucao unica por `evento_nome` no ETL/import, sem criar vinculo em matches ambiguos ou ausentes. | 2 | todo | [README](./issues/ISSUE-F1-03-002-GARANTIR-LEAD-EVENTO-NO-ETL-POR-EVENTO-NOME/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/lead_pipeline_service.py`
- `backend/app/modules/leads_publicidade/application/etl_import/persistence.py`
- `backend/tests/test_lead_gold_pipeline.py`
- `backend/tests/test_lead_silver_mapping.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F1_DASHBOARD_LEADS_EPICS.md)
