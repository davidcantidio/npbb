---
doc_id: "EPIC-F1-01-BASELINE-DE-ADERENCIA-F2-F3-VS-TEMPLATE-CANONICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-10"
---

# EPIC-F1-01 - Baseline de Aderencia F2/F3 vs Template Canonico

## Objetivo

Comparar os manifestos F2 e F3 com o template canonico de fase e produzir um
delta objetivo por manifesto, suficiente para dizer se existe `drift
confirmado`, `no-op controlado` ou bloqueio por divergencia fora do escopo.

## Resultado de Negocio Mensuravel

O PM passa a ter uma baseline objetiva para decidir se F2 e F3 exigem patch
minimo de gate ou apenas evidencia de aderencia, sem inferencia vaga e sem
misturar a trilha sibling com a malha principal do projeto.

## Contexto Arquitetural

Este epic consome o template em `GOV-ISSUE-FIRST.md`, o PRD derivado e os
manifestos reais `F2_FRAMEWORK2_0_EPICS.md` e `F3_FRAMEWORK2_0_EPICS.md`. O
escopo e somente documental; nenhum artefato de auditoria ou log de fase sera
criado nesta etapa.

## Definition of Done do Epico

- [ ] existe delta objetivo por manifesto
- [ ] a classificacao `drift confirmado` ou `no-op controlado` esta explicita
- [ ] ficou delimitado o envelope permitido de ajuste para os epicos seguintes
- [ ] qualquer divergencia fora de checklist/gate esta tratada como `BLOQUEADO`

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Comparar manifestos F2 e F3 com o template canonico de gate | Produzir baseline rastreavel e classificar o delta por manifesto. | 3 | todo | [ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md](./issues/ISSUE-F1-01-001-COMPARAR-MANIFESTOS-F2-E-F3-COM-O-TEMPLATE-CANONICO-DE-GATE.md) |

## Artifact Minimo do Epico

Baseline rastreavel registrada na issue `ISSUE-F1-01-001`, com classificacao
por manifesto e limites explicitos do que os epicos seguintes podem tocar.

## Dependencias

- [Intake Derivado](../../INTAKE-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE.md)
- [PRD Derivado](../../PRD-FRAMEWORK2.0-REVALIDAR-MANIFESTOS-F2-F3-CHECKLIST-DE-GATE 1.md)
- [Fase](./F1_REVALIDACAO_F2_F3_GATE_EPICS.md)
- [Template Canonico](../../../COMUM/GOV-ISSUE-FIRST.md)
