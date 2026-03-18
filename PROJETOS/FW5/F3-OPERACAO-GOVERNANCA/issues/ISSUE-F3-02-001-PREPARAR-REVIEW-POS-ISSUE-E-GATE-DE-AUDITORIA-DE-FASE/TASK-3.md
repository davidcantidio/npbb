---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F3-02-001-PREPARAR-REVIEW-POS-ISSUE-E-GATE-DE-AUDITORIA-DE-FASE"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Entregar fluxo UI de review e auditoria

## objetivo

Expor ao PM a tela de review pos-issue e o fluxo de gate de auditoria da fase.

## precondicoes

- T2 concluida
- API ja retorna veredito, gate e follow-ups

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkGovernancePage.tsx`
- `frontend/src/components/dashboard/FrameworkReviewPanel.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkGovernancePage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir review pos-issue com veredito
  - cobrir atualizacao do gate de auditoria da fase
  - cobrir leitura e roteamento dos follow-ups sugeridos
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkGovernancePage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a review e auditoria
3. implementar o minimo necessario em pagina, servico, tipos e painel de review
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkGovernancePage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue registrar review, inspecionar gate de auditoria e entender follow-ups gerados.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkGovernancePage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a tela precisar inferir follow-up sem dados suficientes do backend
- parar se review pos-issue e auditoria formal se misturarem no mesmo estado sem distincao
