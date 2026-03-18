---
doc_id: "TASK-1.md"
issue_id: "ISSUE-F4-02-001-FECHAR-OBSERVABILIDADE-ROLLBACK-E-PACOTE-DE-AUDITORIA"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
tdd_aplicavel: false
---

# T1 - Fechar observabilidade, rollback e pacote de auditoria

## objetivo

Fechar runbook, metricas, evidencias e rastreabilidade final necessaria para a auditoria do projeto.

## precondicoes

- README da issue lido integralmente
- PRD e epic da fase consultados antes de alterar qualquer arquivo
- dependencias declaradas na issue satisfeitas

## arquivos_a_ler_ou_tocar

- `PROJETOS/DASHBOARD-LEADS/AUDIT-LOG.md`
- `PROJETOS/DASHBOARD-LEADS/F4-DESATIVACAO-HEURISTICO-ENDURECIMENTO/`



## passos_atomicos

1. reler o PRD, o epic e a issue para isolar exatamente a lacuna documental ou operacional que a task deve fechar
2. comparar os arquivos alvo e registrar onde o estado atual contradiz o objetivo da issue
3. ajustar apenas o artefato minimo necessario para fechar a lacuna local sem reabrir temas fora do epic
4. revisar consistencia final do que foi produzido contra PRD, fase e dependencias
5. parar e reportar bloqueio se a task exigir novo requisito nao documentado

## comandos_permitidos

- `rg -n "go|hold|approved|rollback|metric|evid" PROJETOS/DASHBOARD-LEADS/AUDIT-LOG.md PROJETOS/DASHBOARD-LEADS/F4-DESATIVACAO-HEURISTICO-ENDURECIMENTO`
- `rg -n "lead_evento|LeadEvento|LeadEventoSourceKind|AtivacaoLead|evento_nome|lead_batch|manual_reconciled|dashboard" PROJETOS/DASHBOARD-LEADS/AUDIT-LOG.md PROJETOS/DASHBOARD-LEADS/F4-DESATIVACAO-HEURISTICO-ENDURECIMENTO/`

## resultado_esperado

Existe um pacote final de operacao e evidencia pronto para a auditoria formal da fase.

## testes_ou_validacoes_obrigatorias

- conferir manualmente que existe um pacote final de operacao e evidencia pronto para a auditoria formal da fase.

## stop_conditions

- parar se surgir requisito novo nao previsto no PRD ou no README da issue
- parar se o comando alvo falhar por motivo estrutural nao relacionado a escopo local
