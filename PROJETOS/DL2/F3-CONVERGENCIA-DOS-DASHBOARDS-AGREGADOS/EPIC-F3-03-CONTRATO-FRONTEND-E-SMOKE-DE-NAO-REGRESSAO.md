---
doc_id: "EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F3-03 - Contrato frontend e smoke de nao regressao

## Objetivo

Travar os consumidores React sobre os contratos consolidados do backend sem redesenho de UX.

## Resultado de Negocio Mensuravel

O frontend segue funcional enquanto a confiabilidade semantica do backend e consolidada.

## Feature de Origem

- **Feature**: Feature 2
- **Comportamento coberto**: consumidores frontend preservam o payload atual e ficam cobertos por smoke

## Contexto Arquitetural

Deriva diretamente do legado `F3-03` como fechamento do recorte de consumidores priorizados.

## Definition of Done do Epico
- [ ] services e paginas frontend prioritarios seguem operando com o payload atual
- [ ] existe smoke de nao regressao cobrindo as superficies priorizadas
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F3-03-001 | Travar consumidores frontend e smoke de nao regressao | Consumidores frontend preservando contratos consolidados | 2 | todo | [README](./issues/ISSUE-F3-03-001-TRAVAR-CONSUMIDORES-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO/README.md) | Feature 2 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 2 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F3_DL2_EPICS.md)
