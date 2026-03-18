---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-002-REGISTRAR-REVISAO-E-APROVACAO-GOVERNADA-DO-INTAKE"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Entregar fluxo UI de revisao e aprovacao com historico

## objetivo

Permitir que o PM revise o intake, visualize diff e registre aprovacao ou ajuste no frontend administrativo.

## precondicoes

- T1 concluida
- API expõe historico e estado de aprovacao do intake

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkIntakeReviewPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkIntakeReviewPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir visualizacao do diff entre versoes do intake
  - cobrir aprovacao explicita e retorno para ajuste
  - cobrir exibicao da proxima acao apos aprovacao
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakeReviewPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a tela de revisao
3. implementar o minimo necessario em rota, tipos, servico e pagina de revisao
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakeReviewPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue revisar o intake com diff, aprovar ou pedir ajuste e ver o proximo passo do fluxo.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakeReviewPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend precisar inferir diff que nao venha do backend ou de regra explicitada
- parar se a navegacao do dashboard nao comportar a nova rota administrativa
