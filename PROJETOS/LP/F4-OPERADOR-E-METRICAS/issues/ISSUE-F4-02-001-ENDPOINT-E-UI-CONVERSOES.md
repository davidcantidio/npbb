---
doc_id: "ISSUE-F4-02-001-ENDPOINT-E-UI-CONVERSOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
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
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
