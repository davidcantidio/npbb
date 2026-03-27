---
doc_id: "SPRINT-F2-01.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
---

# SPRINT-F2-01 - OpenRouter e Agentes

## Objetivo da Sprint

Entregar a primeira fatia reproduzível do Mission Control com topologia multi-agent, bootstrap host-side e validação operacional.

## Capacidade e Foco

- capacidade estimada: média
- foco: transformar o desenho OpenRouter + trio especializado em config e operação concretas

## Issues Selecionadas

| Issue ID | Nome | SP | Status | Feature | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS | Configurar catálogo OpenRouter e agentes especializados | 5 | done | Feature 2 | [ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-01-001-CONFIGURAR-CATALOGO-OPENROUTER-E-AGENTES-ESPECIALIZADOS) |
| ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW | Automatizar bootstrap host-side do OpenClaw | 5 | done | Feature 3 | [ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW) |
| ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST | Sincronizar workspace versionado no host | 3 | done | Feature 3 | [ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST) |
| ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA | Documentar e validar operação híbrida | 3 | done | Feature 4 | [ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA) |

## Riscos

- auth OpenRouter ausente e topologia ficar só scaffolding
- regressão do dashboard host-side ao tocar no helper
- conflito entre porta local do OpenClaw e túnel remoto do dashboard

## Definition of Done

- [x] as três issues da sprint estão linkadas e rastreáveis
- [x] a topologia local é validada sem secret real
- [x] o runbook reflete o comportamento do bootstrap
