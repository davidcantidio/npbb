---
doc_id: "ISSUE-F1-02-003-IMPLEMENTAR-ENDPOINT-GET-API-V1-DASHBOARD-LEADS-ANALISE-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F1-02-003 - Implementar endpoint GET /dashboard/leads/analise-etaria

## User Story

Como engenheiro de backend do dashboard, quero entregar Implementar endpoint GET /dashboard/leads/analise-etaria para cumprir o objetivo tecnico do epico sem quebrar o contrato ja definido para o dashboard.

## Contexto Tecnico

Manter o router FastAPI com o endpoint `GET /dashboard/leads/analise-etaria`,
integrando autenticacao JWT, validacao de query params e chamada ao servico de analise
etaria. Nesta issue, o foco final e fechar a documentacao OpenAPI com exemplos e alinhar
os artefatos imediatos da fase ao contrato real da rota interna.

Sem observacoes adicionais alem das dependencias e restricoes do epico.

## Plano TDD

- Red: criar ou ajustar testes para reproduzir a lacuna descrita nos criterios de aceitacao.
- Green: implementar o comportamento minimo necessario para fazer os testes passarem.
- Refactor: consolidar nomes, extracoes e contratos sem ampliar o escopo da issue.

## Criterios de Aceitacao

- [x] Rota `GET /dashboard/leads/analise-etaria` registrada no app
- [x] Query params: `evento_id` (int, opcional), `data_inicio` (date, opcional), `data_fim` (date, opcional)
- [x] Resposta tipada como `AgeAnalysisResponse` com status 200
- [x] Autenticacao JWT obrigatoria - retorna 401 sem token valido
- [x] Documentacao OpenAPI auto-gerada com descricao do endpoint e exemplos
- [x] Retorna 200 com dados vazios (nao 404) quando filtro nao encontra leads

## Definition of Done da Issue

- [x] Rota `GET /dashboard/leads/analise-etaria` registrada no app
- [x] Query params: `evento_id` (int, opcional), `data_inicio` (date, opcional), `data_fim` (date, opcional)
- [x] Resposta tipada como `AgeAnalysisResponse` com status 200
- [x] Autenticacao JWT obrigatoria - retorna 401 sem token valido
- [x] Documentacao OpenAPI auto-gerada com descricao do endpoint e exemplos
- [x] Retorna 200 com dados vazios (nao 404) quando filtro nao encontra leads

## Tarefas Decupadas

- [x] T1: Criar `backend/app/routers/dashboard.py` com router prefix `/dashboard`
- [x] T2: Implementar endpoint com dependencia de autenticacao
- [x] T3: Validar e documentar query params
- [x] T4: Registrar router no app principal (`backend/app/main.py`)
- [x] T5: Validar contrato do endpoint e da documentacao OpenAPI com diferentes combinacoes de filtros

## Arquivos Reais Envolvidos

- `backend/app/routers/dashboard.py`
- `backend/app/main.py`
- `backend/app/schemas/dashboard.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`

## Artifact Minimo

- `backend/app/routers/dashboard.py`

## Dependencias

- [Issue Dependente](./ISSUE-F1-02-002-IMPLEMENTAR-LOGICA-DE-QUERY-DA-ANALISE-ETARIA.md)
- [Epic](../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA.md)
- [Fase](../F1_DASHBOARD_LEADS_ETARIA_EPICS.md)
- [PRD](../../../PRD-DASHBOARD-LEADS-ETARIA.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-ENDPOINT-ANALISE-ETARIA]]`
- `[[../../../PRD-DASHBOARD-LEADS-ETARIA]]`
