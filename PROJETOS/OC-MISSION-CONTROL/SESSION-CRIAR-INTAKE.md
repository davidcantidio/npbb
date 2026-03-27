---
doc_id: "SESSION-CRIAR-INTAKE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-MISSION-CONTROL"
---

# SESSION-CRIAR-INTAKE - Criacao de Intake em Sessao de Chat

## Objetivo

Revisar ou expandir o intake retroativo do Mission Control a partir do backlog real ja consolidado no repo.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`

## Parametros Preenchidos

```text
PROJETO:       OC-MISSION-CONTROL
INTAKE_KIND:   new-capability
SOURCE_MODE:   backfilled
ORIGEM:        OPENCLAW-LEGADO consolidado em artefatos existentes
ORIGIN_AUDIT:  nao_aplicavel
CONTEXT:       runtime governado, OpenRouter, agentes especializados, budget, hooks, canais HITL e backlog ja materializado em intake/PRD atuais
OBSERVACOES:   usar este wrapper apenas para ampliar ou corrigir o intake real do Mission Control
```

## Regra Local Adicional

O intake atual ja e a fonte de verdade do projeto. Nao reutilize este wrapper como se o projeto ainda estivesse no scaffold inicial.
