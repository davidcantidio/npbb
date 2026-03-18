---
doc_id: "EPIC-F2-01-PLANEJAMENTO-EXECUTAVEL-RASTREAVEL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
---

# EPIC-F2-01 - Planejamento executavel rastreavel

## Objetivo

Derivar fases, epicos, issues e tasks a partir do PRD preservando `Feature de Origem`.

## Resultado de Negocio Mensuravel

Permitir que o PM decomponha um projeto inteiro sem reorganizar manualmente o trabalho por camada tecnica.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: hierarquia canonica, limites de issue/task, IDs estaveis e links de rastreabilidade

## Contexto Arquitetural

O backend ja possui fase unica criada pelo embriao do `framework`; este epic precisa materializar a cadeia completa e sua superficie administrativa.

## Definition of Done do Epico
- [ ] a cadeia `feature -> fase -> epico -> issue` e navegavel e consistente

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Derivar fases e epicos a partir das features do PRD | Modelar IDs, dependencias e derivacao de fases/epicos. | 5 | todo | [ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD](./issues/ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD/) | Feature 3 |
| ISSUE-F2-01-002 | Derivar issues e tasks com Feature de Origem explicita | Completar a hierarquia com issues, tasks e metadados de sprint. | 5 | todo | [ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA](./issues/ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA/) | Feature 3 |

## Artifact Minimo do Epico

Mapa do projeto com fases, epicos, issues e tasks derivadas do PRD.

## Dependencias
- [Intake](../INTAKE-FW5.md)
- [PRD](../PRD-FW5.md)
- [Fase](./F2_FW5_EPICS.md)
- dependencias_operacionais: F1-FUNDACAO aprovada
