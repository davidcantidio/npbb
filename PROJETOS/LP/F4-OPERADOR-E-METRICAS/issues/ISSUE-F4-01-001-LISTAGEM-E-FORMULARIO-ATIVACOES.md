---
doc_id: "ISSUE-F4-01-001-LISTAGEM-E-FORMULARIO-ATIVACOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F4-01-001 - Listagem e formulário de ativações

## User Story

Como operador, quero listar ativações de um evento e criar/editar ativações via interface para configurar pontos de contato sem usar API diretamente.

## Contexto Tecnico

Página no frontend que lista ativações do evento (GET /eventos/:id/ativacoes) e permite criar (POST) e editar (PATCH). Formulário com nome, descrição, conversão única/múltipla. Protegido por autenticação de operador. Conforme PRD seção 12 (Fase 4).

## Plano TDD

- Red: testes E2E para listagem e CRUD
- Green: implementar páginas e formulários
- Refactor: extrair componentes

## Criterios de Aceitacao

- Given operador autenticado, When acesso página de ativações do evento, Then lista exibida
- Given clico em criar, When preencho formulário e submeto, Then ativação criada
- Given ativação existente, When clico em editar, Then formulário preenchido e PATCH ao salvar
- Given não autenticado, When acesso página, Then redirecionado para login

## Definition of Done da Issue

- [ ] Página de listagem de ativações por evento
- [ ] Formulário de criação/edição
- [ ] Campos: nome, descrição, conversão única/múltipla
- [ ] Protegido por autenticação
- [ ] Testes E2E

## Tarefas Decupadas

- [ ] T1: Criar página de listagem
- [ ] T2: Criar formulário de criação/edição
- [ ] T3: Integrar com API CRUD
- [ ] T4: Testes E2E

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Página de ativações
- Formulário
- Testes

## Dependencias

- [EPIC-F4-01](../EPIC-F4-01-INTERFACE-CONFIG-ATIVACOES.md)
- [F1](../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
