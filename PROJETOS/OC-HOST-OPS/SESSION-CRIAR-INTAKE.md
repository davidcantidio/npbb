---
doc_id: "SESSION-CRIAR-INTAKE.md"
version: "2.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
project: "OC-HOST-OPS"
---

# SESSION-CRIAR-INTAKE - Criacao de Intake em Sessao de Chat

## Objetivo

Revisar ou expandir o intake real do host-side a partir do worktree atual, nao do scaffold generico.

## Sessao Canonica

Leia e siga integralmente:

- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`

## Parametros Preenchidos

```text
PROJETO:       OC-HOST-OPS
INTAKE_KIND:   new-capability
SOURCE_MODE:   backfilled
ORIGEM:        camada host-side reproduzivel do repo openclaw atual
ORIGIN_AUDIT:  nao_aplicavel
CONTEXT:       install, restore, validate, launchd, dashboard tunnel e Telegram bridge do host macOS
OBSERVACOES:   manter a fronteira host-side separada de Mission Control e Trading
```

## Regra Local Adicional

Nao volte ao contexto de scaffold. O intake atual ja e a fonte de verdade do projeto.
