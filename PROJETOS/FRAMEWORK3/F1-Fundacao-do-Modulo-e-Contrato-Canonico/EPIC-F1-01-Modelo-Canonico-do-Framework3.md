---
doc_id: "EPIC-F1-01-Modelo-Canonico-do-Framework3.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-01 - Modelo Canonico do Framework3

## Objetivo

Consolidar o dominio canonico do FRAMEWORK3 e estabilizar a baseline tecnica do embriao ja presente no backend.

## Resultado de Negocio Mensuravel

Baseline sem regressao e dominio persistido alinhado a taxonomias IDs e estados canonicos.

## Contexto Arquitetural

O repositorio ja contem `backend/app/models/framework_models.py`, `backend/app/api/v1/endpoints/framework.py`, `backend/app/services/framework_orchestrator.py` e `backend/app/schemas/framework.py` como superficies parciais do dominio. Este epic absorve a regressao de import atual e fecha o contrato base do modelo.

## Definition of Done do Epico
- [ ] regressao atual do backend registrada e encapsulada na primeira issue executavel
- [ ] modelo schemas e migration do dominio alinhados ao contrato canonico aprovado
- [ ] issues do epic concluida sem ambiguidade residual sobre entidades e estados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Estabilizar baseline do embriao FRAMEWORK3 | Baseline do backend importando com o router framework habilitado e smoke test rastreavel. | 1 | todo | [ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3](./issues/ISSUE-F1-01-001-Estabilizar-baseline-do-embriao-FRAMEWORK3/) |
| ISSUE-F1-01-002 | Fechar contrato canonico de entidades IDs e estados | Dominio FRAMEWORK3 alinhado a taxonomias IDs e estados canonicos com modelos e schemas coerentes. | 2 | todo | [ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados](./issues/ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados/) |

## Artifact Minimo do Epico

Baseline do backend estabilizada e dominio FRAMEWORK3 canonico documentado.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F1_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- nenhuma
