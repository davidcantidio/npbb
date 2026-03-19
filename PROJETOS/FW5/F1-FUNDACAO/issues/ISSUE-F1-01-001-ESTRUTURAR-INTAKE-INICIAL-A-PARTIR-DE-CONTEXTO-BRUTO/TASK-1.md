---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-001-ESTRUTURAR-INTAKE-INICIAL-A-PARTIR-DE-CONTEXTO-BRUTO"
task_id: "T1"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# TASK-1 - Modelar intake, versoes, lacunas e aprovacoes

## objetivo

Fechar as entidades persistidas e os contratos basicos necessarios para intake versionado e auditavel.

## precondicoes

- issue bootstrap do scaffold ja foi supersedida pelo backlog canonico
- taxonomias controladas de `GOV-INTAKE.md` estao definidas

## arquivos_a_ler_ou_tocar

- `backend/app/models/framework_models.py`
- `backend/app/schemas/framework.py`
- `backend/tests/test_framework_domain_contract.py`
- `backend/tests/test_framework_intake_flow.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir campos obrigatorios de intake, estado de aprovacao e estrutura de lacunas conhecidas
  - cobrir serializacao de checklist de prontidao e historico minimo de versao
- comando_para_rodar:
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k intake`
  - `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k schema`
- criterio_red:
  - os testes acima devem falhar antes da implementacao; se passarem, parar e revisar a task

## passos_atomicos

1. escrever os testes listados em `testes_red`
2. rodar os comandos red e confirmar falha inicial ligada ao contrato esperado
3. implementar o minimo necessario em modelos e schemas para intake versionado
4. rodar novamente as suites alvo e confirmar green
5. refatorar nomes e enums locais sem ampliar o escopo mantendo a suite green

## comandos_permitidos

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py -k intake`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k schema`

## resultado_esperado

Entidades e schemas de intake prontos para sustentar versao, lacuna, checklist e aprovacao.

## testes_ou_validacoes_obrigatorias

- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_domain_contract.py`
- `cd backend && SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest -q tests/test_framework_intake_flow.py -k schema`

## stop_conditions

- parar se a modelagem proposta entrar em conflito com `GOV-INTAKE.md`
- parar se for necessario inventar taxonomia fora das listas controladas
