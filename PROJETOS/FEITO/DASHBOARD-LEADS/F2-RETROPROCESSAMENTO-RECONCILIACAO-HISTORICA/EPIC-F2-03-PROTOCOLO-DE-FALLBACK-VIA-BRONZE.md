---
doc_id: "EPIC-F2-03-PROTOCOLO-DE-FALLBACK-VIA-BRONZE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-03 - Protocolo de fallback via bronze

## Objetivo

Traduzir o fallback via bronze/reprocessamento em criterio operacional executavel sobre as superfices ja existentes.

## Resultado de Negocio Mensuravel

O time sabe quando reprocessar e como registrar a decisao sem abrir automacao destrutiva nova nesta fase.

## Contexto Arquitetural

- o repositorio ja contem stages Bronze/Silver/Gold e endpoints de reprocessamento
- o PRD pede criterio operacional, nao reescrita do pipeline

## Definition of Done do Epico

- [ ] protocolo de fallback definido
- [ ] protocolo conectado aos artefatos operacionais existentes

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-03-001 | Definir criterio operacional de fallback via bronze | Definir quando usar reenvio/reprocessamento de lote em vez de backfill direto, sem ampliar o escopo para automacao nova. | 1 | todo | [README](./issues/ISSUE-F2-03-001-DEFINIR-CRITERIO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE/README.md) |
| ISSUE-F2-03-002 | Conectar protocolo aos artefatos operacionais do lote | Amarrar o protocolo de fallback aos artefatos operacionais ja existentes de lote e reprocessamento, sem criar fluxo destrutivo novo. | 2 | todo | [README](./issues/ISSUE-F2-03-002-CONECTAR-PROTOCOLO-AOS-ARTEFATOS-OPERACIONAIS-DO-LOTE/README.md) |

## Artifact Minimo do Epico

- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/models/lead_batch.py`
- `PROJETOS/DASHBOARD-LEADS/PRD-DASHBOARD-LEADS.md`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F2_DASHBOARD_LEADS_EPICS.md)
