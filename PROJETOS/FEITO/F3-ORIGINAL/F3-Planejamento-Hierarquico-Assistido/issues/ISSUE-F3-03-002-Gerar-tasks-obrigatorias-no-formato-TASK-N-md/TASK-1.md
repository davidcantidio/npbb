---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-03-002-Gerar-tasks-obrigatorias-no-formato-TASK-N-md"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Gerar `TASK-N.md` obrigatorias

## objetivo

criar tasks required a partir da issue aprovada

## precondicoes

- `ISSUE-F3-03-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_task_generation.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir quantidade numeracao e campos minimos de `TASK-N.md`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_generation.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_generation.py`

## resultado_esperado

Passos 13 e 14 cobertos com `TASK_MODE=required`.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_generation.py`

## stop_conditions

- parar se a issue aprovada vier com SP ou tarefas incompativeis com limites canonicos
