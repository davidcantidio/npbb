---
doc_id: "EPIC-F1-02-DUAL-WRITE-NO-FLUXO-PUBLICO-E-ATIVACAO.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F1-02 - Dual-write no fluxo publico e ativacao

## Objetivo

Garantir `LeadEvento` nos caminhos de landing e submit publico, preservando `AtivacaoLead` como contexto de conversao.

## Resultado de Negocio Mensuravel

O submit publico passa a assegurar o vinculo canonico em todos os caminhos de sucesso relevantes.

## Contexto Arquitetural

- o fluxo publico hoje conhece `evento` e opcionalmente `ativacao`
- duplicatas de conversao nao podem perder o vinculo `lead-evento`
- a semantica externa do endpoint deve permanecer inalterada

## Definition of Done do Epico

- [ ] submit com ativacao assegura `LeadEvento` e depois trata `AtivacaoLead`
- [ ] submit sem ativacao assegura `LeadEvento`
- [ ] duplicatas de conversao mantem o vinculo canonico

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Garantir dual-write no submit publico | Consolidar `ensure_lead_event` no fluxo publico com e sem `ativacao`, mantendo a ordem transacional minima do PRD. | 2 | done | [README](./issues/ISSUE-F1-02-001-GARANTIR-DUAL-WRITE-NO-SUBMIT-PUBLICO/README.md) |
| ISSUE-F1-02-002 | Cobrir duplicata de conversao e invariantes do submit | Cobrir duplicatas, idempotencia e coerencia entre `LeadEvento` e `AtivacaoLead` nos caminhos do submit publico. | 1 | todo | [README](./issues/ISSUE-F1-02-002-COBRIR-DUPLICATA-DE-CONVERSAO-E-INVARIANTES-DO-SUBMIT/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/landing_page_submission.py`
- `backend/tests/test_landing_public_endpoints.py`
- `backend/tests/test_leads_public_create_endpoint.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F1_DASHBOARD_LEADS_EPICS.md)
