---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F5-01-001-Preparar-e-registrar-auditoria-de-fase-com-gate-persistido"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Preparar contrato de auditoria de fase

## objetivo

alinhar work order relatorio `AUDIT-LOG` e gate persistido ao dominio

## precondicoes

- F4 concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_audit_contract.py`
- `PROJETOS/FRAMEWORK3/AUDIT-LOG.md`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir criacao do work order de auditoria atualizacao de gate e referencia a relatorio ou log
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_audit_contract.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_audit_contract.py`

## resultado_esperado

Auditoria de fase preparada no modulo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_audit_contract.py`

## stop_conditions

- parar se o projeto continuar sem `AUDIT-LOG.md` bootstrapavel pelo protocolo de F1
