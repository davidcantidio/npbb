---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-001-Consolidar-persistencia-de-projeto-a-sprint"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Consolidar models do topo e meio da hierarquia

## objetivo

alinhar models e migration de `project` ate `sprint` ao contrato aprovado

## precondicoes

- F1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/alembic/versions/c0d63429d56d_add_lead_evento_table_for_issue_f1_01_.py`
- `backend/tests/test_framework_topology_models.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir constraints FKs e campos obrigatorios de `project/intake/prd/phase/epic/sprint`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_topology_models.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_topology_models.py`

## resultado_esperado

Persistencia estavel ate `sprint`.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_topology_models.py`

## stop_conditions

- parar se houver conflito entre a migration existente e o contrato aprovado
