---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-02-003-Expor-CRUD-de-issue-task-e-transicoes-de-aprovacao"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Expor transicoes de aprovacao e status por API

## objetivo

permitir aprovar intake PRD issue e task com bloqueio de transicoes invalidas

## precondicoes

- T1 concluida
- `ISSUE-F1-03-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_approval_api.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir aprovacao manual automatica e bloqueio de transicoes invalidas
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_approval_api.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_approval_api.py`

## resultado_esperado

Aprovacoes e estados operacionais disponiveis por API.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_approval_api.py`

## stop_conditions

- parar se surgir novo veredito fora do contrato de F1
