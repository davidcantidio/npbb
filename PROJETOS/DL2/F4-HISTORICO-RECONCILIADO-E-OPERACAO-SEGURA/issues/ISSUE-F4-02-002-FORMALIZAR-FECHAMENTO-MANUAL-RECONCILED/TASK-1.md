---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-02-002-FORMALIZAR-FECHAMENTO-MANUAL-RECONCILED"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
tdd_aplicavel: true
---

# T1 - Formalizar fechamento manual_reconciled

## objetivo

Definir e materializar o caminho minimo para marcar um vinculo historico como `manual_reconciled` com evidencia de origem.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/services/lead_event_service.py`
- `backend/tests/test_lead_event_service.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F4-02-002` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k manual_reconciled`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_lead_event_service.py -k manual_reconciled`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/services/lead_event_service.py backend/tests/test_lead_event_service.py`

## resultado_esperado

Existe caminho explicito para registrar `manual_reconciled` sem perder rastreabilidade do fechamento manual.

## testes_ou_validacoes_obrigatorias

- fechamento manual atualiza `source_kind` para `manual_reconciled`
- o fechamento manual preserva `lead_id`, `evento_id` e referencia de origem

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
