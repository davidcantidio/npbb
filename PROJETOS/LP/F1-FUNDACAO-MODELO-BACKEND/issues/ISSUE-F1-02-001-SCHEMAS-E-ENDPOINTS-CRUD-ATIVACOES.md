---
doc_id: "ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-02-001 - Schemas e endpoints CRUD de ativações

## User Story

Como operador, quero criar, editar e listar ativações de um evento via API autenticada para configurar pontos de contato com QR e tipo de conversão.

## Contexto Tecnico

Endpoints sob `/eventos/:evento_id/ativacoes/:ativacao_id`. Autenticação JWT existente para operadores. Schemas Pydantic para request (create/update) e response (read). Conforme PRD seção 7.1.

## Plano TDD

- Red: testes para POST, GET list, GET by id, PATCH
- Green: implementar schemas e routers
- Refactor: extrair lógica comum

## Criterios de Aceitacao

- Given operador autenticado, When POST /eventos/:id/ativacoes com nome, conversao_unica, Then ativação criada
- Given ativações existentes, When GET /eventos/:id/ativacoes, Then lista retornada
- Given ativação existente, When GET /eventos/:id/ativacoes/:ativacao_id, Then ativação retornada
- Given ativação existente, When PATCH com nome, Then ativação atualizada
- Given requisição sem token, When qualquer endpoint, Then 401 Unauthorized
- Given evento inexistente, When POST, Then 404

## Definition of Done da Issue

- [ ] Schemas AtivacaoCreate, AtivacaoUpdate, AtivacaoRead
- [ ] POST, GET list, GET by id, PATCH implementados
- [ ] Endpoints protegidos por autenticação de operador
- [ ] Testes backend cobrindo CRUD e 401

## Tarefas Decupadas

- [ ] T1: Criar schemas Pydantic para Ativacao
- [ ] T2: Implementar router e endpoints CRUD
- [ ] T3: Registrar router e adicionar testes

## Instructions por Task

### T1
- objetivo: criar schemas AtivacaoCreate, AtivacaoUpdate, AtivacaoRead
- precondicoes: modelo Ativacao existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/schemas/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Criar AtivacaoCreate com nome (obrigatório), descricao (opcional), conversao_unica (default True)
  2. Criar AtivacaoUpdate com campos opcionais para PATCH
  3. Criar AtivacaoRead com todos os campos de leitura incluindo id, evento_id, created_at, updated_at
- comandos_permitidos:
  - `cd backend && python -c "from app.schemas.ativacao import AtivacaoCreate; print(AtivacaoCreate)"`
- resultado_esperado: schemas importáveis
- testes_ou_validacoes_obrigatorias:
  - validação Pydantic com dados válidos e inválidos
- stop_conditions:
  - parar se convenção de schemas do projeto for diferente

### T2
- objetivo: implementar router com POST, GET list, GET by id, PATCH
- precondicoes: T1 concluída; autenticação JWT existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/` ou `backend/app/routers/`
  - `backend/app/deps.py` (se existir para dependências)
- passos_atomicos:
  1. Criar router para /eventos/{evento_id}/ativacoes
  2. POST: validar evento existe, criar Ativacao, retornar AtivacaoRead
  3. GET list: listar ativações do evento
  4. GET by id: retornar ativação ou 404
  5. PATCH: atualizar parcialmente ou 404
  6. Aplicar dependência de autenticação em todos os endpoints
- comandos_permitidos:
  - `cd backend && python -m uvicorn app.main:app --reload` (para verificar)
- resultado_esperado: endpoints respondem corretamente
- testes_ou_validacoes_obrigatorias:
  - chamadas HTTP via TestClient
- stop_conditions:
  - parar se padrão de autenticação for diferente do esperado

### T3
- objetivo: registrar router e adicionar testes
- precondicoes: T2 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/main.py`
  - `backend/tests/`
- passos_atomicos:
  1. Registrar router de ativações no app (incluir prefixo se necessário)
  2. Criar testes que mockam autenticação e testam CRUD
  3. Testar 401 quando token ausente
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k ativacao`
- resultado_esperado: todos os testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest com cobertura de CRUD
- stop_conditions:
  - parar se fixtures de autenticação não existirem

## Arquivos Reais Envolvidos

- `backend/app/schemas/`
- `backend/app/api/` ou `backend/app/routers/`
- `backend/app/main.py`
- `backend/tests/`

## Artifact Minimo

- Schemas em `backend/app/schemas/`
- Router em `backend/app/`
- Testes em `backend/tests/`

## Dependencias

- [EPIC-F1-01](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
