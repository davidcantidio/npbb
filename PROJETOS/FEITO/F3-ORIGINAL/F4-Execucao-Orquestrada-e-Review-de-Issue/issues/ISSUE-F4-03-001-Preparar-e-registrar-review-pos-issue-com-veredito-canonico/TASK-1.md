---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-03-001-Preparar-e-registrar-review-pos-issue-com-veredito-canonico"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Expor contrato de review pos-issue por API

## objetivo

registrar review e veredito canonico no backend

## precondicoes

- `ISSUE-F4-02-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_review_issue_api.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir request response de review e vereditos canonicos
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_issue_api.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_issue_api.py`

## resultado_esperado

Review pos-issue disponivel e persistido.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_issue_api.py`

## stop_conditions

- parar se surgir veredito fora da taxonomia canonica
