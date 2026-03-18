---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Expor mapa administrativo de fases e epicos

## objetivo

Permitir que o PM navegue pelo mapa inicial do projeto com fases, epicos e dependencias.

## precondicoes

- T2 concluida
- API do planejamento ja retorna fases e epicos derivados

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPlanningPage.tsx`
- `frontend/src/components/dashboard/FrameworkProjectMap.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir leitura do mapa de fases e epicos
  - cobrir exibicao de dependencia e `Feature de Origem`
  - cobrir estado vazio ou bloqueado antes da aprovacao do PRD
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao mapa do projeto
3. implementar o minimo necessario em rota servico tipos pagina e componente de mapa
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue visualizar fases e epicos derivados do PRD em uma superficie administrativa navegavel.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend nao receber dependencia e `Feature de Origem` pela API
- parar se a navegacao administrativa exigir rota nao compativel com o dashboard atual
