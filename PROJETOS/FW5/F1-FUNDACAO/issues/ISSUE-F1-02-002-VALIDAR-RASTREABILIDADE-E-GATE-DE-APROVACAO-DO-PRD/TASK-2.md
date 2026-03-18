---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-02-002-VALIDAR-RASTREABILIDADE-E-GATE-DE-APROVACAO-DO-PRD"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Fechar gate de aprovacao do PRD com status e historico visiveis

## objetivo

Expor aprovacao, ajuste e historico do PRD de forma clara para o PM no backend e no frontend.

## precondicoes

- T1 concluida
- API de validacao estrutural do PRD estavel

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPrdReviewPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPrdReviewPage.test.tsx`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_prd_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir aprovacao do PRD e exibicao da proxima acao para planejamento
  - cobrir visualizacao de historico e diff do PRD
  - cobrir estado bloqueado quando a validacao estrutural falhar
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k approval`
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdReviewPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao gate e a tela de revisao
3. implementar o minimo necessario em endpoint, servico, pagina e tipos
4. rodar novamente as suites alvo e confirmar green
5. refatorar mensagens e componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k approval`
- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdReviewPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue aprovar o PRD e ver historico, bloqueios e proxima acao para o planejamento executavel.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py`
- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdReviewPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend precisar calcular historico do PRD sem apoio do backend
- parar se o gate apontar proxima acao antes da aprovacao formal
