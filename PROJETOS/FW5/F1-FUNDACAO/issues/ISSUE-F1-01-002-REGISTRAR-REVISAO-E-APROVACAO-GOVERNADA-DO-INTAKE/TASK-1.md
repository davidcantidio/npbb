---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-002-REGISTRAR-REVISAO-E-APROVACAO-GOVERNADA-DO-INTAKE"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Persistir trilha de revisao, diff e gate Intake -> PRD

## objetivo

Persistir revisoes do intake com diff, aprovador, timestamps e proximo passo visivel no dominio.

## precondicoes

- ISSUE-F1-01-001 concluida
- modelos de intake e checklist estaveis

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_intake_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir nova revisao com diff e versao incremental
  - cobrir aprovacao do intake com registro de aprovador e timestamp
  - cobrir atualizacao do status/proxima acao do projeto apos aprovacao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k approval`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada ao historico e ao gate
3. implementar o minimo necessario no dominio e na API para revisao/aprovacao
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes de eventos e payloads sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k approval`

## resultado_esperado

Historico do intake passa a registrar diff, aprovador e transicao para derivacao do PRD.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py`

## stop_conditions

- parar se a regra de aprovacao exigir estado nao previsto no PRD do FW5
- parar se o diff depender de formato nao acordado entre persistencia e markdown
