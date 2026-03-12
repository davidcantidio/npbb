---
doc_id: "ISSUE-F1-01-002-MODELOS-CONVERSAO-E-TOKEN.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
task_instruction_mode: "required"
decision_refs:
  - "PRD 6.2 - Tabela conversao_ativacao"
  - "PRD 6.3 - Token de Reconhecimento"
  - "PRD 7.3 - Banco / Migrações"
---

# ISSUE-F1-01-002 - Modelos conversao_ativacao e lead_reconhecimento_token

## User Story

Como engenheiro de backend, quero criar os modelos `ConversaoAtivacao` e `LeadReconhecimentoToken` com migrations para suportar registro de conversões por ativação e reconhecimento de leads entre ativações do mesmo evento.

## Contexto Tecnico

Conforme PRD seções 6.2 e 6.3:
- `conversao_ativacao`: id, ativacao_id, lead_id, cpf, created_at; índice composto (ativacao_id, cpf)
- `lead_reconhecimento_token`: lead_id, evento_id, token_hash, expires_at

## Plano TDD

- Red: testes para criação de ConversaoAtivacao e LeadReconhecimentoToken
- Green: implementar modelos e migrations
- Refactor: alinhar convenções

## Criterios de Aceitacao

- Given modelo ConversaoAtivacao, When aplico migration, Then tabela existe com índice (ativacao_id, cpf)
- Given modelo LeadReconhecimentoToken, When aplico migration, Then tabela existe com índice em token_hash
- Given migrations aplicadas, When executo downgrade, Then tabelas removidas sem efeito colateral
- Given conversão criada, When busco por (ativacao_id, cpf), Then lookup é eficiente

## Definition of Done da Issue

- [x] Modelo `ConversaoAtivacao` com id, ativacao_id, lead_id, cpf, created_at
- [x] Modelo `LeadReconhecimentoToken` com lead_id, evento_id, token_hash, expires_at
- [x] Índice composto (ativacao_id, cpf) em conversao_ativacao
- [x] Índice em token_hash em lead_reconhecimento_token
- [x] Migrations aplicáveis e com downgrade válido
- [x] Testes de criação/leitura passam

## Tarefas Decupadas

- [x] T1: Criar modelo ConversaoAtivacao e migration
- [x] T2: Criar modelo LeadReconhecimentoToken e migration
- [x] T3: Validar upgrade/downgrade e testes

## Instructions por Task

### T1
- objetivo: criar modelo ConversaoAtivacao e migration
- precondicoes: ISSUE-F1-01-001 concluída; tabelas ativacao e lead existem
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. Adicionar classe ConversaoAtivacao com id, ativacao_id (FK), lead_id (FK), cpf, created_at
  2. Definir relacoes com Ativacao e Lead
  3. Gerar migration com índice composto UniqueConstraint ou Index em (ativacao_id, cpf) conforme necessidade de unicidade
  4. Implementar upgrade e downgrade
- comandos_permitidos:
  - `cd backend && alembic revision -m "add_conversao_ativacao"`
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- resultado_esperado: migration sobe e desce sem erro
- testes_ou_validacoes_obrigatorias:
  - alembic upgrade head; alembic downgrade -1
- stop_conditions:
  - parar se FK para ativacao ou lead não existir

### T2
- objetivo: criar modelo LeadReconhecimentoToken e migration
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. Adicionar classe LeadReconhecimentoToken com lead_id, evento_id, token_hash, expires_at
  2. Definir relacoes com Lead e Evento
  3. Adicionar índice em token_hash para lookup rápido
  4. Gerar migration e implementar upgrade/downgrade
- comandos_permitidos:
  - `cd backend && alembic revision -m "add_lead_reconhecimento_token"`
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- resultado_esperado: migration sobe e desce sem erro
- testes_ou_validacoes_obrigatorias:
  - alembic upgrade head; alembic downgrade -1
- stop_conditions:
  - parar se FK para lead ou evento não existir

### T3
- objetivo: validar upgrade/downgrade em sequência e adicionar testes
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
- passos_atomicos:
  1. Executar upgrade head completo (incluindo F1-01-001)
  2. Criar testes que instanciam ConversaoAtivacao e LeadReconhecimentoToken
  3. Executar downgrade e validar
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k "conversao or token"`
- resultado_esperado: testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest
- stop_conditions:
  - parar se ordem de migrations causar conflito

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/alembic/versions/`
- `backend/tests/`

## Artifact Minimo

- `backend/app/models/models.py` com ConversaoAtivacao e LeadReconhecimentoToken
- `backend/alembic/versions/` com migrations

## Dependencias

- [ISSUE-F1-01-001](./ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md)
- [Epic](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
