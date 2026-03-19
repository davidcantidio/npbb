---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-01-002-TESTAR-PRECEDENCIA-E-IDEMPOTENCIA-DO-BACKFILL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# T1 - Testar precedencia e idempotencia do backfill

## objetivo

Cobrir precedencia de `source_kind`, upgrade de fonte e idempotencia do backfill.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_event_service.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F4-01-002` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k source_kind`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k source_kind`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/services/lead_event_service.py backend/tests/test_lead_event_service.py`

## resultado_esperado

A precedencia `ACTIVATION > LEAD_BATCH > EVENT_DIRECT > EVENT_NAME_BACKFILL` fica coberta e rastreavel.

## testes_ou_validacoes_obrigatorias

- fonte de maior prioridade atualiza `source_kind`
- runner nao regride a fonte de maior prioridade ja materializada

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
