---
doc_id: "ISSUE-F4-01-001-LISTAGEM-E-FORMULARIO-ATIVACOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 7.1 - Backend"
  - "PRD 12 - Fase 4 — Operador e Métricas"
  - "PRD 13.1 - Modelo e Ativações"
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

## Instructions por Task

### T1
- objetivo: criar a página de listagem de ativações do evento
- precondicoes: API CRUD de ativações disponível
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Definir rota/página de operador para ativações do evento
  2. Buscar a lista de ativações
  3. Exibir nome, descrição e tipo de conversão
  4. Tratar loading, vazio e erro
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operador autenticado enxerga todas as ativações do evento
- testes_ou_validacoes_obrigatorias:
  - teste de listagem
- stop_conditions:
  - parar se a navegação protegida de operador não estiver identificável

### T2
- objetivo: criar formulário de criação e edição de ativações
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Modelar campos `nome`, `descricao` e `conversao_unica`
  2. Diferenciar modos criar/editar
  3. Validar campos obrigatórios e estados de submissão
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operador consegue abrir e preencher o formulário corretamente
- testes_ou_validacoes_obrigatorias:
  - teste de formulário
- stop_conditions:
  - nenhuma

### T3
- objetivo: integrar página e formulário à API CRUD de ativações
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - cliente HTTP do frontend
- passos_atomicos:
  1. Conectar GET list, POST create e PATCH update
  2. Atualizar a listagem após criação/edição
  3. Garantir tratamento de erro e autenticação
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: operações de CRUD ficam disponíveis sem uso manual da API
- testes_ou_validacoes_obrigatorias:
  - teste de integração
- stop_conditions:
  - parar se o contrato real do CRUD divergir do planejado

### T4
- objetivo: cobrir a jornada do operador com E2E
- precondicoes: T1, T2 e T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/`
- passos_atomicos:
  1. Testar acesso autenticado à página
  2. Testar criação de ativação
  3. Testar edição de ativação existente
  4. Testar bloqueio/redirecionamento sem autenticação
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: fluxo principal do operador fica protegido
- testes_ou_validacoes_obrigatorias:
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

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
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
