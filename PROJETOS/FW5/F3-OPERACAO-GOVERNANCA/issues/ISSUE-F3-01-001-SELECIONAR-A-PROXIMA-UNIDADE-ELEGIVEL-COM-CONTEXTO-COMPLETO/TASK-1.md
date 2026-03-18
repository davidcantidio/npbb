---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar work order, contexto e preflight de elegibilidade

## objetivo

Fechar a modelagem de work order, contexto de execucao e preflight que valida dependencias e gates.

## precondicoes

- F2 concluida
- backlog executavel disponivel no dominio

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_execution_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir contrato de work order com escopo, risco e contexto da unidade elegivel
  - cobrir preflight de dependencia, gate e `task_instruction_mode`
  - cobrir payload da proxima acao recomendada
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k work_order`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada ao contrato de work order
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes e serializacao sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k work_order`

## resultado_esperado

Contrato de work order pronto para selecionar a proxima unidade elegivel com contexto completo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py`

## stop_conditions

- parar se o preflight depender de politica de autonomia ainda nao modelada
- parar se o work order nao conseguir apontar a unidade executavel de forma estavel
