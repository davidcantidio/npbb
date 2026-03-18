---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-03-002-Materializar-follow-up-de-review-como-issue-local-ou-new-intake"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# TASK-1 - Criar follow-up no destino correto apos a review

## objetivo

materializar issue local ou new intake conforme o veredito da review

## precondicoes

- `ISSUE-F4-03-001` concluida

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/tests/test_framework_review_followup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir criacao de issue local abertura de intake derivado e cancelamento justificado
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_followup.py`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario para fazer apenas os cenarios desta task passarem
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes contratos ou extracoes locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_followup.py`

## resultado_esperado

Remediacao pos-review nasce no artefato certo.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_review_followup.py`

## stop_conditions

- parar se o follow-up estrutural exigir abrir sibling PRD fora do escopo local
