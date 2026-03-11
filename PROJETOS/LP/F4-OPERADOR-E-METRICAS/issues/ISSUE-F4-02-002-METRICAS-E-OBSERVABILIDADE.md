---
doc_id: "ISSUE-F4-02-002-METRICAS-E-OBSERVABILIDADE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F4-02-002 - Métricas e observabilidade

## User Story

Como operador, quero acessar métricas (ativações por evento, conversões por ativação, taxa de reconhecimento) para avaliar o desempenho do fluxo de QR por ativação.

## Contexto Tecnico

Métricas leading: número de ativações por evento, conversões por ativação, taxa de reconhecimento. Métricas lagging: conversões atribuíveis, redução de abandono. Endpoint ou dashboard. Logs e métricas expostas para observabilidade. Conforme PRD seção 9.

## Plano TDD

- Red: testes para endpoints de métricas
- Green: implementar agregados e UI
- Refactor: extrair cálculos

## Criterios de Aceitacao

- Given evento, When consulto métricas, Then ativações por evento retornado
- Given ativações, When consulto, Then conversões por ativação
- Given dados de reconhecimento, When calculo, Then taxa de reconhecimento
- Given operador, When acesso dashboard, Then KPIs exibidos

## Definition of Done da Issue

- [ ] Endpoint ou dados para métricas leading
- [ ] UI exibe KPIs (ativações, conversões, taxa reconhecimento)
- [ ] Logs relevantes para debugging
- [ ] Testes

## Tarefas Decupadas

- [ ] T1: Implementar cálculos de métricas no backend
- [ ] T2: Endpoint ou extensão para métricas
- [ ] T3: UI de KPIs
- [ ] T4: Logs e observabilidade básica

## Arquivos Reais Envolvidos

- `backend/app/api/` ou `backend/app/services/`
- `frontend/src/`
- `backend/tests/`

## Artifact Minimo

- Endpoints/dados de métricas
- UI de KPIs
- Logs

## Dependencias

- [ISSUE-F4-02-001](./ISSUE-F4-02-001-ENDPOINT-E-UI-CONVERSOES.md)
- [EPIC-F4-02](../EPIC-F4-02-VISUALIZACAO-CONVERSOES-METRICAS.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
