---
doc_id: "TASK-3.md"
issue_id: "ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO"
task_id: "T3"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-3 - Entregar UI assistida com checklist de prontidao

## objetivo

Expor no frontend o fluxo inicial de abertura do projeto com leitura do intake e checklist de prontidao.

## precondicoes

- T2 concluida
- contratos de leitura e validacao do intake estaveis na API

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/services/framework.ts`
- `frontend/src/types/framework.ts`
- `frontend/src/pages/dashboard/FrameworkIntakePage.tsx`
- `frontend/src/pages/dashboard/__tests__/FrameworkIntakePage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir abertura assistida do projeto com submit de contexto bruto
  - cobrir exibicao do checklist de prontidao e das lacunas conhecidas
  - cobrir estado bloqueado quando o intake nao puder seguir para PRD
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakePage.test.tsx`
  - `cd frontend && npm run typecheck`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a tela e ao cliente HTTP
3. implementar o minimo necessario na rota servico tipos e pagina do intake
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes e extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakePage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

PM consegue abrir um projeto, inspecionar o intake e entender se o gate `Intake -> PRD` esta pronto ou bloqueado.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/dashboard/__tests__/FrameworkIntakePage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a rota administrativa do frontend conflitar com a navegacao atual do dashboard
- parar se a API ainda nao expuser dados suficientes para checklist e lacunas
