---
doc_id: "SESSION-REVISAR-US.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-25"
project: "OPENCLAW-MIGRATION"
---

# SESSION-REVISAR-US - Revisao Pos-User Story em Sessao de Chat

## Objetivo

Revisar a user story atualmente em `ready_for_review` em
`OPENCLAW-MIGRATION`, usando o handoff persistido na propria US.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-REVISAR-US.md`

## Parametros Preenchidos

```text
PROJETO:      OPENCLAW-MIGRATION
FEATURE_ID:   <resolver_no_handoff_ou_na_us_alvo>
US_ID:        <resolver_no_handoff_ou_na_us_alvo>
US_PATH:      <resolver_no_handoff_ou_na_us_alvo>
BASE_COMMIT:  auto
TARGET_COMMIT:auto
EVIDENCIA:    auto
OBSERVACOES:  usar o handoff persistido na user story alvo sempre que existir
REVIEW_MODE:  auto
```

## Regra Local Adicional

- a fonte de verdade da revisao e o handoff em `## Handoff para Revisao Pos-User Story`
- nao use wrappers `ISSUE` historicos deste projeto como atalho
- se ainda nao houver US `ready_for_review`, retorne para execucao ou para o
  planejamento conforme o estado da feature

