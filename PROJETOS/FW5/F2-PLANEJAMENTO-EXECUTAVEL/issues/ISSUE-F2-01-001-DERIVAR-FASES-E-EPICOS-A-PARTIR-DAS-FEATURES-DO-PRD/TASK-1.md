---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar fases, epicos, IDs e dependencias

## objetivo

Fechar entidades e schemas para fases e epicos com IDs canonicos, dependencia e `Feature de Origem`.

## precondicoes

- F1 aprovada
- PRD aprovado e acessivel ao dominio

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_planning_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir entidades de fase/epico com IDs canonicos e dependencia
  - cobrir ligacao de fase/epico com feature de origem
  - cobrir payload de leitura do mapa inicial do projeto
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k phase`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k phase`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato de fase/epico
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes e serializacao sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k phase`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k phase`

## resultado_esperado

Modelagem de fase e epico pronta para derivacao rastreavel do planejamento.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k phase`

## stop_conditions

- parar se a modelagem exigir inventar dependencias nao declaradas no PRD
- parar se os IDs canonicos nao puderem ser derivados de forma estavel
