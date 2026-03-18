---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-02-002-VALIDAR-RASTREABILIDADE-E-GATE-DE-APROVACAO-DO-PRD"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Validar estrutura, criterios por feature e bloqueios do PRD

## objetivo

Garantir que o PRD so seja elegivel para aprovacao quando estiver completo e rastreavel.

## precondicoes

- ISSUE-F1-02-001 concluida
- PRD gerado e acessivel pela API

## arquivos_a_ler_ou_tocar

- `backend/app/services/framework_orchestrator.py`
- `backend/app/api/v1/endpoints/framework.py`
- `backend/tests/test_framework_prd_flow.py`
- `backend/tests/test_framework_domain_contract.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir bloqueio quando faltar feature, criterio ou rastreabilidade com intake
  - cobrir bloqueio quando o PRD tentar seguir com lacuna critica nao explicitada
  - cobrir payload de validacao estrutural e motivo do bloqueio
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k validate`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar o comando red e confirmar falha inicial ligada ao gate do PRD
3. implementar o minimo necessario nas validacoes estruturais do dominio
4. rodar novamente a suite alvo e confirmar green
5. refatorar mensagens e checks locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k validate`

## resultado_esperado

PRD so avanca ao planejamento quando estrutura, criterios e rastreabilidade estiverem coerentes.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py`

## stop_conditions

- parar se a validacao depender de regra nao declarada no PRD do FW5
- parar se o gate do PRD ficar permissivo para lacunas criticas
