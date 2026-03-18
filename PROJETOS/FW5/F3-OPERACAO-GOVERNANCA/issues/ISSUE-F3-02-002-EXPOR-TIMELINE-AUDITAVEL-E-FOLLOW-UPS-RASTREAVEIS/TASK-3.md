---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-02-002-EXPOR-TIMELINE-AUDITAVEL-E-FOLLOW-UPS-RASTREAVEIS"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Expor timeline e drilldown de follow-ups ao PM

## objetivo

Entregar no frontend uma timeline auditavel com filtros e drilldown dos follow-ups do projeto.

## precondicoes

- T2 concluida
- API de historico consolidado ja retorna eventos e follow-ups

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkTimelinePage.tsx`
- `frontend/src/components/dashboard/FrameworkTimeline.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkTimelinePage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir listagem da timeline com filtros por fase, issue e follow-up
  - cobrir drilldown de follow-up com origem, destino e evidencias
  - cobrir exibicao de prompts, outputs e diffs relevantes
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkTimelinePage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a timeline e ao drilldown
3. implementar o minimo necessario em pagina, servico, tipos e componente de timeline
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkTimelinePage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue consultar a timeline do projeto e abrir follow-ups, aprovacoes e evidencias no mesmo fluxo.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkTimelinePage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend nao receber filtros e referencias suficientes para o drilldown
- parar se a timeline misturar contexto operacional com navegacao de planejamento da F2
