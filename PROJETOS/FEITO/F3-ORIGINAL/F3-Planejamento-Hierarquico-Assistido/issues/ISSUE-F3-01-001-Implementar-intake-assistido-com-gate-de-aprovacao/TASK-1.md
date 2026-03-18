---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-001-Implementar-intake-assistido-com-gate-de-aprovacao"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Implementar fluxo de intake assistido

## objetivo

cobrir criacao edicao e aprovacao do intake no modulo

## precondicoes

- F2 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkIntakePage.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkIntakeFlow.test.tsx`
- `backend/tests/test_framework_intake_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir criacao edicao e aprovacao do intake em backend e frontend
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py`
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkIntakeFlow.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkIntakeFlow.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Passos 1 e 2 do algoritmo cobertos no modulo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkIntakeFlow.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o contrato de aprovacao divergir do decidido em F1
