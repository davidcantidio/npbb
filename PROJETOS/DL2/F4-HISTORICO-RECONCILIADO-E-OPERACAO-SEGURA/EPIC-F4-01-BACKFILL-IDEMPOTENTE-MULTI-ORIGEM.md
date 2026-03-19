---
doc_id: "EPIC-F4-01-BACKFILL-IDEMPOTENTE-MULTI-ORIGEM.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F4-01 - Backfill idempotente multi-origem

## Objetivo

Materializar historico resolvivel em `LeadEvento` por execucao controlada e reexecutavel.

## Resultado de Negocio Mensuravel

O historico resolvivel passa a sustentar os dashboards por evento sem duplicidade.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: runner controlado de backfill com idempotencia e precedencia explicitas

## Contexto Arquitetural

Reaproveita o legado `F2-01`, agora vinculado diretamente a confiabilidade historica da Feature 3.

## Definition of Done do Epico
- [ ] runner controlado de backfill esta disponivel
- [ ] precedencia, upgrade de fonte e idempotencia estao cobertos em teste
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F4-01-001 | Implementar runner idempotente de backfill | Runner controlado de backfill multi-origem | 3 | todo | [README](./issues/ISSUE-F4-01-001-IMPLEMENTAR-RUNNER-IDEMPOTENTE-DE-BACKFILL/README.md) | Feature 3 |
| ISSUE-F4-01-002 | Testar precedencia e idempotencia do backfill | Precedencia e idempotencia do backfill validadas | 2 | todo | [README](./issues/ISSUE-F4-01-002-TESTAR-PRECEDENCIA-E-IDEMPOTENCIA-DO-BACKFILL/README.md) | Feature 3 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 3 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F4_DL2_EPICS.md)
