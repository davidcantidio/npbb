---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F4-04-001-Sincronizar-cascata-documental-e-persistida-apos-execucao"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Validar derivacao de status e reabertura por follow-up

## objetivo

reabrir corretamente a cascata quando surgir follow-up local

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_status_derivation.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir retorno para `active` e reversao de `audit_gate` quando issue nova local surgir
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_derivation.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_derivation.py`

## resultado_esperado

Estados derivados ficam consistentes mesmo apos follow-up.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_derivation.py`

## stop_conditions

- parar se a fase ja estiver `approved`, caso em que o follow-up local deve ser bloqueado
