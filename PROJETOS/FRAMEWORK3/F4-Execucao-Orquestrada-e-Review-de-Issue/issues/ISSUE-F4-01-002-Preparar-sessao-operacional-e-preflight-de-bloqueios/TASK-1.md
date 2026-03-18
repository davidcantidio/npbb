---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-01-002-Preparar-sessao-operacional-e-preflight-de-bloqueios"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Preparar sessao operacional e barrar preflights invalidos

## objetivo

validar preflight da task e montar o contexto executavel correto

## precondicoes

- `ISSUE-F4-01-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_execution_preflight.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir falta de commit task incompleta artefato ausente e bloqueio de execucao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_preflight.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_preflight.py`

## resultado_esperado

So tasks elegiveis produzem sessao operacional.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_preflight.py`

## stop_conditions

- parar se um bloqueio depender de dado ainda nao persistido pelo modulo
