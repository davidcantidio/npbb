---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar issues, tasks, dependencias e metadados de sprint

## objetivo

Completar a modelagem do dominio para issues, tasks, dependencias e relacao com sprint.

## precondicoes

- ISSUE-F2-01-001 concluida
- fase e epicos ja possuem IDs e dependencias estaveis

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_planning_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir entidades de issue/task com `Feature de Origem`, dependencia e formato canonic
  - cobrir metadados minimos de sprint para selecao operacional
  - cobrir serializacao da hierarquia detalhada da issue e da task
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k task`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k task`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato de issue/task
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes e serializacao sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k task`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k task`

## resultado_esperado

Modelagem de issue/task pronta para derivacao detalhada e selecao em sprint.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k task`

## stop_conditions

- parar se a modelagem ultrapassar o limite canonico e exigir novo nivel documental
- parar se a relacao com sprint depender de regra nao declarada pelo framework
