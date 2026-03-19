---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO"
task_id: "T2"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# TASK-2 - Implementar fluxo assistido de geracao e validacao do intake

## objetivo

Fazer o backend gerar intake estruturado, validar completude e sinalizar bloqueios de prontidao.

## precondicoes

- T1 concluida
- contrato minimo de modelos e schemas do intake aprovado

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_intake_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao do intake a partir de contexto bruto
  - cobrir bloqueio quando houver lacuna critica real
  - cobrir payload de resposta para leitura do intake estruturado
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k intake`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao fluxo esperado
3. implementar o minimo necessario no servico e nos endpoints do dominio
4. rodar novamente as suites alvo e confirmar green
5. refatorar contratos locais do orquestrador sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k intake`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Servico e API do intake geram estrutura valida e bloqueiam o gate `Intake -> PRD` quando necessario.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se o endpoint exigir contrato que contradiga o PRD do FW5
- parar se o servico nao conseguir distinguir fato inferencia e hipotese sem regra explicita
