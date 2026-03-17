---
doc_id: "EPIC-F2-02-RECONCILIACAO-DE-CASOS-AMBIGUOS-E-NAO-RESOLVIDOS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-02 - Reconciliacao de casos ambiguos e nao resolvidos

## Objetivo

Separar os casos historicos nao resolvidos e permitir fechamento manual controlado.

## Resultado de Negocio Mensuravel

Os casos fora do match deterministico deixam de ser invisiveis e passam a ser auditaveis.

## Contexto Arquitetural

- `resolve_unique_evento_by_name` ja distingue `missing` e `ambiguous`
- o projeto precisa transformar isso em evidencias e caminho manual de fechamento

## Definition of Done do Epico

- [ ] relatorio de reconciliacao emitido
- [ ] `manual_reconciled` formalizado como fechamento manual

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Gerar relatorio de reconciliacao missing e ambiguous | Emitir artefato rastreavel com os casos `missing` e `ambiguous` encontrados pelo backfill. | 2 | todo | [README](./issues/ISSUE-F2-02-001-GERAR-RELATORIO-DE-RECONCILIACAO-MISSING-E-AMBIGUOUS/README.md) |
| ISSUE-F2-02-002 | Formalizar fechamento manual_reconciled | Definir e materializar o caminho minimo para marcar um vinculo historico como `manual_reconciled` com evidencia de origem. | 1 | todo | [README](./issues/ISSUE-F2-02-002-FORMALIZAR-FECHAMENTO-MANUAL-RECONCILED/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_event_service.py`
- `artifacts/lead_evento_reconciliation/`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F2_DASHBOARD_LEADS_EPICS.md)
