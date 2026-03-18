---
doc_id: "EPIC-F2-01-Persistencia-do-Dominio-de-Projetos.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-01 - Persistencia do Dominio de Projetos

## Objetivo

Cobrir o modelo persistido de projeto ate task com relacionamentos coerentes e migrations rastreaveis.

## Resultado de Negocio Mensuravel

O dominio persistido do FRAMEWORK3 deixa de ter lacunas entre topo da hierarquia e nivel operacional.

## Contexto Arquitetural

Depois do contrato canonico aprovado em F1 o proximo passo e consolidar models migrations e schemas do recorte persistido completo.

## Definition of Done do Epico
- [ ] persistencia de projeto a sprint consolidada
- [ ] persistencia de issue task e agent execution consolidada
- [ ] migrations e schemas permanecem coerentes com o dominio

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Consolidar persistencia de projeto a sprint | Persistencia estavel do recorte `project/intake/prd/phase/epic/sprint` com schemas coerentes. | 2 | todo | [ISSUE-F2-01-001-Consolidar-persistencia-de-projeto-a-sprint](./issues/ISSUE-F2-01-001-Consolidar-persistencia-de-projeto-a-sprint/) |
| ISSUE-F2-01-002 | Consolidar persistencia de issue task e agent execution | Persistencia estavel do nivel operacional do FRAMEWORK3 com schemas coerentes. | 2 | todo | [ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution](./issues/ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution/) |

## Artifact Minimo do Epico

Dominio persistido do FRAMEWORK3 pronto para ser consumido pelo CRUD.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F2_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- F1 concluida
