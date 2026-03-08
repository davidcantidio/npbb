---
doc_id: "EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F1-02 - Endpoint de Analise Etaria

## Objetivo

Implementar o endpoint `GET /dashboard/leads/analise-etaria` com schemas de
resposta tipados, lógica de cálculo de faixas etárias (18–25, 26–40, fora de 18–40),
cobertura de dados BB e agregação consolidada (Top 3, média, mediana). O endpoint é
consumido exclusivamente pelo dashboard frontend e requer autenticação JWT.

## Resultado de Negocio Mensuravel

O dashboard recebe um endpoint unico, autenticado e tipado para consultar distribuicao etaria e cobertura BB por evento e no consolidado.

## Contexto Arquitetural

- Router FastAPI em `backend/app/routers/` — novo módulo `dashboard.py`
- Schemas Pydantic: `FaixaEtariaMetrics`, `AgeBreakdown`, `AgeAnalysisResponse`
- Query SQL com cálculo de idade via `data_nascimento` e agregação por evento
- Filtros: `evento_id` (opcional), `data_inicio` (opcional), `data_fim` (opcional)
- Autenticação Bearer token (JWT) — mesma dependência dos endpoints existentes
- Campos `is_cliente_bb` e `is_cliente_estilo` já disponíveis no modelo Lead (EPIC-F1-01)

## Definition of Done do Epico

- [x] Schemas `FaixaEtariaMetrics`, `AgeBreakdown`, `AgeAnalysisResponse` implementados
- [x] Endpoint retorna `por_evento` (lista) e `consolidado` (objeto) conforme PRD
- [x] Filtros `evento_id`, `data_inicio`, `data_fim` funcionando
- [x] Faixas etárias calculadas corretamente (percentuais somam 100%)
- [x] Cobertura BB calculada e threshold aplicado (payload retorna `null` quando cobertura < threshold)
- [x] Consolidado inclui Top 3, média, mediana e concentração Top 3
- [x] Endpoint protegido por JWT
- [x] Testes unitários cobrindo cenários relevantes
- [x] Endpoint documentado no OpenAPI (auto-gerado pelo FastAPI)

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Criar schemas Pydantic da análise etária | Criar schemas Pydantic da análise etária | 3 | done | [ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md](./issues/ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA.md) |
| ISSUE-F1-02-002 | Implementar lógica de query da análise etária | Implementar lógica de query da análise etária | 5 | done | [ISSUE-F1-02-002-IMPLEMENTAR-LOGICA-DE-QUERY-DA-ANALISE-ETARIA.md](./issues/ISSUE-F1-02-002-IMPLEMENTAR-LOGICA-DE-QUERY-DA-ANALISE-ETARIA.md) |
| ISSUE-F1-02-003 | Implementar endpoint GET /dashboard/leads/analise-etaria | Implementar endpoint GET /dashboard/leads/analise-etaria | 3 | done | [ISSUE-F1-02-003-IMPLEMENTAR-ENDPOINT-GET-API-V1-DASHBOARD-LEADS-ANALISE-ETARIA.md](./issues/ISSUE-F1-02-003-IMPLEMENTAR-ENDPOINT-GET-API-V1-DASHBOARD-LEADS-ANALISE-ETARIA.md) |
| ISSUE-F1-02-004 | Testes unitários do endpoint de análise etária | Testes unitários do endpoint de análise etária | 3 | done | [ISSUE-F1-02-004-TESTES-UNITARIOS-DO-ENDPOINT-DE-ANALISE-ETARIA.md](./issues/ISSUE-F1-02-004-TESTES-UNITARIOS-DO-ENDPOINT-DE-ANALISE-ETARIA.md) |

## Artifact Minimo do Epico

- `backend/app/schemas/dashboard.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/routers/dashboard.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS-ETARIA.md)
- [Fase](./F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [Decision Protocol](../../DECISION-PROTOCOL.md)

## Notas de Implementacao Globais

- O módulo `dashboard.py` (router e schemas) deve ser estruturado para acomodar futuros
endpoints de dashboard sem refatoração
- Nomear o router com tag `dashboard` para agrupamento no OpenAPI
- O threshold de cobertura BB (80%) deve ser configurável via constante ou variável de
ambiente, não hardcoded no serviço

## Navegacao Rapida

- `[[./issues/ISSUE-F1-02-001-CRIAR-SCHEMAS-PYDANTIC-DA-ANALISE-ETARIA]]`
- `[[./issues/ISSUE-F1-02-002-IMPLEMENTAR-LOGICA-DE-QUERY-DA-ANALISE-ETARIA]]`
- `[[./issues/ISSUE-F1-02-003-IMPLEMENTAR-ENDPOINT-GET-API-V1-DASHBOARD-LEADS-ANALISE-ETARIA]]`
- `[[./issues/ISSUE-F1-02-004-TESTES-UNITARIOS-DO-ENDPOINT-DE-ANALISE-ETARIA]]`
- `[[../../PRD-DASHBOARD-LEADS-ETARIA]]`
