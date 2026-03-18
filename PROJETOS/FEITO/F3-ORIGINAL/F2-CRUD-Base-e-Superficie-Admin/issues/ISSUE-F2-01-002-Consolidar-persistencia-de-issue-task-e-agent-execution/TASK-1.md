---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-002-Consolidar-persistencia-de-issue-task-e-agent-execution"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Consolidar models de issue task e agent execution

## objetivo

alinhar models e migration do nivel operacional ao contrato aprovado

## precondicoes

- F1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_execution_models.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir relacionamentos `issue-task`, payload obrigatorio de task required e vinculos de `AgentExecution`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_models.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_models.py`

## resultado_esperado

Persistencia estavel do nivel operacional.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_models.py`

## stop_conditions

- parar se o payload de task required nao couber no modelo aprovado em F1
