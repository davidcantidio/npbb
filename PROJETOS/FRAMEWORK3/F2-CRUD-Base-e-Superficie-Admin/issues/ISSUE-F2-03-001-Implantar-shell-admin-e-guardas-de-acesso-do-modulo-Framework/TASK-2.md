---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-03-001-Implantar-shell-admin-e-guardas-de-acesso-do-modulo-Framework"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Implantar shell e rota protegida do modulo

## objetivo

disponibilizar a entrada protegida do modulo Framework no dashboard

## precondicoes

- T1 concluida
- CRUD base disponivel

## arquivos_a_ler_ou_tocar

- `frontend/src/app/AppRoutes.tsx`
- `frontend/src/pages/framework/FrameworkHomePage.tsx`
- `frontend/src/components/ProtectedRoute.tsx`
- `frontend/src/pages/framework/__tests__/FrameworkRouting.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir rota protegida e renderizacao do shell do modulo
- comando_para_rodar:
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkRouting.test.tsx`
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

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkRouting.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Entrada protegida do modulo disponivel no dashboard.

## testes_ou_validacoes_obrigatorias

- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkRouting.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se a integracao exigir reorganizar o roteamento global fora do escopo
