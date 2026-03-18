---
doc_id: "EPIC-F1-04-COBERTURA-EXECUTAVEL-E-INVARIANTES-DO-VINCULO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-04 - Cobertura executavel e invariantes do vinculo

## Objetivo

Alinhar fixtures e suites de regressao ao modelo canonico para que a baseline futura seja auditavel.

## Resultado de Negocio Mensuravel

Os testes deixam de depender implicitamente de `AtivacaoLead` como precondicao para pertencimento ao evento.

## Contexto Arquitetural

- os endpoints de dashboard ja leem `LeadEvento` em partes importantes do runtime
- as fixtures existentes ainda refletem o paradigma antigo em varios testes

## Definition of Done do Epico

- [ ] fixtures de dashboard semeiam `LeadEvento` explicitamente
- [ ] suites alvo cobrem o comportamento canonico aprovado no PRD

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-04-001 | Alinhar fixtures e suite ao modelo canonico | Atualizar fixtures e suites de dashboard para semear `LeadEvento` e validar o comportamento canonico do runtime. | 2 | todo | [README](./issues/ISSUE-F1-04-001-ALINHAR-FIXTURES-E-SUITE-AO-MODELO-CANONICO/README.md) |

## Artifact Minimo do Epico

- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F1_DASHBOARD_LEADS_EPICS.md)
