---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-01-001-Selecionar-proxima-task-elegivel-e-montar-work-order-executavel"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Selecionar a proxima task elegivel

## objetivo

resolver a proxima unidade executavel respeitando hierarquia bloqueios e approvals

## precondicoes

- F3 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_next_task_selection.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir ordenacao por fase epico issue task exclusao de itens bloqueados e respeito a approvals
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_task_selection.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_task_selection.py`

## resultado_esperado

Proxima task elegivel determinada sem ambiguidade.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_task_selection.py`

## stop_conditions

- parar se a governanca permitir multiplas tasks equivalentes sem criterio de desempate
