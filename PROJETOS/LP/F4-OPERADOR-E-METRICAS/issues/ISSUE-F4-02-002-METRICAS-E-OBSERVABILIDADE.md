---
doc_id: "ISSUE-F4-02-002-METRICAS-E-OBSERVABILIDADE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 9.2 - Métricas Leading"
  - "PRD 9.3 - Métricas Lagging"
  - "PRD 12 - Fase 4 — Operador e Métricas"
---

# ISSUE-F4-02-002 - Métricas e observabilidade

## User Story

Como operador, quero acessar métricas leading e lagging do fluxo de QR por ativação para avaliar desempenho operacional e resultado de negócio.

## Contexto Tecnico

Métricas leading: número de ativações por evento, conversões por ativação, taxa de reconhecimento. Métricas lagging: conversões atribuíveis e redução de abandono por repetição de CPF. Endpoint ou dashboard. Logs e métricas expostas para observabilidade. Conforme PRD seções 9 e 12.

## Plano TDD

- Red: testes para endpoints de métricas
- Green: implementar agregados e UI
- Refactor: extrair cálculos

## Criterios de Aceitacao

- Given evento, When consulto métricas, Then ativações por evento retornado
- Given ativações, When consulto, Then conversões por ativação
- Given dados de reconhecimento, When calculo, Then taxa de reconhecimento
- Given dados do período/evento, When consulto métricas lagging, Then conversões atribuíveis são exibidas
- Given histórico comparável do fluxo, When consulto métricas lagging, Then redução de abandono por repetição de CPF é exibida
- Given operador, When acesso dashboard, Then KPIs exibidos

## Definition of Done da Issue

- [ ] Endpoint ou dados para métricas leading e lagging
- [ ] UI exibe KPIs de ativações, conversões, taxa de reconhecimento, conversões atribuíveis e redução de abandono por repetição de CPF
- [ ] Logs relevantes para debugging
- [ ] Testes

## Tarefas Decupadas

- [ ] T1: Implementar cálculos de métricas no backend
- [ ] T2: Endpoint ou extensão para métricas
- [ ] T3: UI de KPIs
- [ ] T4: Logs e observabilidade básica

## Instructions por Task

### T1
- objetivo: implementar os cálculos/agregados de métricas leading e lagging previstos no PRD
- precondicoes: dados de ativações, conversões e reconhecimento disponíveis no backend
- arquivos_a_ler_ou_tocar:
  - `backend/app/services/`
  - `backend/app/api/`
  - `backend/tests/`
- passos_atomicos:
  1. Implementar agregados de ativações por evento, conversões por ativação e taxa de reconhecimento
  2. Implementar agregados para conversões atribuíveis e redução de abandono por repetição de CPF conforme os dados disponíveis
  3. Quando algum KPI lagging depender de histórico/base auxiliar, documentar explicitamente a dependência no próprio endpoint ou serviço
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k metric`
- resultado_esperado: backend produz os números ou agregados necessários para todos os KPIs prometidos
- testes_ou_validacoes_obrigatorias:
  - teste backend dos cálculos
- stop_conditions:
  - parar se faltar dado mínimo para algum KPI lagging e registrar a lacuna no artefato da issue

### T2
- objetivo: expor as métricas em endpoint ou extensão consumível pela UI
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/`
  - `backend/tests/`
- passos_atomicos:
  1. Definir shape de resposta para KPIs leading e lagging
  2. Proteger acesso por autenticação de operador
  3. Garantir resposta consistente mesmo com valores zerados ou indisponíveis
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k metric`
- resultado_esperado: UI consegue consumir um contrato único de métricas
- testes_ou_validacoes_obrigatorias:
  - teste de endpoint
- stop_conditions:
  - parar se a estratégia de agregação conflitar com o endpoint de conversões já definido

### T3
- objetivo: exibir os KPIs de métricas na interface do operador
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Definir apresentação dos KPIs leading e lagging
  2. Exibir estados de carregamento, vazio e indisponibilidade de forma explícita
  3. Integrar o bloco de métricas à área de operador já existente
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operador enxerga no mesmo fluxo os indicadores operacionais e de resultado
- testes_ou_validacoes_obrigatorias:
  - teste de UI
- stop_conditions:
  - nenhuma

### T4
- objetivo: adicionar logs e cobertura de observabilidade básica para o fluxo de métricas
- precondicoes: T1, T2 e T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/app/`
  - `backend/tests/`
  - `frontend/e2e/` quando aplicável
- passos_atomicos:
  1. Adicionar logs úteis para cálculo e exposição das métricas
  2. Cobrir endpoint e UI com testes automatizados
  3. Validar cenários com dados zerados e com métricas lagging disponíveis
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k metric`
  - `cd frontend && npx playwright test`
- resultado_esperado: fluxo de métricas fica observável e protegido contra regressão
- testes_ou_validacoes_obrigatorias:
  - pytest
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

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
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
