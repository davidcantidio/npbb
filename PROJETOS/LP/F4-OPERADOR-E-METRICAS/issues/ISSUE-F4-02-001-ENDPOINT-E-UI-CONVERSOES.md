---
doc_id: "ISSUE-F4-02-001-ENDPOINT-E-UI-CONVERSOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 9.2 - Métricas Leading"
  - "PRD 12 - Fase 4 — Operador e Métricas"
  - "PRD 13.4 - Conversão por Ativação"
---

# ISSUE-F4-02-001 - Endpoint e UI de conversões por ativação

## User Story

Como operador, quero visualizar quantas conversões cada ativação teve para avaliar desempenho dos pontos de contato.

## Contexto Tecnico

Endpoint GET /eventos/:id/ativacoes/:ativacao_id/conversoes ou agregado em GET ativações. Retorna contagem ou lista de conversões. UI: tabela ou cards com conversões por ativação. Conforme PRD seções 9 e 12 (Fase 4).

## Plano TDD

- Red: testes para endpoint e UI
- Green: implementar
- Refactor: extrair componentes

## Criterios de Aceitacao

- Given evento com ativações, When GET conversões, Then contagem por ativação retornada
- Given operador autenticado, When acesso página de ativações, Then conversões exibidas
- Given ativação sem conversões, When visualizo, Then 0 exibido

## Definition of Done da Issue

- [ ] Endpoint ou extensão que retorna conversões por ativação
- [ ] UI exibe conversões na listagem ou detalhe
- [ ] Protegido por autenticação
- [ ] Testes backend e E2E

## Tarefas Decupadas

- [ ] T1: Implementar endpoint ou agregado de conversões
- [ ] T2: UI para exibir conversões
- [ ] T3: Integrar na página de ativações
- [ ] T4: Testes

## Instructions por Task

### T1
- objetivo: expor conversões por ativação para uso da UI de operador
- precondicoes: `conversao_ativacao` já persistida no backend
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/`
  - `backend/app/services/`
  - `backend/tests/`
- passos_atomicos:
  1. Decidir se o dado entra em endpoint dedicado ou agregado do GET de ativações existente
  2. Retornar contagem ou lista suficiente para a UI planejada
  3. Proteger o acesso com autenticação de operador
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k convers`
- resultado_esperado: backend expõe dados de conversão por ativação de forma consumível
- testes_ou_validacoes_obrigatorias:
  - teste backend
- stop_conditions:
  - parar se não houver fonte de autenticação de operador disponível

### T2
- objetivo: exibir conversões por ativação na interface do operador
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Definir apresentação em tabela, cards ou coluna na listagem
  2. Exibir contagem de conversões por ativação
  3. Tratar zero conversões e erro de carregamento
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operador enxerga desempenho básico de cada ativação
- testes_ou_validacoes_obrigatorias:
  - teste de UI
- stop_conditions:
  - nenhuma

### T3
- objetivo: integrar a visualização de conversões à página de ativações
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - cliente HTTP do frontend
- passos_atomicos:
  1. Consumir o endpoint/agregado definido em T1
  2. Renderizar os dados junto da listagem ou detalhe
  3. Garantir atualização após recarregar ou alterar ativações
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: dados de conversão ficam disponíveis no fluxo natural do operador
- testes_ou_validacoes_obrigatorias:
  - teste de integração
- stop_conditions:
  - nenhuma

### T4
- objetivo: cobrir backend e UI com testes
- precondicoes: T1, T2 e T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
  - `frontend/e2e/`
- passos_atomicos:
  1. Testar retorno de contagem por ativação no backend
  2. Testar exibição das conversões na UI
  3. Testar caso sem conversões exibindo zero
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k convers`
  - `cd frontend && npx playwright test`
- resultado_esperado: agregados de conversão e UI ficam protegidos contra regressão
- testes_ou_validacoes_obrigatorias:
  - pytest
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `backend/app/api/`
- `frontend/src/`
- `backend/tests/`
- `frontend/e2e/`

## Artifact Minimo

- Endpoint ou agregado
- UI de conversões
- Testes

## Dependencias

- [EPIC-F4-02](../EPIC-F4-02-VISUALIZACAO-CONVERSOES-METRICAS.md)
- [F1](../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
