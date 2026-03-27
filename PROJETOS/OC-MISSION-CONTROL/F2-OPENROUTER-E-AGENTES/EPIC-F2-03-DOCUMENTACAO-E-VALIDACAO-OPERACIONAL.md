---
doc_id: "EPIC-F2-03-DOCUMENTACAO-E-VALIDACAO-OPERACIONAL.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-20"
---

# EPIC-F2-03 - Documentacao e validacao operacional

## Objetivo

Descrever o fluxo híbrido e automatizar a verificação do que significa ambiente pronto para o trio especializado.

## Resultado de Negocio Mensuravel

O operador consegue verificar a topologia local sem abrir o código e sabe quando usar `planner`, `builder` e `auditor`.

## Feature de Origem

- **Feature**: Feature 4
- **Comportamento coberto**: runbook, matriz tarefa -> agente e validações locais.

## Contexto Arquitetural

- `README.md`
- `bin/validate-host.sh`
- artefatos de fase/issue

## Definition of Done do Epico

- [x] README descreve bootstrap e fluxo híbrido
- [x] validate-host cobre a topologia local
- [x] a fase F2 mantém rastreabilidade de configuração, automação e validação

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA | Documentar e validar operação híbrida | Dar um runbook curto e checks automatizados para a topologia OpenClaw/OpenRouter. | 3 | done | [ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/issues/ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA) | Feature 4 |

## Artifact Minimo do Epico

- `README.md` da issue
- `TASK-1.md`

## Dependencias

- [Epic anterior](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)
