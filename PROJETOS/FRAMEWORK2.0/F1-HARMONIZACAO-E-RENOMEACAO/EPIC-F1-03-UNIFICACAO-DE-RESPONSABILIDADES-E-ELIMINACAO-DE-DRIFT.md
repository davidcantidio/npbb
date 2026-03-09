---
doc_id: "EPIC-F1-03-UNIFICACAO-DE-RESPONSABILIDADES-E-ELIMINACAO-DE-DRIFT.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F1-03 - Unificacao de Responsabilidades e Eliminacao de Drift

## Objetivo

Remover duplicacoes normativas e garantir que cada regra tenha uma fonte primaria.

## Resultado de Negocio Mensuravel

Leitura e planejamento deixam de depender de comparacao manual entre documentos
que descrevem o mesmo tema com variacoes sutis.

## Contexto Arquitetural

- afeta `GOV-FRAMEWORK-MASTER`, `GOV-SCRUM`, `GOV-INTAKE`, `GOV-ISSUE-FIRST` e prompts canonicos

## Definition of Done do Epico

- [ ] responsabilidades delimitadas entre master e scrum
- [ ] gate `Intake -> PRD` consolidado em `GOV-INTAKE.md`
- [ ] issue template com `decision_refs`

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Delimitar responsabilidades entre master e scrum | Separar mapa do framework de regras scrum. | 3 | todo | [ISSUE-F1-03-001-DELIMITAR-RESPONSABILIDADES-ENTRE-MASTER-E-SCRUM.md](./issues/ISSUE-F1-03-001-DELIMITAR-RESPONSABILIDADES-ENTRE-MASTER-E-SCRUM.md) |
| ISSUE-F1-03-002 | Consolidar leitura canonica e gate intake para PRD | Apontar prompts para a ordem unica e centralizar o gate de intake. | 3 | todo | [ISSUE-F1-03-002-CONSOLIDAR-LEITURA-CANONICA-E-GATE-INTAKE-PARA-PRD.md](./issues/ISSUE-F1-03-002-CONSOLIDAR-LEITURA-CANONICA-E-GATE-INTAKE-PARA-PRD.md) |
| ISSUE-F1-03-003 | Alinhar governanca de issue com decision refs e spec task instructions | Completar rastreabilidade e reduzir duplicacao de regra. | 3 | todo | [ISSUE-F1-03-003-ALINHAR-GOVERNANCA-DE-ISSUE-COM-DECISION-REFS.md](./issues/ISSUE-F1-03-003-ALINHAR-GOVERNANCA-DE-ISSUE-COM-DECISION-REFS.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/GOV-FRAMEWORK-MASTER.md`

## Dependencias

- [Fase](./F1_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
