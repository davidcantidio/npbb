---
doc_id: "WORK-ORDER-SPEC.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-07"
---

# WORK-ORDER-SPEC

## Objetivo

Definir o contrato minimo de demanda entre camadas para qualquer execucao com side effect, persistencia ou custo operacional relevante.

## Schema Canonico

```yaml
work_order:
  work_order_id: "wo-2026-03-03-001"
  idempotency_key: "lead-etl-import-preview:evento-123:sha256"
  risk_class: "operacional"
  risk_tier: "R1"
  data_sensitivity: "interna"
  expected_output: "issue implementation package"
  scope:
    unit: "issue"
    issue_id: "ISSUE-F2-01-02-IMPLEMENTAR-ENDPOINT"
    issue_path: "PROJETOS/MEU-PROJETO/F2-MINHA-FASE/issues/ISSUE-F2-01-02-IMPLEMENTAR-ENDPOINT.md"
    epic_path: "PROJETOS/MEU-PROJETO/F2-MINHA-FASE/EPIC-F2-01-MINHA-CAPACIDADE.md"
  budget:
    hard_cap: "30m_cpu|1_execucao"
  status: "pending"
```

## Campos Obrigatorios

- `work_order_id`
- `idempotency_key`
- `risk_class`
- `risk_tier`
- `data_sensitivity`
- `expected_output`
- `scope.unit`
- `budget.hard_cap`
- `status`

## Unidade de Execucao Recomendada

- para trabalho de implementacao, a unidade padrao e `issue`
- `epico` continua valido como unidade de planejamento
- `fase` continua valida como unidade de review e gate
- work order de execucao com side effect deve nomear `issue_id` e `issue_path` quando o projeto usar o padrao `issue-first`

## SLA Classes

- `instantaneo`
- `normal`
- `overnight`

## Exemplo Minimo

```yaml
work_order:
  work_order_id: "wo-import-etl-preview-0001"
  idempotency_key: "preview:evento-42:filehash-abc123"
  risk_class: "dados"
  risk_tier: "R1"
  data_sensitivity: "dados-pessoais"
  expected_output: "implementar uma issue e atualizar seus artefatos de status"
  scope:
    unit: "issue"
    issue_id: "ISSUE-F1-02-03-ETL-PREVIEW"
    issue_path: "PROJETOS/LEAD-ETL-FUSION/F1-NUCLEO-ETL/issues/ISSUE-F1-02-03-ETL-PREVIEW.md"
    epic_path: "PROJETOS/LEAD-ETL-FUSION/F1-NUCLEO-ETL/EPIC-F1-02-MODELO-CANONICO-LEAD-ROW.md"
  budget:
    hard_cap: "1 arquivo por execucao"
  status: "pending"
  sla_class: "normal"
```

## Regras

- todo work order deve ser idempotente por `idempotency_key`
- `risk_tier` deve seguir a taxonomia de `DECISION-PROTOCOL.md`
- `status` deve refletir o estado atual da execucao, nunca um estado presumido
- output esperado deve ser verificavel por artefato, log, persistencia ou resposta de API
- quando `scope.unit=issue`, o arquivo da issue e a fonte primaria do escopo executavel
- `epic_path` serve como contexto de navegacao e consolidacao, nao substitui `issue_path` em projetos `issue-first`
- quando um work order concluir o gate de uma fase, o fechamento operacional deve incluir a movimentacao da pasta da fase para `feito/` no projeto correspondente
