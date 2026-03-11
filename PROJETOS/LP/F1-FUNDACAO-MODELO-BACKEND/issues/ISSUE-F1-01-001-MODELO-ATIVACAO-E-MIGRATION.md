---
doc_id: "ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 6.1 - Tabela ativacao"
  - "PRD 7.3 - Banco / Migrações"
  - "PRD 13.1 - Modelo e Ativações"
---

# ISSUE-F1-01-001 - Modelo Ativacao e migration

## User Story

Como engenheiro de backend, quero validar e alinhar o suporte existente de `Ativacao` e da chain Alembic para garantir que as ativacoes vinculadas a eventos permanecam cobertas pelo contrato atual do repositorio.

## Contexto Tecnico

O repositorio ja possui `Ativacao` em `backend/app/models/models.py`, a tabela `ativacao` na chain historica do Alembic e superficies backend que expoem o campo `checkin_unico`. Nesta execucao, o contrato vigente foi preservado sem introduzir `conversao_unica`, e a evidencia da issue passou a ser a validacao da importacao do modelo, da chain Alembic em PostgreSQL e dos testes filtrados de ativacao.

## Plano TDD

- Red: verificar se existia gap real entre a issue e o estado atual do repositorio
- Green: validar o modelo `Ativacao`, a chain Alembic existente e a cobertura de testes ja disponivel
- Refactor: alinhar a documentacao da issue ao contrato vigente em `checkin_unico`

## Criterios de Aceitacao

- [x] Given modelo `Ativacao` existente, When importo a classe, Then a importacao ocorre sem erro
- [x] Given chain Alembic existente, When executo `alembic upgrade head` em PostgreSQL, Then a migration aplica sem erro
- [x] Given banco no head, When executo `alembic downgrade -1` e `alembic upgrade head`, Then o rollback imediato e o retorno ao head ocorrem sem erro
- [x] Given cobertura backend existente para ativacao, When executo `pytest -q -k ativacao`, Then os testes passam
- [x] Given o contrato atual do repositorio, When leio a superficie backend, Then o campo booleano oficial continua sendo `checkin_unico`

## Definition of Done da Issue

- [x] Modelo `Ativacao` em `backend/app/models/models.py` validado no contrato vigente do repositorio
- [x] Chain Alembic existente validada em PostgreSQL com upgrade, downgrade imediato e retorno ao head
- [x] `alembic upgrade head` e `alembic downgrade -1` executam sem erro
- [x] Testes de criacao/leitura de Ativacao passam

## Tarefas Decupadas

- [x] T1: Validar modelo Ativacao existente em models.py
- [x] T2: Validar a chain Alembic existente para `ativacao`
- [x] T3: Validar upgrade/downgrade e testes

## Instructions por Task

### T1
- objetivo: validar a classe `Ativacao` existente no `models.py` e confirmar que o contrato vigente segue `checkin_unico`
- precondicoes: arquivo models.py existente; tabela evento existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Importar a classe `Ativacao` a partir de `app.models.models`
  2. Confirmar que a tabela `ativacao` e o relacionamento com `Evento` ja existem
  3. Confirmar que o booleano exposto no contrato atual e `checkin_unico`
- comandos_permitidos:
  - `cd backend && python -c "from app.models.models import Ativacao; print(Ativacao)"`
- resultado_esperado: classe `Ativacao` importavel sem erro
- testes_ou_validacoes_obrigatorias:
  - importacao sem erro
- stop_conditions:
  - parar se houver conflito de nomes com modelos existentes

### T2
- objetivo: validar a chain Alembic existente para `ativacao` em PostgreSQL sem gerar migration artificial
- precondicoes: T1 concluída; revision base identificada
- arquivos_a_ler_ou_tocar:
  - `backend/alembic/versions/`
  - `backend/alembic/env.py`
- passos_atomicos:
  1. Confirmar que a chain Alembic ja contem a criacao de `ativacao`
  2. Executar `alembic upgrade head` em PostgreSQL configurado
  3. Executar `alembic downgrade -1` e `alembic upgrade head` para validar rollback imediato e retorno ao head
- comandos_permitidos:
  - `cd backend && alembic upgrade head`
  - `cd backend && alembic downgrade -1`
- resultado_esperado: chain sobe, desce um passo e retorna ao head sem erro
- testes_ou_validacoes_obrigatorias:
  - `alembic upgrade head`
  - `alembic downgrade -1`
- stop_conditions:
  - parar se houver migration concorrente ou conflito de revision

### T3
- objetivo: validar a cobertura existente de `Ativacao` e evitar criacao de testes sem gap objetivo
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
  - `backend/alembic/versions/`
- passos_atomicos:
  1. Executar `pytest -q -k ativacao`
  2. Confirmar que a cobertura existente ja valida criacao/leitura e superficies de ativacao
  3. Nao adicionar teste novo se nao houver gap objetivo
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

- validacao do modelo `Ativacao` existente
- validacao da chain Alembic existente em PostgreSQL

## Evidencias de Execucao

- Import do modelo: `from app.models.models import Ativacao` executado sem erro
- Alembic em PostgreSQL: `upgrade head` -> `downgrade -1` -> `upgrade head` executados sem erro
- Testes: `pytest -q -k ativacao` -> `16 passed, 352 deselected`

## Dependencias

- [Epic](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [Fase](../F1_LP_EPICS.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
