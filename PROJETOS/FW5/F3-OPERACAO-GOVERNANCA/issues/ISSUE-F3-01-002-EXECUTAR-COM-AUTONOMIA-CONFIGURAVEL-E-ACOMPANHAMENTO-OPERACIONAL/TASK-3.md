---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Entregar acompanhamento operacional com override do PM

## objetivo

Expor no frontend o acompanhamento operacional da execucao com override do PM e leitura das evidencias.

## precondicoes

- T2 concluida
- API de execucao ja retorna estado, evidencias e override

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkExecutionPage.tsx`
- `frontend/src/components/dashboard/FrameworkExecutionPanel.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir acompanhamento do estado da execucao
  - cobrir acao de override humano e exibicao do motivo
  - cobrir leitura de outputs e evidencias operacionais
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao acompanhamento operacional
3. implementar o minimo necessario em pagina, servico, tipos e painel operacional
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM acompanha a execucao, aplica override quando necessario e inspeciona evidencias e outputs.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkExecutionPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o frontend nao receber estado suficiente para distinguir bloqueio, execucao e concluido
- parar se o override humano puder ser disparado sem registro de motivo
