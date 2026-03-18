---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-02-001-Expor-CRUD-de-projeto-intake-e-PRD"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Expor endpoints de projeto intake e PRD

## objetivo

entregar CRUD do topo da hierarquia no backend

## precondicoes

- `ISSUE-F2-01-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_project_intake_prd_api.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir criacao listagem e atualizacao de `project/intake/prd`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_project_intake_prd_api.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_project_intake_prd_api.py`

## resultado_esperado

CRUD do topo da hierarquia disponivel.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_project_intake_prd_api.py`

## stop_conditions

- parar se o servico ainda depender de placeholders incompativeis com o contrato de F1
