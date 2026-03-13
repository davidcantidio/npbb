---
doc_id: "EPIC-F1-01-Levantamento.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F1-01 - Levantamento

## Objetivo

Criar script ou query para contar registros `ativacao` com `landing_url` ou `url_promotor` contendo `localhost` ou `127.0.0.1`, documentando o volume de registros incorretos antes da migracao.

## Resultado de Negocio Mensuravel

Volume de registros com URL local conhecido e documentado, permitindo planejamento da migracao na F2.

## Contexto Arquitetural

- Tabela `ativacao` — colunas `landing_url`, `qr_code_url`, `url_promotor`
- Codigo relevante: `backend/app/utils/urls.py`, `backend/app/services/landing_pages.py`

## Definition of Done do Epico
- [x] Script ou query executavel e documentado
- [x] Volume de registros incorretos registrado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Contar Ativacao Localhost | Script/query para contar registros com URL local | 2 | done | [ISSUE-F1-01-001-Contar-Ativacao-Localhost.md](./issues/ISSUE-F1-01-001-Contar-Ativacao-Localhost.md) |

## Artifact Minimo do Epico

- Script ou query SQL em `backend/scripts/` ou documentado em issue
- Numero de registros afetados documentado

## Dependencias
- [Intake](../INTAKE.md)
- [PRD](../PRD-QR-GEN.md)
- [Fase](./F1_QR-GEN_EPICS.md)
