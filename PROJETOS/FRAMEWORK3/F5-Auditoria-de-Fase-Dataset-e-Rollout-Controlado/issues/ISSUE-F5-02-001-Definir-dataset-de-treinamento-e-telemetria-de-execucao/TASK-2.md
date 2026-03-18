---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F5-02-001-Definir-dataset-de-treinamento-e-telemetria-de-execucao"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Instrumentar persistencia e extracao do dataset

## objetivo

persistir e exportar a visao treinavel aprovada para o FRAMEWORK3

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_training_dataset.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir persistencia e export da visao treinavel aprovada
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_training_dataset.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_training_dataset.py`

## resultado_esperado

Dataset treinavel extraivel do modulo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_training_dataset.py`

## stop_conditions

- parar se o contrato aprovado exigir storage ou infraestrutura externa
