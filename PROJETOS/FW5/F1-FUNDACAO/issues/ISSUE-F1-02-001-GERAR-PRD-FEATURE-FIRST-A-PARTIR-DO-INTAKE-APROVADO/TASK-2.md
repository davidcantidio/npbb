---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-02-001-GERAR-PRD-FEATURE-FIRST-A-PARTIR-DO-INTAKE-APROVADO"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Implementar derivacao do PRD feature-first a partir do intake aprovado

## objetivo

Fazer o servico do dominio derivar o PRD a partir do intake aprovado preservando origem, restricoes e riscos.

## precondicoes

- T1 concluida
- gate de aprovacao do intake funcionando

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_prd_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao do PRD somente para intake aprovado
  - cobrir preservacao de frontmatter, restricoes e riscos do intake
  - cobrir populacao das features e impactos por camada
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k generate`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a derivacao do PRD
3. implementar o minimo necessario no servico e nos endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar transformacoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k generate`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Servico e API passam a gerar o PRD `feature-first` a partir do intake aprovado.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se a derivacao exigir inventar feature onde o intake marca lacuna critica
- parar se o fluxo permitir gerar PRD a partir de intake nao aprovado
