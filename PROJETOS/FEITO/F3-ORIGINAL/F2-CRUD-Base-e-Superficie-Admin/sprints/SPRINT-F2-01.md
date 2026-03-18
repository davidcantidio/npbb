---
doc_id: "SPRINT-F2-01.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# SPRINT-F2-01

## Objetivo da Sprint

Consolidar persistencia e CRUD do topo e meio da hierarquia do FRAMEWORK3.

## Capacidade
- story_points_planejados: 6
- issues_planejadas: 4
- override: nenhum

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Documento |
|---|---|---|---|---|
| ISSUE-F2-01-001 | Consolidar persistencia de projeto a sprint | 2 | todo | [ISSUE-F2-01-001-Consolidar-persistencia-de-projeto-a-sprint](../issues/ISSUE-F2-01-001-Consolidar-persistencia-de-projeto-a-sprint/) |
| ISSUE-F2-01-002 | Consolidar persistencia de issue task e agent execution | 2 | todo | [ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution](../issues/ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution/) |
| ISSUE-F2-02-001 | Expor CRUD de projeto intake e PRD | 1 | todo | [ISSUE-F2-02-001-Expor-CRUD-de-projeto-intake-e-PRD](../issues/ISSUE-F2-02-001-Expor-CRUD-de-projeto-intake-e-PRD/) |
| ISSUE-F2-02-002 | Expor CRUD de fase epico e sprint | 1 | todo | [ISSUE-F2-02-002-Expor-CRUD-de-fase-epico-e-sprint](../issues/ISSUE-F2-02-002-Expor-CRUD-de-fase-epico-e-sprint/) |

## Riscos e Bloqueios
- drift entre models schemas e migrations pode quebrar o recorte base de CRUD
- qualquer campo canonico ausente em F1 reaparece como bloqueio na camada de API

## Encerramento
- decisao: pendente
- observacoes: a sprint encerra apenas quando os criterios do objetivo acima estiverem atendidos sem violar os gates aprovados do FRAMEWORK3
