---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-01-001-SELECIONAR-A-PROXIMA-UNIDADE-ELEGIVEL-COM-CONTEXTO-COMPLETO"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Entregar painel de proxima acao e bloqueios

## objetivo

Expor no frontend a proxima acao recomendada, o work order resumido e os bloqueios da execucao.

## precondicoes

- T2 concluida
- API ja retorna work order, status e razoes de bloqueio

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkExecutionPage.tsx`
- `frontend/src/components/dashboard/FrameworkNextActionCard.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir exibicao da proxima acao recomendada
  - cobrir exibicao de bloqueios quando a unidade nao for elegivel
  - cobrir leitura resumida do work order
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao painel operacional
3. implementar o minimo necessario em pagina, servico, tipos e card de proxima acao
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue ver a proxima unidade elegivel, o contexto resumido e os bloqueios da execucao.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend precisar inferir elegibilidade sem apoio da API
- parar se o painel misturar selecao da unidade com historico final da F3
