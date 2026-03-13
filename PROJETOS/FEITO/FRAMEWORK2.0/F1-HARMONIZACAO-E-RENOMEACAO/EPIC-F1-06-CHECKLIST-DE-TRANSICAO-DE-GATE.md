---
doc_id: "EPIC-F1-06-CHECKLIST-DE-TRANSICAO-DE-GATE.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-10"
---

# EPIC-F1-06 - Checklist de Transicao de Gate

## Objetivo

Levar para o template de fase um checklist verificavel de transicao de gate.

## Resultado de Negocio Mensuravel

O agente deixa de depender de inferencia manual para saber quando a fase pode
ir de `not_ready` para `pending` e depois para `hold/approved`.

## Contexto Arquitetural

- afeta o template canonico de fase em `GOV-ISSUE-FIRST.md`

## Definition of Done do Epico

- [x] checklist de gate incluido no template de fase
- [x] itens verificaveis e coerentes com `GOV-AUDITORIA.md`

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-06-001 | Inserir checklist de transicao de gate no template de fase | Fechar a ambiguidade operacional do gate. | 3 | done | [ISSUE-F1-06-001-INSERIR-CHECKLIST-DE-TRANSICAO-DE-GATE-NO-TEMPLATE-DE-FASE.md](./issues/ISSUE-F1-06-001-INSERIR-CHECKLIST-DE-TRANSICAO-DE-GATE-NO-TEMPLATE-DE-FASE.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`

## Dependencias

- [Fase](./F1_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
