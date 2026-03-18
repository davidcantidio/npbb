---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-001-Implementar-planejamento-assistido-de-fases-e-epicos"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Gerar fases e epicos a partir do PRD aprovado

## objetivo

persistir o planejamento alto nivel a partir do PRD aprovado

## precondicoes

- `ISSUE-F3-01-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_phase_epic_planning.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao de fases e epicos e vinculo hierarquico
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_phase_epic_planning.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_phase_epic_planning.py`

## resultado_esperado

Fases e epicos gerados no modulo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_phase_epic_planning.py`

## stop_conditions

- parar se o PRD aprovado nao trouxer escopo suficiente para fatiamento
