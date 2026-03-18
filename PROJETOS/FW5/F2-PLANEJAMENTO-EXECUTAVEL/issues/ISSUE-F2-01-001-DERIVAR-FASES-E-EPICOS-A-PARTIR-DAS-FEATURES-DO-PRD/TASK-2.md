---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-01-001-DERIVAR-FASES-E-EPICOS-A-PARTIR-DAS-FEATURES-DO-PRD"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Derivar fases e epicos a partir das features

## objetivo

Implementar no dominio a derivacao de fases e epicos a partir do PRD aprovado.

## precondicoes

- T1 concluida
- lista de features do PRD disponivel para leitura

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_planning_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir criacao de fases e epicos a partir das features aprovadas
  - cobrir preservacao da dependencia entre fases e epicos
  - cobrir bloqueio quando o PRD ainda nao estiver aprovado
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k epic`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a derivacao do planejamento
3. implementar o minimo necessario em servico e endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar transformacoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k epic`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Servico e API passam a derivar fases e epicos a partir do PRD aprovado.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se o planejamento reintroduzir agrupamento por camada tecnica
- parar se a API permitir iniciar F2 sem PRD aprovado
