---
doc_id: "F2_OC-MISSION-CONTROL_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-23"
audit_gate: "pending"
---

# Epicos - OC-MISSION-CONTROL / F2 - OpenRouter e Agentes

## Objetivo da Fase

Materializar a primeira topologia governada de agentes/modelos do Mission Control com OpenRouter, bootstrap host-side e validação operacional.

## Gate de Saida da Fase

O ambiente local consegue reproduzir `main/planner/builder/auditor`, o binding Telegram do `planner`, o catálogo OpenRouter e as validações mínimas sem secrets no Git.

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `nao_aplicavel`
- veredito_atual: `nao_aplicavel`
- relatorio_mais_recente: `PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/auditorias/RELATORIO-AUDITORIA-F2-R01.md`
- log_do_projeto: [PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md](PROJETOS/OC-MISSION-CONTROL/AUDIT-LOG.md)

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os épicos estão `done`
- [x] todas as issues filhas estão `done`
- [x] README, helper e validate-host foram revisados em conjunto

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria é `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria é `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Feature | Depende de | Status | Arquivo |
|---|---|---|---|---|---|---|
| EPIC-F2-01 | Catalogo OpenRouter e topologia multi-agent | Explicitar agentes, modelos e binding inicial no runtime. | Feature 2 | EPIC-F1-01 | done | [EPIC-F2-01 - Catalogo OpenRouter e topologia multi-agent](./EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md) |
| EPIC-F2-02 | Automacao host-side do bootstrap OpenClaw | Materializar a topologia via toolkit host-side. | Feature 3 | EPIC-F2-01 | done | [EPIC-F2-02 - Automacao host-side do bootstrap OpenClaw](./EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md) |
| EPIC-F2-03 | Documentacao e validacao operacional | Publicar runbook e validações da topologia local. | Feature 4 | EPIC-F2-02 | done | [EPIC-F2-03 - Documentacao e validacao operacional](./EPIC-F2-03-DOCUMENTACAO-E-VALIDACAO-OPERACIONAL.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende de `EPIC-F1-01`
- `EPIC-F2-02`: depende de `EPIC-F2-01`
- `EPIC-F2-03`: depende de `EPIC-F2-02`

## Escopo desta Fase

### Dentro
- catálogo OpenRouter no config
- topologia `main/planner/builder/auditor`
- bootstrap host-side reproduzível
- validação operacional e runbook

### Fora
- persistência de `router_decision` em banco
- budget/trace store do intake completo
- múltiplos canais automáticos além do Telegram

## Definition of Done da Fase
- [x] `~/.openclaw/openclaw.json` materializa a topologia declarada
- [x] `planner` possui binding Telegram configurado
- [x] `install-host.sh` aciona o bootstrap local
- [x] `validate-host.sh` valida a topologia local
- [x] README descreve o fluxo híbrido e a matriz tarefa -> agente
- [x] relatório base de auditoria existe em `auditorias/`
