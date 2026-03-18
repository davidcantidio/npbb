---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-04-001-Sincronizar-cascata-documental-e-persistida-apos-execucao"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Sincronizar cascata de status apos execucao e review

## objetivo

atualizar pais e gates derivados apos execucao e review de issue

## precondicoes

- `ISSUE-F4-03-002` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_status_cascade.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir atualizacao de pais e gatilho de `audit_gate: pending` apenas quando devido
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_cascade.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_cascade.py`

## resultado_esperado

Fechamento documental e persistido seguem a governanca.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_status_cascade.py`

## stop_conditions

- parar se houver comportamento divergente entre legados e issue-first nao previsto
