---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-03-001-DEFINIR-CRITERIO-OPERACIONAL-DE-FALLBACK-VIA-BRONZE"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T1 - Definir criterio operacional de fallback via bronze

## objetivo

Definir quando usar reenvio/reprocessamento de lote em vez de backfill direto, sem ampliar o escopo para automacao nova.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/models/lead_batch.py`
- `PROJETOS/DASHBOARD-LEADS/PRD-DASHBOARD-LEADS.md`



## passos_atomicos

1. reler o PRD, o epic e a issue para isolar exatamente a lacuna documental ou operacional que a task deve fechar
2. comparar os arquivos alvo e registrar onde o estado atual contradiz o objetivo da issue
3. ajustar apenas o artefato minimo necessario para fechar a lacuna local sem reabrir temas fora do epic
4. revisar consistencia final do que foi produzido contra PRD, fase e dependencias
5. parar e reportar bloqueio se a task exigir novo requisito nao documentado

## comandos_permitidos

- `rg -n "reprocess|bronze|silver|gold" backend/app/routers/ingestao_inteligente.py backend/app/models/lead_batch.py PROJETOS/DASHBOARD-LEADS/PRD-DASHBOARD-LEADS.md`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/routers/ingestao_inteligente.py backend/app/models/lead_batch.py PROJETOS/DASHBOARD-LEADS/PRD-DASHBOARD-LEADS.md`

## resultado_esperado

Existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.

## testes_ou_validacoes_obrigatorias

- conferir manualmente que existe criterio operacional claro para decidir entre backfill direto e fallback via bronze/reprocessamento.

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
