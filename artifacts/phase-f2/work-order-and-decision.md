# Phase F2 Work Order And Decision

## Estado Atual

Status operacional atual: `pending`.

Esta evidencia foi criada para registrar a governanca minima da Fase 2 antes da execucao da migracao de banco.

## Work Order

```yaml
work_order:
  work_order_id: "wo-f2-migracao-banco-2026-03-03-001"
  idempotency_key: "f2-migracao-banco:supabase-to-hostinger:dry-run"
  risk_class: "dados"
  risk_tier: "R3"
  data_sensitivity: "dados-pessoais"
  expected_output: "dump restore validado com contagens identicas de lead evento usuario"
  budget:
    hard_cap: "1 dump completo e 1 restore por janela aprovada"
  status: "pending"
  sla_class: "overnight"
```

## Decision

```yaml
decision:
  decision_id: "dec-f2-migracao-banco-2026-03-03-001"
  risk_tier: "R3"
  side_effect_class: "persistencia"
  explicit_human_approval: true
  rollback_plan: "manter Supabase como fonte de verdade, bloquear cutover e descartar destino local se a validacao falhar antes da reabertura de escrita"
```

## Checklist de Preflight

- `SUPABASE_DATABASE_URL` definido no contexto da janela.
- `LOCAL_DATABASE_URL` definido no contexto da janela.
- Aprovacao humana explicita registrada.
- Plano de rollback aceito pelo owner operacional.
- Janela de migracao validada como `R3`.
