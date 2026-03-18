---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Expor navegacao e leitura detalhada da hierarquia

## objetivo

Permitir que o PM abra epicos, issues e tasks derivadas e entenda dependencias e rastreabilidade.

## precondicoes

- T2 concluida
- API do planejamento detalhado ja retorna issues e tasks

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPlanningPage.tsx`
- `frontend/src/components/dashboard/FrameworkHierarchyTree.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir leitura detalhada de epico, issue e task derivadas
  - cobrir exibicao de dependencia, `Feature de Origem` e metadados de sprint
  - cobrir estado vazio antes da derivacao completa da hierarquia
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a arvore da hierarquia
3. implementar o minimo necessario em servico tipos pagina e componente de leitura detalhada
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue navegar pela hierarquia detalhada e inspecionar o backlog executavel do projeto.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPlanningPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a leitura detalhada depender de estrutura que a API ainda nao retorne
- parar se a pagina misturar navegacao de planejamento com execucao operacional da F3
