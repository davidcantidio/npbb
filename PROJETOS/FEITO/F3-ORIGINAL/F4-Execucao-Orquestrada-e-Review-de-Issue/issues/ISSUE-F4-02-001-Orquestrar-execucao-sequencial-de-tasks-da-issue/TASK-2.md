---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F4-02-001-Orquestrar-execucao-sequencial-de-tasks-da-issue"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Registrar execucao e fechamento por task

## objetivo

persistir agente executor horario resumo e status final de cada task

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_task_completion.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir `executed_by_agent`, `executed_at`, `result_summary` e transicao de status da task
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_completion.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_completion.py`

## resultado_esperado

Execucao por task fica registrada e encerrada corretamente.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_task_completion.py`

## stop_conditions

- parar se a conclusao exigir fluxo de review antecipado
