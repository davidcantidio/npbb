---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-002-EXPOR-TIMELINE-AUDITAVEL-E-FOLLOW-UPS-RASTREAVEIS"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar timeline, eventos e filtros

## objetivo

Modelar a timeline operacional do projeto, seus eventos e filtros basicos de consulta.

## precondicoes

- ISSUE-F3-02-001 concluida
- execucoes, reviews e auditorias ja podem ser persistidas

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_timeline.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir entidade de evento de timeline com tipo, origem e referencia
  - cobrir filtros por fase, epico, issue e task
  - cobrir serializacao ordenada dos eventos
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py -k timeline`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada ao contrato de timeline
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes de eventos e filtros sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py -k timeline`

## resultado_esperado

Dominio de timeline pronto para registrar e filtrar eventos auditaveis do projeto.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_timeline.py`

## stop_conditions

- parar se a timeline nao conseguir apontar origem e referencia de cada evento
- parar se filtros exigirem regra nao declarada no PRD do FW5
