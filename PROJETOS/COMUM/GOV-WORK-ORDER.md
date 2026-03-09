---
doc_id: "GOV-WORK-ORDER.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# GOV-WORK-ORDER

## Objetivo

Definir o contrato minimo de demanda entre camadas para qualquer execucao com side effect, persistencia ou custo operacional relevante.

## Schema Canonico

### Work order de implementacao

```yaml
work_order:
  work_order_id: "wo-2026-03-03-001"
  idempotency_key: "dashboard-age-analysis:evento-123:sha256"
  risk_class: "operacional"
  risk_tier: "R1"
  data_sensitivity: "interna"
  expected_output: "issue implementation package"
  scope:
    unit: "issue"
    issue_id: "ISSUE-F1-01-001"
    issue_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/issues/ISSUE-F1-01-001-NOME.md"
    task_instruction_mode: "required"
    epic_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/EPIC-F1-01-NOME.md"
    phase_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/F1_MEU_PROJETO_EPICS.md"
  budget:
    hard_cap: "30m_cpu|1_execucao"
  status: "pending"
```

### Work order de auditoria

```yaml
work_order:
  work_order_id: "wo-2026-03-08-017"
  idempotency_key: "landing-form-first:F1:audit:R01:sha"
  risk_class: "governanca"
  risk_tier: "R2"
  data_sensitivity: "interna"
  expected_output: "phase audit report"
  scope:
    unit: "audit"
    phase_id: "F1"
    phase_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/F1_MEU_PROJETO_EPICS.md"
    audit_round: "R01"
    audit_log_path: "PROJETOS/MEU-PROJETO/AUDIT-LOG.md"
    report_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/auditorias/RELATORIO-AUDITORIA-F1-R01.md"
    base_commit: "abc1234"
  budget:
    hard_cap: "45m_cpu|1_execucao"
  status: "pending"
```

## Regras

- para implementacao, a unidade padrao e `issue`
- para gate de fase, a unidade padrao e `audit`
- `epico` continua valido para planejamento
- `fase` continua valida para review e gate
- todo work order de execucao precisa nomear `issue_id` e `issue_path`
- quando a issue usar `task_instruction_mode: required`, o bloco `Instructions por Task` vira contrato de execucao vinculante
- todo work order de auditoria precisa nomear `phase_path`, `audit_log_path`, `report_path` e `base_commit`
- o arquivo da issue e a fonte primaria do escopo executavel
- o arquivo da auditoria e a fonte primaria do veredito de gate
- `epic_path` serve para contexto e consolidacao, nao substitui `issue_path`
- auditoria formal com worktree sujo deve ser registrada como `provisional` e nao pode emitir `go`
- quando o work order concluir o gate de uma fase com veredito `go`, o fechamento operacional deve incluir a movimentacao da pasta da fase para `<projeto>/feito/`
- `BLOQUEADO` e `BLOCKED_LIMIT` podem aparecer como estado operacional da execucao, mas nao substituem os status documentais canonicos
