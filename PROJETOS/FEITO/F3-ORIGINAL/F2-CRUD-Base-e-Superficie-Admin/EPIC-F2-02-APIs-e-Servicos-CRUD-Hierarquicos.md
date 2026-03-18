---
doc_id: "EPIC-F2-02-APIs-e-Servicos-CRUD-Hierarquicos.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-02 - APIs e Servicos CRUD Hierarquicos

## Objetivo

Expor CRUD do dominio FRAMEWORK3 com navegacao hierarquica transicoes de aprovacao e validacoes de capacidade.

## Resultado de Negocio Mensuravel

Projeto intake PRD fases epicos sprints issues e tasks ficam operaveis por API com contratos unificados.

## Contexto Arquitetural

Com a persistencia consolidada o backend precisa oferecer uma superficie coerente para o modulo admin e para o orquestrador.

## Definition of Done do Epico
- [ ] CRUD do topo da hierarquia disponivel
- [ ] CRUD de planejamento intermediario disponivel com limites de sprint
- [ ] CRUD profundo e transicoes de aprovacao expostos por API

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-02-001 | Expor CRUD de projeto intake e PRD | CRUD do topo da hierarquia disponivel por API. | 1 | todo | [ISSUE-F2-02-001-Expor-CRUD-de-projeto-intake-e-PRD](./issues/ISSUE-F2-02-001-Expor-CRUD-de-projeto-intake-e-PRD/) |
| ISSUE-F2-02-002 | Expor CRUD de fase epico e sprint | CRUD do planejamento intermediario disponivel por API com limites de sprint observaveis. | 1 | todo | [ISSUE-F2-02-002-Expor-CRUD-de-fase-epico-e-sprint](./issues/ISSUE-F2-02-002-Expor-CRUD-de-fase-epico-e-sprint/) |
| ISSUE-F2-02-003 | Expor CRUD de issue task e transicoes de aprovacao | CRUD profundo do FRAMEWORK3 e transicoes de aprovacao disponiveis por API. | 2 | todo | [ISSUE-F2-02-003-Expor-CRUD-de-issue-task-e-transicoes-de-aprovacao](./issues/ISSUE-F2-02-003-Expor-CRUD-de-issue-task-e-transicoes-de-aprovacao/) |

## Artifact Minimo do Epico

Camada de API do FRAMEWORK3 operavel e aderente a governanca.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F2_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F2-01
