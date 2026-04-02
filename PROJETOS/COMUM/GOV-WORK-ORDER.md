---
doc_id: "GOV-WORK-ORDER.md"
version: "3.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
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
  expected_output: "user story implementation package"
  scope:
    unit: "user_story"
    user_story_id: "US-1-01-NOME"
    user_story_path: "PROJETOS/MEU-PROJETO/features/FEATURE-1-MINHA-FEATURE/user-stories/US-1-01-NOME/"
    task_instruction_mode: "required"
    feature_path: "PROJETOS/MEU-PROJETO/features/FEATURE-1-MINHA-FEATURE/FEATURE-1.md"
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
  expected_output: "feature audit report"
  scope:
    unit: "audit"
    feature_id: "FEATURE-1"
    feature_path: "PROJETOS/MEU-PROJETO/features/FEATURE-1-MINHA-FEATURE/FEATURE-1.md"
    audit_round: "R01"
    audit_log_path: "PROJETOS/MEU-PROJETO/AUDIT-LOG.md"
    report_path: "PROJETOS/MEU-PROJETO/features/FEATURE-1-MINHA-FEATURE/auditorias/RELATORIO-AUDITORIA-FEATURE-1-R01.md"
    base_commit: "abc1234"
  budget:
    hard_cap: "45m_cpu|1_execucao"
  status: "pending"
```

## Regras

- para implementacao, a unidade padrao e `user_story`
- para gate de auditoria, a unidade padrao e `audit`
- referencias a `issue`, `epico` e `fase` sobrevivem apenas como compatibilidade
  historica em artefatos legados
- todo work order de execucao precisa nomear `user_story_id` e `user_story_path`
- `user_story_path` pode apontar para pasta `US-*/` com `README.md` e `TASK-*.md`
  ou para manifesto legado equivalente ainda preservado no projeto
- quando a user story usar `task_instruction_mode: required`, o contrato de
  execucao vinculante vive em `TASK-N.md` (US granularizada) ou em
  `## Instructions por Task` (US legada)
- todo work order de auditoria precisa nomear `feature_path`, `audit_log_path`,
  `report_path` e `base_commit`
- o manifesto da user story (`README.md` da pasta ou arquivo legado) e a fonte
  primaria do escopo executavel
- `SCOPE-LEARN.md` no
  mesmo diretorio, quando existir, e entrada suplementar valida para revisao de
  criterios de aceite em `SESSION-REVISAR-US.md`; nao substitui o manifesto
  primario nem o PRD
- quando a user story for granularizada, a task selecionada em `TASK-N.md` completa
  o escopo operacional da work order
- o arquivo da auditoria e a fonte primaria do veredito de gate
- `feature_path` serve para contexto e consolidacao, nao substitui
  `user_story_path`
- auditoria formal com worktree sujo deve ser registrada como `provisional` e nao pode emitir `go`
- quando o work order concluir o gate de uma feature com veredito `go`, o
  fechamento operacional deve incluir a movimentacao da pasta da feature para
  `features/encerradas/`
- `BLOQUEADO` e `BLOCKED_LIMIT` podem aparecer como estado operacional da execucao, mas nao substituem os status documentais canonicos
