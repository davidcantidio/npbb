---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-002-Implementar-planejamento-assistido-de-sprints-com-enforcement-de-limites"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Gerar sprints com enforcement de limites

## objetivo

permitir selecionar issues por sprint respeitando capacidade e gate humano

## precondicoes

- `ISSUE-F3-02-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkSprintPlanningPage.tsx`
- `backend/tests/test_framework_sprint_limits.py`
- `frontend/src/pages/framework/__tests__/FrameworkSprintPlanning.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir selecao de issues por sprint e bloqueio de excesso de capacidade
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sprint_limits.py`
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkSprintPlanning.test.tsx`
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

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sprint_limits.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkSprintPlanning.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Passos 9 e 10 cobertos com limites canonicos.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sprint_limits.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkSprintPlanning.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o PM pedir override estrutural fora da governanca
