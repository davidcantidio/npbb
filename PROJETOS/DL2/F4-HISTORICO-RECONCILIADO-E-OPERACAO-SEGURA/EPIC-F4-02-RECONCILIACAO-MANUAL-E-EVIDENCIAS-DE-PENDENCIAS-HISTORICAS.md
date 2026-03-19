---
doc_id: "EPIC-F4-02-RECONCILIACAO-MANUAL-E-EVIDENCIAS-DE-PENDENCIAS-HISTORICAS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F4-02 - Reconciliacao manual e evidencias de pendencias historicas

## Objetivo

Tornar visiveis os casos historicos nao resolvidos e formalizar o fechamento manual rastreavel.

## Resultado de Negocio Mensuravel

`missing`, `ambiguous` e `manual_reconciled` deixam de ser casos invisiveis para a operacao.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: reconciliacao rastreavel e fechamento manual minimo

## Contexto Arquitetural

Deriva do legado `F2-02`, mantendo escopo controlado e auditavel.

## Definition of Done do Epico
- [ ] relatorio de reconciliacao e emitido com trilha de origem
- [ ] `manual_reconciled` esta formalizado como caminho minimo de fechamento manual
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F4-02-001 | Gerar relatorio de reconciliacao missing e ambiguous | Reconciliacao rastreavel dos casos nao resolvidos | 2 | todo | [README](./issues/ISSUE-F4-02-001-GERAR-RELATORIO-DE-RECONCILIACAO-MISSING-E-AMBIGUOUS/README.md) | Feature 3 |
| ISSUE-F4-02-002 | Formalizar fechamento manual_reconciled | Fechamento manual rastreavel de manual_reconciled | 1 | todo | [README](./issues/ISSUE-F4-02-002-FORMALIZAR-FECHAMENTO-MANUAL-RECONCILED/README.md) | Feature 3 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 3 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F4_DL2_EPICS.md)
