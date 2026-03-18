---
doc_id: "TASK-2.md"
issue_id: "ISSUE-F2-01-002-DERIVAR-ISSUES-E-TASKS-COM-FEATURE-DE-ORIGEM-EXPLICITA"
task_id: "T2"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-2 - Derivar issues e tasks com Feature de Origem e elegibilidade

## objetivo

Fazer o backend derivar backlog detalhado com dependencias e sinalizacao basica da proxima unidade elegivel.

## precondicoes

- T1 concluida
- lista de fases e epicos ja esta disponivel

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_planning_flow.py`
- `backend/tests/test_framework_startup.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir geracao de issues e tasks a partir de epicos derivados
  - cobrir `Feature de Origem`, dependencias e metadados de elegibilidade
  - cobrir bloqueio quando o PRD ou a F2 ainda nao estiverem prontos
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k eligibility`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada a derivacao detalhada
3. implementar o minimo necessario em servico e endpoints
4. rodar novamente as suites alvo e confirmar green
5. refatorar regras locais de ordenacao sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py -k eligibility`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py -k framework`

## resultado_esperado

Backlog de issues e tasks derivado do PRD e pronto para suportar a F3.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_planning_flow.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_startup.py`

## stop_conditions

- parar se a elegibilidade depender de politica de autonomia ainda nao modelada na F3
- parar se a derivacao gerar item acima dos limites canonicos sem sinalizacao
