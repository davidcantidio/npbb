---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-02-001-ALINHAR-FIXTURES-E-SUITES-AO-MODELO-CANONICO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# T1 - Alinhar fixtures e suite ao modelo canonico

## objetivo

Atualizar fixtures e suites de dashboard para semear `LeadEvento` e validar o comportamento canonico do runtime.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F2-02-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/tests/test_dashboard_age_analysis_endpoint.py backend/tests/test_dashboard_leads_endpoint.py backend/tests/test_dashboard_leads_report_endpoint.py`

## resultado_esperado

As suites de dashboard passam a refletir explicitamente o modelo canonico `LeadEvento`.

## testes_ou_validacoes_obrigatorias

- fixtures de dashboard criam `LeadEvento`
- os tres endpoints preservam payload e filtros com a fixture canonica

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
