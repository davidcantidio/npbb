---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-02-002-Expor-consulta-e-export-auditavel-do-historico-do-Framework"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Expor consulta e export do historico

## objetivo

permitir filtrar consultar e exportar o historico do FRAMEWORK3

## precondicoes

- `ISSUE-F5-02-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/api/v1/endpoints/framework.py`
- `frontend/src/pages/framework/FrameworkExportPage.tsx`
- `backend/tests/test_framework_history_export_api.py`
- `frontend/src/pages/framework/__tests__/FrameworkExportPage.test.tsx`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir filtros export e rastreabilidade do historico
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_history_export_api.py`
  - `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkExportPage.test.tsx`
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

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_history_export_api.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkExportPage.test.tsx`
- `cd frontend && npm run typecheck`

## resultado_esperado

Historico consultavel e exportavel.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_history_export_api.py`
- `cd frontend && npm run test -- --run src/pages/framework/__tests__/FrameworkExportPage.test.tsx`
- `cd frontend && npm run typecheck`

## stop_conditions

- parar se o contrato de export exigir paginacao ou streaming nao previstos
