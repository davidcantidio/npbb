---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-02-001-GARANTIR-DUAL-WRITE-NO-SUBMIT-PUBLICO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# T1 - Garantir dual-write no submit publico

## objetivo

Consolidar `ensure_lead_event` no fluxo publico com e sem `ativacao`, mantendo a ordem transacional minima do PRD.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/services/landing_page_submission.py`
- `backend/app/services/lead_event_service.py`
- `backend/tests/test_landing_public_endpoints.py`
- `backend/tests/test_leads_public_create_endpoint.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F1-02-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_landing_public_endpoints.py tests/test_leads_public_create_endpoint.py -k lead_event`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_landing_public_endpoints.py tests/test_leads_public_create_endpoint.py -k lead_event`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/services/landing_page_submission.py backend/app/services/lead_event_service.py backend/tests/test_landing_public_endpoints.py backend/tests/test_leads_public_create_endpoint.py`

## resultado_esperado

O fluxo publico assegura `LeadEvento` tanto no submit direto do evento quanto no submit associado a ativacao.

## testes_ou_validacoes_obrigatorias

- submit sem ativacao cria ou assegura `LeadEvento`
- submit com ativacao cria ou assegura `LeadEvento` antes de depender de `AtivacaoLead`

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
