---
doc_id: "PHASE-F2-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F2 Servico Analitico e API - Epicos

## Objetivo da Fase

Entregar o servico de agregacao etaria e o endpoint autenticado `/dashboard/leads/analise-etaria`, com filtros, cobertura BB e consolidado geral aderentes ao PRD.

## Gate de Saida da Fase

`GET /dashboard/leads/analise-etaria` responde com autenticacao, retorna consolidado e `por_evento` corretos para cenarios com e sem `evento_id`, respeita os thresholds de cobertura BB e passa nos cenarios ampliados de `backend/tests/test_dashboard_leads_endpoint.py` e `backend/tests/test_dashboard_leads_report_endpoint.py`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F2-01` | Query Service Analise Etaria | Construir a camada de agregacao que calcula faixas, cobertura BB, Top 3, media e mediana por evento. | `todo` | [EPIC-F2-01-QUERY-SERVICE-ANALISE-ETARIA.md](./EPIC-F2-01-QUERY-SERVICE-ANALISE-ETARIA.md) |
| `EPIC-F2-02` | Endpoint Analise Etaria e Autorizacao | Expor a rota nova no router de dashboard, reutilizando autenticacao e visibilidade existentes. | `todo` | [EPIC-F2-02-ENDPOINT-ANALISE-ETARIA-E-AUTORIZACAO.md](./EPIC-F2-02-ENDPOINT-ANALISE-ETARIA-E-AUTORIZACAO.md) |

## Escopo desta Entrega

Inclui servico SQL/ORM, consolidacao, faixa dominante, regra de `NULL` para metricas BB sem cobertura e endpoint autenticado com filtros. Exclui manifesto do dashboard, roteamento do frontend e validacao manual de UX.
