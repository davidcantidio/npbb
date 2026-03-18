---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F1-02-001-GERAR-PRD-FEATURE-FIRST-A-PARTIR-DO-INTAKE-APROVADO"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Entregar UI de geracao e revisao do PRD

## objetivo

Expor no dashboard a geracao do PRD e a leitura das features derivadas do intake aprovado.

## precondicoes

- T2 concluida
- API de PRD ja retorna estrutura do documento e das features

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkPrdPage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkPrdPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao do PRD a partir de intake aprovado
  - cobrir leitura das features e de seus criterios de aceite
  - cobrir estado bloqueado quando o intake ainda nao estiver aprovado
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdPage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a tela e ao cliente HTTP
3. implementar o minimo necessario na rota servico tipos e pagina do PRD
4. rodar novamente as suites alvo e confirmar green
5. refatorar componentes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue gerar e revisar o PRD `feature-first` no modulo administrativo.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkPrdPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a pagina precisar inferir estrutura de feature nao exposta pela API
- parar se a geracao do PRD ainda nao estiver bloqueada pelo estado do intake
