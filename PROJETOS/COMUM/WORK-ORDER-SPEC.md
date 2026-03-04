---
doc_id: "WORK-ORDER-SPEC.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-03"
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
  expected_output: "dq_report_preview"
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
- `budget.hard_cap`
- `status`

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
  expected_output: "preview com contagem de linhas validas e invalidas"
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
- quando um work order concluir o gate de uma fase, o fechamento operacional deve incluir a movimentacao da pasta da fase para `feito/` no projeto correspondente
