---
doc_id: "ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Extensão POST /leads com ativacao_id e registro de conversão

## User Story

Como sistema, quero que o POST /leads aceite ativacao_id e registre a conversão em conversao_ativacao, para atribuir cada lead à ativação correspondente.

## Contexto Tecnico

Estender request do POST /leads com ativacao_id (obrigatório quando acesso via ativação). Ao criar/atualizar lead, inserir registro em conversao_ativacao. Response: conversao_registrada, bloqueado_cpf_duplicado. Conforme PRD seções 7.1 e 8.2.

## Plano TDD

- Red: testes para POST com ativacao_id e registro de conversão
- Green: implementar extensão
- Refactor: extrair serviço de conversão

## Criterios de Aceitacao

- Given POST /leads com ativacao_id e dados válidos, When submeto, Then lead criado e conversão registrada
- Given ativacao_id inexistente, When POST, Then 400 ou 404
- Given lead existente (por email/cpf) e ativacao_id, When POST, Then conversão registrada para lead existente
- Given response, When sucesso, Then conversao_registrada = true

## Definition of Done da Issue

- [ ] Request aceita ativacao_id
- [ ] Conversão registrada em conversao_ativacao (lead_id, ativacao_id, cpf)
- [ ] Response inclui conversao_registrada
- [ ] Testes backend cobrindo cenários

## Tarefas Decupadas

- [ ] T1: Estender schema de request e response
- [ ] T2: Implementar lógica de registro de conversão
- [ ] T3: Adicionar testes

## Instructions por Task

### T1
- objetivo: estender schemas de request e response do POST /leads
- precondicoes: endpoint POST /leads existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/schemas/`
  - `backend/app/api/` ou routers de leads
- passos_atomicos:
  1. Adicionar ativacao_id (Optional[int]) ao schema de criação de lead
  2. Adicionar conversao_registrada (bool) e bloqueado_cpf_duplicado (bool) ao response
  3. Manter retrocompatibilidade: ativacao_id opcional quando não via ativação
- comandos_permitidos:
  - `cd backend && python -c "from app.schemas.lead import LeadCreate; print(LeadCreate)"`
- resultado_esperado: schemas atualizados
- testes_ou_validacoes_obrigatorias:
  - validação Pydantic
- stop_conditions:
  - parar se estrutura atual do POST /leads for muito diferente

### T2
- objetivo: implementar lógica de registro de conversão no fluxo do POST /leads
- precondicoes: T1 concluída; modelo ConversaoAtivacao existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/` ou `backend/app/services/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. No handler do POST /leads, se ativacao_id presente: validar ativação existe
  2. Após criar/obter lead, inserir em conversao_ativacao (lead_id, ativacao_id, cpf)
  3. Retornar conversao_registrada = True
  4. Tratar bloqueio de CPF duplicado (próxima issue) — aqui apenas registrar
- comandos_permitidos:
  - `cd backend && python -m uvicorn app.main:app --reload`
- resultado_esperado: conversão registrada
- testes_ou_validacoes_obrigatorias:
  - teste que verifica registro em conversao_ativacao
- stop_conditions:
  - parar se transação não garantir consistência

### T3
- objetivo: adicionar testes para extensão
- precondicoes: T2 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
- passos_atomicos:
  1. Teste: POST com ativacao_id cria lead e conversão
  2. Teste: ativacao_id inexistente retorna erro
  3. Teste: response inclui conversao_registrada
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k "leads and ativacao"`
- resultado_esperado: testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest
- stop_conditions:
  - parar se fixtures de evento/ativação não existirem

## Arquivos Reais Envolvidos

- `backend/app/schemas/`
- `backend/app/api/` ou `backend/app/services/`
- `backend/tests/`

## Artifact Minimo

- Schemas atualizados
- Lógica de conversão
- Testes

## Dependencias

- [EPIC-F1-01](../../F1-FUNDACAO-MODELO-BACKEND/EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
