---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-03-001-Definir-maquina-de-estados-e-gates-HITL-do-orquestrador"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Aplicar maquina de estados e gates HITL no dominio

## objetivo

formalizar e validar as transicoes de estado do FRAMEWORK3

## precondicoes

- `ISSUE-F1-01-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_state_transitions.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir transicoes validas e invalidas de `ProjectStatus`, `ApprovalStatus` e `AuditGateState`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_state_transitions.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_state_transitions.py`

## resultado_esperado

Estados e gates operacionais sem ambiguidade.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_state_transitions.py`

## stop_conditions

- parar se surgir novo status nao previsto pela governanca canonica
