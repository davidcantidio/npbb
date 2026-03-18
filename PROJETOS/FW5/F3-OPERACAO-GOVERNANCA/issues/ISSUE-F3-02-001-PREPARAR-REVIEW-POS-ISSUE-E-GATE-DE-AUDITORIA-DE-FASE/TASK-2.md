---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F3-02-001-PREPARAR-REVIEW-POS-ISSUE-E-GATE-DE-AUDITORIA-DE-FASE"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Registrar vereditos e roteamento no servico/API

## objetivo

Permitir que backend e API registrem review, gate de auditoria e roteamento de follow-ups.

## precondicoes

- T1 concluida
- execucoes e issues concluidas ja estao acessiveis no dominio

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_governance_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir registro de review com veredito
  - cobrir atualizacao do gate de auditoria da fase
  - cobrir criacao/roteamento de follow-up para `issue-local`, `new-intake` ou `cancelled`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k verdict`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a review e auditoria
3. implementar o minimo necessario em servico e endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar mensagens e eventos sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py -k verdict`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Servico e API passam a registrar vereditos, atualizar gate e rotearem follow-ups com rastreabilidade.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_governance_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se o roteamento de follow-up permitir destino fora da governanca vigente
- parar se o gate da fase puder ser aprovado sem veredito formal
