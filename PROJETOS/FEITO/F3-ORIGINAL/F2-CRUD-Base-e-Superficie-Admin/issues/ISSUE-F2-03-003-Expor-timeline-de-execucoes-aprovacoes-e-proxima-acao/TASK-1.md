---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-03-003-Expor-timeline-de-execucoes-aprovacoes-e-proxima-acao"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Expor timeline operacional do projeto

## objetivo

listar execucoes aprovacoes e proxima acao do projeto Framework

## precondicoes

- `ISSUE-F1-02-002` concluida

## arquivos_a_ler_ou_tocar

- `frontend/src/pages/framework/FrameworkTimelinePage.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/pages/framework/__tests__/FrameworkTimeline.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir listagem da timeline e painel de proxima acao
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkTimeline.test.tsx`
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

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkTimeline.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Historico operacional visivel ao PM.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkTimeline.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o backend nao expuser dados minimos de ordenacao temporal
