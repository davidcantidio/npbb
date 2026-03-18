---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-01-002-Orquestrar-follow-ups-de-hold-e-retomada-da-fase"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Orquestrar remediacao de hold e retomada da fase

## objetivo

manter o gate em hold ate a resolucao dos follow-ups obrigatorios

## precondicoes

- `ISSUE-F5-01-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_hold_remediation.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao de follow-ups bloqueantes manutencao do gate em `hold` e retomada apenas apos resolucao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_hold_remediation.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_hold_remediation.py`

## resultado_esperado

Hold e remediacao seguem a governanca.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_hold_remediation.py`

## stop_conditions

- parar se um follow-up estrutural exigir abrir novo PRD sibling fora do modulo atual
