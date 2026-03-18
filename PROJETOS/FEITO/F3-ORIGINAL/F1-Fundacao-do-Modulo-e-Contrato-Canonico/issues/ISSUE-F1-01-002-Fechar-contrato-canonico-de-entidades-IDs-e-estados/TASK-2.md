---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-002-Fechar-contrato-canonico-de-entidades-IDs-e-estados"
task_id: "T2"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Materializar contrato aprovado em models schemas e migration

## objetivo

alinhar models schemas e migration ao contrato canonico aprovado

## precondicoes

- T1 concluida e contrato aprovado

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_domain_contract.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir enums constraints e campos canonicos do dominio `framework`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`

## resultado_esperado

Dominio persistido alinhado ao contrato aprovado.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -c "import app.models.framework_models"`

## stop_conditions

- parar se a migration existente tiver drift estrutural que exija intake de remediacao proprio
