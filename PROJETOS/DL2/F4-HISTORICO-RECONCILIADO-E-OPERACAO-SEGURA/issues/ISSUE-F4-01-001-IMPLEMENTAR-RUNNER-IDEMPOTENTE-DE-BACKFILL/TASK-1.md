---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-01-001-IMPLEMENTAR-RUNNER-IDEMPOTENTE-DE-BACKFILL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# T1 - Implementar runner idempotente de backfill

## objetivo

Transformar a logica de backfill em execucao controlada e rastreavel para `AtivacaoLead`, `LeadBatch` e `evento_nome` deterministico.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/services/lead_event_service.py`
- `backend/scripts/`
- `backend/tests/test_lead_event_service.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F4-01-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k backfill`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k backfill`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/services/lead_event_service.py backend/scripts/ backend/tests/test_lead_event_service.py`

## resultado_esperado

Existe um runner controlado que materializa `LeadEvento` sem duplicar pares ja existentes.

## testes_ou_validacoes_obrigatorias

- runner cria links faltantes nas tres fontes previstas
- runner reexecuta sem duplicar registros

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
