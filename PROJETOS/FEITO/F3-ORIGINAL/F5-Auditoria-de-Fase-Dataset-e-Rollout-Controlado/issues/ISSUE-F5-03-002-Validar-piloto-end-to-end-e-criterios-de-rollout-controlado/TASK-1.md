---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-03-002-Validar-piloto-end-to-end-e-criterios-de-rollout-controlado"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Validar piloto end-to-end e criterios de rollout

## objetivo

executar smokes do fluxo completo do piloto e consolidar os criterios de rollout controlado

## precondicoes

- `ISSUE-F5-03-001` concluida
- modulo funcional ate auditoria

## arquivos_a_ler_ou_tocar

- `backend/tests/test_framework_e2e_pilot.py`
- `frontend/src/pages/framework/__tests__/FrameworkPilotFlow.test.tsx`
- `PROJETOS/FRAMEWORK3/PRD-FRAMEWORK3.md`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o fluxo completo do piloto e a presenca das evidencias minimas exigidas
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_e2e_pilot.py`
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkPilotFlow.test.tsx`
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

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_e2e_pilot.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkPilotFlow.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Piloto completo validado e criterios de rollout fechados.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_e2e_pilot.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkPilotFlow.test.tsx`
- `cd frontend && npm run typecheck`
- `checagem manual do fluxo completo do piloto`

## stop_conditions

- parar se o piloto revelar lacuna estrutural que exija novo intake
