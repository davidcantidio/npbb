---
doc_id: "EPIC-F3-01-PARIDADE-DA-ANALISE-ETARIA.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F3-01 - Paridade da analise etaria

## Objetivo

Consolidar a analise etaria no caminho canonico e provar que o contrato atual nao regrediu.

## Resultado de Negocio Mensuravel

O endpoint da analise etaria continua com o mesmo payload externo, mas apoiado apenas na semantica canonica aprovada.

## Contexto Arquitetural

- `dashboard_service.py` ja le `LeadEvento`, mas ainda contem residuos de caminho transitorio
- as fixtures precisam provar o comportamento canonico

## Definition of Done do Epico

- [ ] analise etaria consolidada no caminho canonico
- [ ] testes de contrato e paridade ajustados

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Consolidar a analise etaria no caminho canonico | Remover drift interno da analise etaria e deixar o endpoint apoiado apenas na semantica canonica aprovada. | 2 | todo | [README](./issues/ISSUE-F3-01-001-CONSOLIDAR-ANALISE-ETARIA-NO-CAMINHO-CANONICO/README.md) |
| ISSUE-F3-01-002 | Validar paridade da analise etaria | Ajustar fixtures e testes da analise etaria para provar paridade e nao regressao de contrato. | 1 | todo | [README](./issues/ISSUE-F3-01-002-VALIDAR-PARIDADE-DA-ANALISE-ETARIA/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/dashboard_service.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_age_analysis_service.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F3_DASHBOARD_LEADS_EPICS.md)
