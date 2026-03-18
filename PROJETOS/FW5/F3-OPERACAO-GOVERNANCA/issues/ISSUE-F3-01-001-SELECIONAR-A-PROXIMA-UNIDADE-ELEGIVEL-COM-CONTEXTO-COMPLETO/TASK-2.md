---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Implementar selecao da proxima unidade elegivel

## objetivo

Fazer o backend selecionar a proxima unidade elegivel e devolver work order e bloqueios.

## precondicoes

- T1 concluida
- hierarquia de issues/tasks derivada na F2

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_execution_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir selecao da primeira unidade elegivel respeitando dependencias
  - cobrir resposta bloqueada quando houver gate pendente ou task inelegivel
  - cobrir determinacao da proxima acao do projeto
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k eligible`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a selecao da unidade elegivel
3. implementar o minimo necessario em servico e endpoint
4. rodar novamente as suites alvo e confirmar green
5. refatorar ordenacao e mensagens sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k eligible`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Servico e API retornam a proxima unidade elegivel, work order e razoes de bloqueio quando houver.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se a selecao exigir executar task antes de dependencia concluida
- parar se a API nao conseguir distinguir estado bloqueado de estado elegivel
