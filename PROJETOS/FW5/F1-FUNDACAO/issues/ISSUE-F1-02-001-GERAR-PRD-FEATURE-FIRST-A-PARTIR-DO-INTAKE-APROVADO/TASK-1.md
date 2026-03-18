---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-02-001-GERAR-PRD-FEATURE-FIRST-A-PARTIR-DO-INTAKE-APROVADO"
task_id: "T1"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-18"
tdd_aplicavel: true
---

# TASK-1 - Modelar PRD, features e rastreabilidade com o intake

## objetivo

Preparar entidades e schemas para PRD versionado, lista de features e ligacao explicita com o intake aprovado.

## precondicoes

- ISSUE-F1-01-002 concluida
- trilha de aprovacao do intake estavel

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_prd_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir entidades de PRD e feature com referencia ao intake
  - cobrir metadados de aprovacao e status do PRD
  - cobrir serializacao da estrutura de features para a API
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k prd`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k schema`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato de PRD
3. implementar o minimo necessario em modelos e schemas do dominio
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes e enums locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k prd`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k schema`

## resultado_esperado

Modelagem do PRD pronta para armazenar features, origem e aprovacao.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_prd_flow.py -k schema`

## stop_conditions

- parar se a estrutura de feature exigir regra nao sustentada pelo PRD do FW5
- parar se a ligacao com o intake aprovado ficar ambigua
