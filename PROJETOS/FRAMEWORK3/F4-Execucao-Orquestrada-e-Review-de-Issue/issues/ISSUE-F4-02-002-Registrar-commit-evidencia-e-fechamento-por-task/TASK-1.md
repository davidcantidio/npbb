---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-02-002-Registrar-commit-evidencia-e-fechamento-por-task"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Exigir commit e evidencia no fechamento da task

## objetivo

bloquear conclusao de task sem `commit_ref` e `evidence_ref`

## precondicoes

- `ISSUE-F4-02-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_commit_evidence.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir obrigatoriedade de `commit_ref` e `evidence_ref` no fechamento da task
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_commit_evidence.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_commit_evidence.py`

## resultado_esperado

Task so encerra com rastreabilidade minima.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_commit_evidence.py`

## stop_conditions

- parar se a politica de commit por task divergir de `GOV-COMMIT-POR-TASK`
