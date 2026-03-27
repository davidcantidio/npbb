---
doc_id: "EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
---

# EPIC-F2-02 - Automacao host-side do bootstrap OpenClaw

## Objetivo

Fazer o toolkit host-side recriar a topologia OpenClaw/OpenRouter de modo idempotente, sem secrets versionados.

## Resultado de Negocio Mensuravel

Reinstalar o toolkit ou reprovisionar a máquina deixa a configuração local pronta sem edição manual do `openclaw.json`.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: merge local/remoto no helper, bootstrap no install-host e placeholders no `host.env`.

## Contexto Arquitetural

- `src/nemoclaw-host/helper.js`
- `src/nemoclaw-host/common.sh`
- `bin/install-host.sh`
- `config/host.env.example`

## Definition of Done do Epico

- [x] helper faz merge da topologia no config local
- [x] helper preserva o sync remoto do dashboard
- [x] install-host aciona o bootstrap local automaticamente
- [x] `host.env.example` documenta placeholders sem secret real

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW | Automatizar bootstrap host-side do OpenClaw | Tornar reproduzível a configuração OpenClaw/OpenRouter no toolkit host-side. | 5 | done | [ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW) | Feature 3 |
| ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST | Sincronizar workspace versionado no host | Fazer o `main` local carregar o snapshot versionado de Assis/QMD com backup e automação por install + hooks. | 3 | done | [ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST) | Feature 3 |

## Artifact Minimo do Epico

- `README.md` da issue
- `TASK-1.md`

## Dependencias

- [Epic anterior](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)
