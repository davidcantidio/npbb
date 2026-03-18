---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-02-002-Formalizar-rastreabilidade-de-aprovacoes-e-artefatos"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Persistir trilha de prompts aprovacoes e evidencias

## objetivo

registrar historico minimo treinavel e auditavel no dominio FRAMEWORK3

## precondicoes

- `ISSUE-F1-02-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_traceability.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir gravação de `AgentExecution`, `human_approval`, `evidence_ref` e vinculo com `project/phase/issue/task`
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_traceability.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_traceability.py`

## resultado_esperado

Rastreabilidade minima treinavel e auditavel persistida no dominio.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_traceability.py`

## stop_conditions

- parar se surgirem exigencias de retencao ou compliance fora do escopo do PRD
