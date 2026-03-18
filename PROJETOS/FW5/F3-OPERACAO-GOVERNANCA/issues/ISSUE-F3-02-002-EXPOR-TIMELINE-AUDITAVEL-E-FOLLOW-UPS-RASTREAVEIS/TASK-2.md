---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-02-002-EXPOR-TIMELINE-AUDITAVEL-E-FOLLOW-UPS-RASTREAVEIS"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Consolidar leitura auditavel de aprovacoes, prompts, outputs e diffs

## objetivo

Fazer o backend consolidar uma leitura auditavel do historico do projeto com eventos, aprovacoes, outputs e diffs.

## precondicoes

- T1 concluida
- review, auditoria e execucao ja registram eventos no dominio

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_governance_flow.py`
- `backend/tests/test_framework_timeline.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir consulta consolidada de eventos, aprovacoes e outputs
  - cobrir exposicao de diffs e evidencias relevantes na timeline
  - cobrir leitura de follow-ups com origem e destino
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k history`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py -k history`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a consulta auditavel
3. implementar o minimo necessario em servico e endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar agregacoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k history`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py -k history`

## resultado_esperado

API de historico passa a consolidar aprovacoes, prompts, outputs, diffs e follow-ups do projeto.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py`

## stop_conditions

- parar se a leitura consolidada omitir origem ou referencia de follow-up
- parar se a API exigir que o frontend recomponha eventos por conta propria
