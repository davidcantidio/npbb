---
doc_id: "SESSION-REVISAR-US.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-26"
project: "NPBB"
---

# SESSION-REVISAR-US - Revisao Pos-User Story em Sessao de Chat

## Objetivo

Revisar a user story atualmente em `ready_for_review` ou a user story explicitamente indicada pelo PM.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REVISAR-US.md`

## Parametros Preenchidos

```text
PROJETO:        NPBB
FEATURE_ID:     <resolver_no_handoff_ou_na_us_alvo>
US_ID:          <resolver_no_handoff_ou_na_us_alvo>
US_PATH:        <resolver_no_handoff_ou_na_us_alvo>
BASE_COMMIT:    auto
TARGET_COMMIT:  auto
EVIDENCIA:      auto
OBSERVACOES:    usar o handoff persistido na user story alvo sempre que existir
REVIEW_MODE:    auto
```

## Regra Local Adicional

- resolva primeiro a user story `ready_for_review` vigente do projeto; so use override manual quando o PM trouxer evidencia reproduzivel
- este wrapper nao fixa a revisao na bootstrap; a US alvo muda conforme a fila
- em caso de conflito, o handoff persistido na user story continua sendo a fonte de verdade
