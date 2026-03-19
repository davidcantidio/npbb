---
doc_id: "EPIC-F4-04-RETIRADA-CONTROLADA-DO-HEURISTICO-RESIDUAL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F4-04 - Retirada controlada do heuristico residual

## Objetivo

Eliminar codigo residual de uniao heuristica que nao faca mais parte do caminho oficial.

## Resultado de Negocio Mensuravel

Os consumidores analiticos deixam de ter uma fonte paralela de verdade fora da semantica canonica.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: caminho oficial sem heuristicas residuais

## Contexto Arquitetural

Deriva do legado `F4-01` e depende do fechamento visivel das Features 1 e 2.

## Definition of Done do Epico
- [ ] residuos heuristicas e codigo morto fora do caminho oficial foram removidos
## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F4-04-001 | Remover heuristicos residuais e codigo morto | Caminho oficial sem heuristicas residuais | 3 | todo | [README](./issues/ISSUE-F4-04-001-REMOVER-HEURISTICOS-RESIDUAIS-E-CODIGO-MORTO/README.md) | Feature 3 |

## Artifact Minimo do Epico

- rastreabilidade de Feature 3 materializada em issues `required`
- evidencias e artefatos minimos listados em cada issue filha

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F4_DL2_EPICS.md)
