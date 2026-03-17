---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F1-01-002-VERSIONAR-MIGRATION-LEAD-EVENTO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: true
---

# T1 - Versionar migration de lead_evento

## objetivo

Criar ou validar a migration Alembic da tabela `lead_evento` com FKs, indices e `UNIQUE (lead_id, evento_id)`.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/alembic/versions/`
- `backend/app/models/lead_public_models.py`
- `backend/app/models/models.py`

## testes_red

- testes_a_escrever_primeiro:
  - cobrir o contrato principal de `ISSUE-F1-01-002` no modulo alvo
  - cobrir um caso de regressao ligado ao paradigma canonico `LeadEvento`
- comando_para_rodar:
  - `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_alembic_single_head.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao; se ja passarem sem mudanca de codigo, parar e revisar a task

## passos_atomicos

1. escrever ou ajustar primeiro os testes focados listados em `testes_red`
2. rodar o comando red e confirmar falha ligada ao comportamento esperado da issue
3. implementar o minimo necessario nos arquivos alvo para satisfazer apenas o contrato descrito
4. rodar novamente a suite alvo e confirmar green
5. refatorar nomes, imports ou duplicacoes locais sem ampliar escopo

## comandos_permitidos

- `cd backend && PYTHONPATH=.. SECRET_KEY=ci-secret-key TESTING=true python3 -m pytest -q tests/test_alembic_single_head.py`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/alembic/versions/ backend/app/models/lead_public_models.py backend/app/models/models.py`

## resultado_esperado

Existe uma migration versionada e rastreavel para `lead_evento`, aderente ao modelo SQLModel atual.

## testes_ou_validacoes_obrigatorias

- validar cabeca unica de migration
- validar que a migration cria a estrutura de `lead_evento` esperada

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
