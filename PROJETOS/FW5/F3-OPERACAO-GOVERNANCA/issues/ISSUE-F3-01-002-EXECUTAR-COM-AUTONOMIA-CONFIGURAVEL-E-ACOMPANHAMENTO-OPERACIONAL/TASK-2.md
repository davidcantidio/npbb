---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Integrar disparo e registro de execucao com evidencias

## objetivo

Executar work orders conforme a politica de autonomia e registrar evidencias, outputs e bloqueios.

## precondicoes

- T1 concluida
- work order elegivel ja pode ser selecionado

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_execution_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir disparo de execucao para unidade elegivel
  - cobrir persistencia de output, evidencia e motivo de bloqueio
  - cobrir override e reentrada no fluxo apos escalada
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k execution`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao disparo operacional
3. implementar o minimo necessario em servico e endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar eventos operacionais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k execution`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Execucao do work order passa a registrar outputs, evidencias e bloqueios com rastreabilidade.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se a execucao puder avancar sem work order valido
- parar se o registro de evidencia nao diferenciar sucesso, bloqueio e override
