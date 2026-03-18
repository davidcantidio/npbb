---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F3-01-002-EXECUTAR-COM-AUTONOMIA-CONFIGURAVEL-E-ACOMPANHAMENTO-OPERACIONAL"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Definir politicas de autonomia, escalada e estados de execucao

## objetivo

Modelar os modos de autonomia, escalada e estados de execucao que regerao o work order.

## precondicoes

- ISSUE-F3-01-001 concluida
- contrato basico de work order ja existe

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_execution_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir modos de autonomia por projeto
  - cobrir estados de execucao e transicoes de escalada
  - cobrir serializacao de override humano e motivo operacional
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k autonomy`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada a autonomia e escalada
3. implementar o minimo necessario em modelos e schemas
4. rodar novamente a suite alvo e confirmar green
5. refatorar estados e nomes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py -k autonomy`

## resultado_esperado

Politicas de autonomia e estados de execucao ficam explicitamente modelados no dominio.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_execution_flow.py`

## stop_conditions

- parar se a modelagem exigir inventar modo de autonomia nao sustentado pelo PRD
- parar se o override humano nao tiver rastreabilidade suficiente
