---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F2-03-002-CONECTAR-PROTOCOLO-AOS-ARTEFATOS-OPERACIONAIS-DO-LOTE"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T1 - Conectar protocolo aos artefatos operacionais do lote

## objetivo

Amarrar o protocolo de fallback aos artefatos operacionais ja existentes de lote e reprocessamento, sem criar fluxo destrutivo novo.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingestao_inteligente.py`
- `backend/app/services/lead_pipeline_service.py`
- `backend/app/models/lead_batch.py`



## passos_atomicos

1. reler o PRD, o epic e a issue para isolar exatamente a lacuna documental ou operacional que a task deve fechar
2. comparar os arquivos alvo e registrar onde o estado atual contradiz o objetivo da issue
3. ajustar apenas o artefato minimo necessario para fechar a lacuna local sem reabrir temas fora do epic
4. revisar consistencia final do que foi produzido contra PRD, fase e dependencias
5. parar e reportar bloqueio se a task exigir novo requisito nao documentado

## comandos_permitidos

- `rg -n "reprocess|LeadBatch|stage|gold|silver|bronze" backend/app/routers/ingestao_inteligente.py backend/app/services/lead_pipeline_service.py backend/app/models/lead_batch.py`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" backend/app/routers/ingestao_inteligente.py backend/app/services/lead_pipeline_service.py backend/app/models/lead_batch.py`

## resultado_esperado

O protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.

## testes_ou_validacoes_obrigatorias

- conferir manualmente que o protocolo referencia claramente os artefatos e pontos de entrada existentes para fallback controlado.

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
