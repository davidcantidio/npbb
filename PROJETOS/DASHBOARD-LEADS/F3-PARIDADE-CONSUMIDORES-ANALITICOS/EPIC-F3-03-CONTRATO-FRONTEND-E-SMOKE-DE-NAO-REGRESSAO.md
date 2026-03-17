---
doc_id: "EPIC-F3-03-CONTRATO-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F3-03 - Contrato frontend e smoke de nao regressao

## Objetivo

Travar os consumidores React sobre os contratos atuais sem redesenho ou mudanca de UX.

## Resultado de Negocio Mensuravel

Os consumidores frontend seguem operando sobre os contratos canonicos consolidados do backend.

## Contexto Arquitetural

- o PRD preserva os payloads externos
- o frontend deve apenas provar nao regressao funcional

## Definition of Done do Epico

- [ ] servicos frontend seguem sem mudanca de payload
- [ ] smokes principais passam

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-03-001 | Travar consumidores frontend e smoke de nao regressao | Validar consumidores React e servicos frontend sem alterar payloads ou UX fora do escopo do PRD. | 2 | todo | [README](./issues/ISSUE-F3-03-001-TRAVAR-CONSUMIDORES-FRONTEND-E-SMOKE-DE-NAO-REGRESSAO/README.md) |

## Artifact Minimo do Epico

- `frontend/src/services/dashboard_age_analysis.ts`
- `frontend/src/services/dashboard_leads.ts`
- `frontend/src/pages/dashboard/__tests__/`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F3_DASHBOARD_LEADS_EPICS.md)
