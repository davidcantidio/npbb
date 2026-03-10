---
doc_id: "EPIC-F1-05-REGRA-OPERACIONAL-PARA-BACKFILLED.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-10"
---

# EPIC-F1-05 - Regra Operacional para Backfilled

## Objetivo

Documentar `source_mode: backfilled` de forma operacional e sem lacunas.

## Resultado de Negocio Mensuravel

Novos projetos retroativos deixam de bloquear por falta de regra de intake.

## Contexto Arquitetural

- afeta `GOV-INTAKE.md`
- afeta sessoes e prompts que dependem do gate de intake

## Definition of Done do Epico

- [x] contexts validos de origem declarados
- [x] campos obrigatorios em backfill documentados
- [x] gate explicita se vale integralmente em backfill

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-05-001 | Documentar regra operacional de backfilled em GOV-INTAKE | Fechar a lacuna de intakes retroativos. | 3 | done | [ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md](./issues/ISSUE-F1-05-001-DOCUMENTAR-REGRA-OPERACIONAL-DE-BACKFILLED-EM-GOV-INTAKE.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/GOV-INTAKE.md`

## Dependencias

- [Fase](./F1_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F1-01-RENOMEACAO-PARA-CONVENCAO-DE-PREFIXO.md)
