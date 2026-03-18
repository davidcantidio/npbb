---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-02-001-Formalizar-sincronizacao-precedencia-e-bootstrap-Markdown-banco"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-2 - Aplicar contrato de sincronizacao e bootstrapping no backend

## objetivo

materializar no dominio o bootstrap minimo e o estado de sincronizacao aprovado

## precondicoes

- T1 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_sync_contract.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir bootstrap de projeto paths minimos e estado de sincronizacao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sync_contract.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sync_contract.py`

## resultado_esperado

Projeto framework consegue nascer com paths minimos e fonte de verdade declarada.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_sync_contract.py`

## stop_conditions

- parar se o bootstrap exigir side effects fora do dominio framework
