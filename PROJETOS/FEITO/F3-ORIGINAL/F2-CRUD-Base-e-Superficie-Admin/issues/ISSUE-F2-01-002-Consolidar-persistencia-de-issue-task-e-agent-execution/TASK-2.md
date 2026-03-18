---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Consolidar schemas de issue task e agent execution

## objetivo

alinhar payloads operacionais aos models aprovados

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_execution_schemas.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir validacao de `FrameworkIssue*`, `FrameworkTask*` e `FrameworkExecution*`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_schemas.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_schemas.py`

## resultado_esperado

Payloads operacionais coerentes com o dominio.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_schemas.py`

## stop_conditions

- parar se algum schema exigir redefinir a maquina de estados
