---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-01-001-ESTABILIZAR-SURFACE-DE-MODELO-E-BOOT-DA-BASELINE-CANONICA"
task_id: "T1"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# T1 - Estabilizar surface de modelo e boot da baseline canonica

## objetivo

Fechar o drift restante do agregado de modelos e do boot da aplicacao, reaproveitando como evidencia a exportacao ja concluida no legado sem reabrir o item herdado `done`.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- entendimento explicito de que `ISSUE-F1-01-003` do legado entra apenas como evidencia parcial

## arquivos_a_ler_ou_tocar

- `backend/app/models/models.py`
- `backend/app/models/lead_public_models.py`
- `backend/app/services/landing_page_submission.py`
- `backend/app/services/lead_event_service.py`
- `backend/tests/test_dashboard_age_analysis_endpoint.py`
- `backend/tests/test_dashboard_leads_endpoint.py`
- `backend/tests/test_dashboard_leads_report_endpoint.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F2-01-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para fechar apenas o drift restante da baseline canonica
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_dashboard_age_analysis_endpoint.py tests/test_dashboard_leads_endpoint.py tests/test_dashboard_leads_report_endpoint.py`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/models/models.py backend/app/models/lead_public_models.py backend/app/services/landing_page_submission.py backend/app/services/lead_event_service.py`

## resultado_esperado

A aplicacao sobe sem `ImportError` e os modulos que dependem de `LeadEvento` ou `LeadEventoSourceKind` importam pelo caminho canonico esperado para o `DL2`.

## testes_ou_validacoes_obrigatorias

- coleta de `tests/test_dashboard_age_analysis_endpoint.py` sem erro de import
- coleta de `tests/test_dashboard_leads_endpoint.py` sem erro de import
- coleta de `tests/test_dashboard_leads_report_endpoint.py` sem erro de import

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
