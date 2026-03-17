---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-03-001-GARANTIR-LEAD-EVENTO-NO-PIPELINE-GOLD"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# T1 - Garantir LeadEvento no pipeline Gold

## objetivo

Fechar o caminho `LeadBatch.evento_id -> LeadEvento` no pipeline Gold com idempotencia clara.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/services/lead_pipeline_service.py`
- `backend/app/models/lead_batch.py`
- `backend/tests/test_lead_gold_pipeline.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F1-03-001` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_gold_pipeline.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_gold_pipeline.py`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/services/lead_pipeline_service.py backend/app/models/lead_batch.py backend/tests/test_lead_gold_pipeline.py`

## resultado_esperado

Leads promovidos a Gold asseguram `LeadEvento` quando o lote conhece `evento_id`.

## testes_ou_validacoes_obrigatorias

- promocao para Gold assegura `LeadEvento`
- reprocessamento do lote nao duplica `(lead_id, evento_id)`

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
