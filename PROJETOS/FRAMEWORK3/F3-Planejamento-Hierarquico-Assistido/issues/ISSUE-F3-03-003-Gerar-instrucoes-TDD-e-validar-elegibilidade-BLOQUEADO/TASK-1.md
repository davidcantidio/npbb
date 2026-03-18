---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-03-003-Gerar-instrucoes-TDD-e-validar-elegibilidade-BLOQUEADO"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Gerar instrucoes TDD para tasks automatizaveis

## objetivo

criar `testes_red` e ordem TDD para tasks com cobertura automatizavel

## precondicoes

- `ISSUE-F3-03-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_tdd_instructions.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir presenca de `testes_red`, ordem TDD e comandos permitidos quando `tdd_aplicavel: true`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_tdd_instructions.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_tdd_instructions.py`

## resultado_esperado

Passo 15 coberto no backend.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_tdd_instructions.py`

## stop_conditions

- parar se a task nao envolver cobertura automatizavel
