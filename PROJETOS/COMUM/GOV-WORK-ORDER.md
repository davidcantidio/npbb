---
doc_id: "GOV-WORK-ORDER.md"
version: "2.2"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
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
    issue_path: "PROJETOS/MEU-PROJETO/F1-MINHA-FASE/issues/ISSUE-F1-01-001-NOME/"
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
- `issue_path` pode apontar para pasta `ISSUE-*/` com `README.md` e `TASK-*.md`
  ou para arquivo legado `ISSUE-*.md`
- quando a issue usar `task_instruction_mode: required`, o contrato de
  execucao vinculante vive em `TASK-N.md` (issue granularizada) ou em
  `## Instructions por Task` (issue legada)
- todo work order de auditoria precisa nomear `phase_path`, `audit_log_path`, `report_path` e `base_commit`
- o manifesto da issue (`README.md` da pasta ou arquivo legado) e a fonte
  primaria do escopo executavel
- quando o escopo executavel for uma user story (pasta `US-*/` com
  `README.md` ou manifesto legado equivalente no projeto), `SCOPE-LEARN.md` no
  mesmo diretorio, quando existir, e entrada suplementar valida para revisao de
  criterios de aceite em `SESSION-REVISAR-US.md`; nao substitui o manifesto
  primario nem o PRD
- quando a issue for granularizada, a task selecionada em `TASK-N.md` completa
  o escopo operacional da work order
- o arquivo da auditoria e a fonte primaria do veredito de gate
- `epic_path` serve para contexto e consolidacao, nao substitui `issue_path`
- auditoria formal com worktree sujo deve ser registrada como `provisional` e nao pode emitir `go`
- quando o work order concluir o gate de uma fase com veredito `go`, o fechamento operacional deve incluir a movimentacao da pasta da fase para `<projeto>/feito/`
- `BLOQUEADO` e `BLOCKED_LIMIT` podem aparecer como estado operacional da execucao, mas nao substituem os status documentais canonicos
