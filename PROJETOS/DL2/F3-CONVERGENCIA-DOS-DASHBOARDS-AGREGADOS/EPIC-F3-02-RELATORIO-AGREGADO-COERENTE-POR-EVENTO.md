---
doc_id: "EPIC-F3-02-RELATORIO-AGREGADO-COERENTE-POR-EVENTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F3-02 - Relatorio agregado coerente por evento

## Objetivo

Fechar `/dashboard/leads/relatorio` sobre a mesma semantica canonica dos demais consumidores priorizados.

## Resultado de Negocio Mensuravel

O relatorio deixa de constituir fonte paralela de verdade para o mesmo evento.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: relatorio agregado coerente com os demais consumidores

## Contexto Arquitetural

Deriva do legado `F3-02` com foco exclusivo no recorte de relatorio.

## Definition of Done do Epico
- [ ] `/dashboard/leads/relatorio` retorna contagens coerentes com as outras superficies priorizadas
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Consolidar /dashboard/leads/relatorio | Relatorio agregado coerente por evento | 1 | todo | [README](./issues/ISSUE-F3-02-001-CONSOLIDAR-DASHBOARD-LEADS-RELATORIO/README.md) | Feature 2 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 2 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F3_DL2_EPICS.md)
