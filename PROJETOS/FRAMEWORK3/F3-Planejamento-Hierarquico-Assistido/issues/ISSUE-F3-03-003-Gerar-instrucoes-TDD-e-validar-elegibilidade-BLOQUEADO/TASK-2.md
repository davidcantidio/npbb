---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-03-003-Gerar-instrucoes-TDD-e-validar-elegibilidade-BLOQUEADO"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Bloquear execucao com task required incompleta

## objetivo

retornar BLOQUEADO quando faltarem `TASK-N.md` ou campos minimos

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_blocked_eligibility.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir retorno `blocked` quando faltarem tasks ou campos minimos obrigatorios
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_blocked_eligibility.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_blocked_eligibility.py`

## resultado_esperado

Execucao so avanca com issue required completa.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_blocked_eligibility.py`

## stop_conditions

- parar se o bloqueio exigir redefinir o contrato de task required
