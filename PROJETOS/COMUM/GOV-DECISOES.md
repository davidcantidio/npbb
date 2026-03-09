---
doc_id: "GOV-DECISOES.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-09"
---

# GOV-DECISOES

## Taxonomia de Risco

- `R0`: sem side effect, sem custo relevante, sem impacto operacional
- `R1`: side effect baixo e reversivel, baixo impacto operacional
- `R2`: side effect moderado, exige observabilidade e rollback claro
- `R3`: side effect alto, potencial de impacto relevante em dados, usuarios ou operacao

## Schema YAML de Decision

```yaml
decision:
  decision_id: "dec-2026-03-03-001"
  risk_tier: "R2"
  side_effect_class: "persistencia"
  explicit_human_approval: true
  rollback_plan: "restaurar snapshot anterior e invalidar lote atual"
  status: "APPROVED"
```

## Maquina de Estados

`PENDING -> APPROVED | REJECTED | KILLED | EXPIRED`

## Regras de Estado

- `PENDING`: aguardando avaliacao e, quando necessario, aprovacao humana
- `APPROVED`: apta a executar dentro dos limites definidos
- `REJECTED`: avaliada e negada por risco, custo ou inconsistencias
- `KILLED`: interrompida apos aprovacao por condicao de seguranca ou rollback
- `EXPIRED`: perdeu validade temporal ou contextual antes da execucao

## SLA

- risco alto p95 `<= 15 min`
- risco medio p95 `<= 60 min`

## Regras Operacionais

- toda decision com `R2` ou `R3` deve ter `rollback_plan`
- `explicit_human_approval` e obrigatorio quando o side effect nao for trivialmente reversivel
- nenhuma decision pode ir para `APPROVED` sem contexto suficiente para execucao auditavel
- transicoes devem ser registradas com timestamp e agente responsavel
- decision que conclui gate de fase deve incluir como acao de fechamento a movimentacao da fase para `<projeto>/feito/` e a atualizacao dos caminhos relacionados

## Registro Ativo

| Decision ID | Data | Escopo | Risk Tier | Status | Decisao |
|---|---|---|---|---|---|
| `dec-2026-03-09-001` | `2026-03-09` | `framework/planning` | `R1` | `APPROVED` | `PROMPT-PLANEJAR-FASE.md` permanece como artefato complementar consumido por `SESSION-PLANEJAR-PROJETO.md`; nao deve substituir o fluxo de sessao e nao esta depreciado. |

## Notas de Uso

- `decision_refs` em issues e auditorias podem apontar para IDs deste registro ou para um `DECISION-PROTOCOL.md` local do projeto
- decisoes estruturais de `PROJETOS/COMUM/` devem preferir este arquivo como registro compartilhado
