---
doc_id: "ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Modelo Ativacao e migration

## User Story

Como engenheiro de backend, quero criar o modelo `Ativacao` e a migration Alembic correspondente para suportar ativações vinculadas a eventos, cada uma com QR único e flag de conversão única/múltipla.

## Contexto Tecnico

Conforme PRD seção 6.1: tabela `ativacao` com id, evento_id, nome, descricao, conversao_unica, qr_code_url, created_at, updated_at. O modelo deve usar SQLModel e seguir o padrão existente em `backend/app/models/models.py`.

## Plano TDD

- Red: criar ou ajustar testes para validar criação de Ativacao e campos obrigatórios
- Green: implementar modelo e migration
- Refactor: alinhar nomes e convenções ao restante do codebase

## Criterios de Aceitacao

- Given modelo Ativacao criado, When aplico migration, Then tabela `ativacao` existe com todos os campos
- Given migration aplicada, When executo downgrade, Then tabela é removida sem efeito colateral
- Given evento existente, When crio Ativacao com evento_id, Then registro persiste corretamente
- Given Ativacao criada, When leio conversao_unica, Then valor boolean é retornado

## Definition of Done da Issue

- [ ] Modelo `Ativacao` em `backend/app/models/models.py` com campos conforme PRD
- [ ] Migration Alembic criada com upgrade e downgrade válidos
- [ ] `alembic upgrade head` e `alembic downgrade -1` executam sem erro
- [ ] Testes de criação/leitura de Ativacao passam

## Tarefas Decupadas

- [ ] T1: Criar modelo Ativacao em models.py
- [ ] T2: Criar migration Alembic para tabela ativacao
- [ ] T3: Validar upgrade/downgrade e testes

## Instructions por Task

### T1
- objetivo: adicionar classe Ativacao ao models.py com todos os campos do PRD
- precondicoes: arquivo models.py existente; tabela evento existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Importar SQLModel, Field, relationship se necessário
  2. Criar classe Ativacao com id, evento_id (FK), nome, descricao (Optional), conversao_unica (bool, default True), qr_code_url (Optional), created_at, updated_at
  3. Definir relacao com Evento
- comandos_permitidos:
  - `cd backend && python -c "from app.models.models import Ativacao; print(Ativacao)"`
- resultado_esperado: classe Ativacao importável sem erro
- testes_ou_validacoes_obrigatorias:
  - importação sem erro
- stop_conditions:
  - parar se houver conflito de nomes com modelos existentes

### T2
- objetivo: criar migration Alembic para tabela ativacao
- precondicoes: T1 concluída; revision base identificada
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/versions/`
  - `backend/alembic/env.py`
- passos_atomicos:
  1. Gerar migration: `alembic revision -m "add_ativacao_table"`
  2. Implementar upgrade() criando tabela ativacao com colunas conforme modelo
  3. Implementar downgrade() removendo tabela ativacao
- comandos_permitidos:
  - `cd backend && alembic revision -m "add_ativacao_table"`
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- resultado_esperado: migration sobe e desce sem erro
- testes_ou_validacoes_obrigatorias:
  - `alembic upgrade head`
  - `alembic downgrade -1`
- stop_conditions:
  - parar se houver migration concorrente ou conflito de revision

### T3
- objetivo: validar upgrade/downgrade em ambiente de teste e adicionar testes de modelo
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. Executar alembic upgrade head em ambiente de teste
  2. Criar ou atualizar teste que cria Ativacao e valida campos
  3. Executar downgrade e validar
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k ativacao`
- resultado_esperado: testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest com filtro ativacao
- stop_conditions:
  - parar se migration falhar em banco com dados existentes

## Arquivos Reais Envolvidos

- `backend/app/models/models.py`
- `backend/alembic/versions/`
- `backend/tests/`

## Artifact Minimo

- `backend/app/models/models.py` com classe Ativacao
- `backend/alembic/versions/xxxx_add_ativacao_table.py`

## Dependencias

- [Epic](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [Fase](../F1_LP_EPICS.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
