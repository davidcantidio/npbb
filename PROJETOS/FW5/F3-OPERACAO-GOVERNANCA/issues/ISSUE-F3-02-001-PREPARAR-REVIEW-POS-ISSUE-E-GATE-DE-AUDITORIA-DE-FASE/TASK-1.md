---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-02-001-PREPARAR-REVIEW-POS-ISSUE-E-GATE-DE-AUDITORIA-DE-FASE"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar review, auditoria, gate e destinos de follow-up

## objetivo

Fechar a modelagem de review pos-issue, gate de auditoria e destinos de follow-up no dominio.

## precondicoes

- ISSUE-F3-01-002 concluida
- execucoes e evidencias ja podem ser persistidas

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_governance_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir entidades de review, auditoria e follow-up com origem/destino
  - cobrir gate de auditoria da fase e seus estados
  - cobrir serializacao de veredito e motivo
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k gate`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada ao contrato de governanca
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes e serializacao sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k gate`

## resultado_esperado

Dominio de review, auditoria e follow-up fica modelado com gate de fase explicito.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py`

## stop_conditions

- parar se a modelagem contrariar vereditos e destinos definidos em `GOV-AUDITORIA.md`
- parar se follow-up nao puder apontar origem e destino de forma rastreavel
