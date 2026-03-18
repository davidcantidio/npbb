---
doc_id: "EPIC-F4-02-Execucao-Sequencial-de-Tasks-por-Orquestrador.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F4-02 - Execucao Sequencial de Tasks por Orquestrador

## Objetivo

Rodar tasks em sequencia por issue registrar evidencias minimas e tratar retry e stop conditions.

## Resultado de Negocio Mensuravel

A issue deixa de ser apenas planejamento e passa a ter ciclo operacional controlado pelo modulo.

## Contexto Arquitetural

A execucao precisa respeitar a ordem das tasks a rastreabilidade por task e os criterios de parada definidos em F1.

## Definition of Done do Epico
- [ ] loop sequencial T1..Tn implementado
- [ ] fechamento por task exige commit e evidencia minima
- [ ] retry e parada segura preservam o estado do fluxo

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-02-001 | Orquestrar execucao sequencial de tasks da issue | Loop sequencial `T1..Tn` controlado pelo orquestrador com historico de execucao por task. | 2 | todo | [ISSUE-F4-02-001-Orquestrar-execucao-sequencial-de-tasks-da-issue](./issues/ISSUE-F4-02-001-Orquestrar-execucao-sequencial-de-tasks-da-issue/) |
| ISSUE-F4-02-002 | Registrar commit evidencia e fechamento por task | Task so encerra com rastreabilidade minima de commit e evidencia. | 1 | todo | [ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task](./issues/ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task/) |
| ISSUE-F4-02-003 | Tratar retry stop conditions e coordenacao de subagentes | Falhas operacionais deixam o fluxo em estado seguro com retry e parada definidos. | 1 | todo | [ISSUE-F4-02-003-Tratar-retry-stop-conditions-e-coordenacao-de-subagentes](./issues/ISSUE-F4-02-003-Tratar-retry-stop-conditions-e-coordenacao-de-subagentes/) |

## Artifact Minimo do Epico

Execucao operacional por issue com rastreabilidade por task.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F4_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F4-01
