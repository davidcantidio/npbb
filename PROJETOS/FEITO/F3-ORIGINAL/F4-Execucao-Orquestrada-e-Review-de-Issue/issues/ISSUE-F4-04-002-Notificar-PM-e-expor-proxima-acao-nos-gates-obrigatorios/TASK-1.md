---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-04-002-Notificar-PM-e-expor-proxima-acao-nos-gates-obrigatorios"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Expor proxima acao e notificacoes de gate

## objetivo

mostrar ao PM a proxima acao obrigatoria e os eventos relevantes de gate

## precondicoes

- `ISSUE-F4-04-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `frontend/src/pages/framework/FrameworkTimelinePage.tsx`
- `backend/tests/test_framework_next_action_notifications.py`
- `frontend/src/pages/framework/__tests__/FrameworkNextAction.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir proxima acao e notificacoes de gate em backend e frontend
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_action_notifications.py`
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkNextAction.test.tsx`
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

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_action_notifications.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkNextAction.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM visualiza claramente o proximo gate ou acao do sistema.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_next_action_notifications.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkNextAction.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o mecanismo de notificacao exigir infraestrutura externa nao prevista no PRD
