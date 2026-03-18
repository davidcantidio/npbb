---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-04-001-Persistir-prompts-outputs-aprovacoes-e-evidencias-do-planejamento"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Persistir historico do planejamento por etapa

## objetivo

registrar prompts outputs aprovacoes e evidencias do planejamento no backend

## precondicoes

- `ISSUE-F1-02-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/models/framework_models.py`
- `backend/tests/test_framework_planning_history.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir gravacao completa do historico por etapa do planejamento
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_history.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_history.py`

## resultado_esperado

Planejamento inteiro deixa trilha persistida.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_history.py`

## stop_conditions

- parar se o payload treinavel extrapolar o contrato aprovado em F1
