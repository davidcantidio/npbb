---
doc_id: "EPIC-F3-01-DASHBOARD-AGREGADO-E-RANKINGS-COERENTES-POR-EVENTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F3-01 - Dashboard agregado e rankings coerentes por evento

## Objetivo

Consolidar KPIs, series e rankings de `/dashboard/leads` sobre a mesma leitura canonica.

## Resultado de Negocio Mensuravel

O dashboard agregado deixa de divergir da analise etaria para o mesmo evento.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: dashboard agregado coerente com a analise etaria

## Contexto Arquitetural

Deriva do legado `F3-02` sem alterar payloads ou UX.

## Definition of Done do Epico
- [ ] `/dashboard/leads` usa a mesma base de leitura da Feature 1
- [ ] rankings e filtros permanecem coerentes para o mesmo evento
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Consolidar /dashboard/leads e rankings | Dashboard agregado e rankings coerentes por evento | 2 | todo | [README](./issues/ISSUE-F3-01-001-CONSOLIDAR-DASHBOARD-LEADS-E-RANKINGS/README.md) | Feature 2 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 2 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F3_DL2_EPICS.md)
