---
doc_id: "ISSUE-F2-02-001-AUTOMATIZAR-BOOTSTRAP-HOST-SIDE-DO-OPENCLAW"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-001 - Automatizar bootstrap host-side do OpenClaw

## User Story

Como operador de host-side restore, quero que `install-host.sh` e o helper recriem a topologia OpenClaw/OpenRouter para que eu não precise editar `openclaw.json` manualmente.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: merge local/remoto da topologia e bootstrap idempotente via toolkit host-side.

## Contexto Tecnico

O toolkit atual já sabe sincronizar o dashboard remoto e tocar o `openclaw.json` remoto. Esta issue amplia esse bootstrap para uma topologia multi-agent e inclui o bootstrap local em `~/.openclaw/`.

## Plano TDD

- Red: demonstrar que o toolkit atual não cria a topologia OpenRouter/OpenClaw desejada
- Green: acoplar bootstrap local e merge remoto ao helper/install-host
- Refactor: consolidar defaults em variáveis locais e reduzir drift entre local e remoto

## Criterios de Aceitacao

- [x] `install-host.sh` aciona o bootstrap local do OpenClaw
- [x] `helper.js` faz merge local e remoto da topologia
- [x] `config/host.env.example` expõe placeholders para OpenRouter e Telegram
- [x] o dashboard remoto host-side continua preservado

## Definition of Done da Issue

- [x] helper suporta bootstrap local
- [x] helper suporta sync remoto com topologia ampliada
- [x] install-host aciona o bootstrap local
- [x] defaults locais não exigem secret em Git

## Tasks

- [T1 - Automatizar bootstrap local e sync remoto](./TASK-1.md)

## Arquivos Reais Envolvidos

- `src/nemoclaw-host/helper.js`
- `src/nemoclaw-host/common.sh`
- `bin/install-host.sh`
- `config/host.env.example`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md)
- [Epic anterior](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-01-CATALOGO-OPENROUTER-E-TOPOLOGIA-MULTI-AGENT.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)

## Handoff para Revisao Pos-Issue

- resumo_execucao: a sessao reconciliou a issue F2 com o estado operacional vigente; nenhuma mudanca de codigo foi necessaria porque o bootstrap local/remoto e as validacoes ja estavam conformes
- base_commit: `5d6aef802e92341c955b0cc393782be64e78721c`
- target_commit: `c69f3172d067f471b34922459e2e442b18fd4a27`
- evidencia: `git diff 5d6aef802e92341c955b0cc393782be64e78721c..c69f3172d067f471b34922459e2e442b18fd4a27`
- commits_execucao:
  - `6b266b015105477e653897b72b75c2101f750214`
  - `a6b6258e2f76ae13ec5c963fd3a72eb54ebccfe3`
  - `bcb0f852e91a0219f023be69573d9d204932f4e9`
  - `c69f3172d067f471b34922459e2e442b18fd4a27`
- validacoes_executadas:
  - `node --check src/nemoclaw-host/helper.js` -> ok
  - `bash -n src/nemoclaw-host/common.sh` -> ok
  - `bash -n bin/install-host.sh` -> ok
  - `bash -n bin/validate-host.sh` -> ok
  - `./bin/validate-host.sh` -> PASS em topologia local, launchd, dashboard remoto e allowlist Telegram
  - `~/.local/bin/nemoclaw-hostctl status` -> Colima/OpenShell conectados; dashboard remoto alcançável
  - `~/.local/bin/nemoclaw-hostctl dashboard --no-open` -> URL com token gerada
  - leitura de `~/.openclaw/openclaw.json` local -> `main/planner/builder/auditor`, binding do `planner`, catálogo OpenRouter, `gateway.port=18890`
  - leitura de `~/.openclaw/openclaw.json` remoto -> mesma topologia, `gateway.port=18789`, `controlUi.allowedOrigins` e `trustedProxies` corretos
  - `curl http://127.0.0.1:18789/` -> `HTTP/1.1 200 OK`
- arquivos_de_codigo_relevantes:
  - `src/nemoclaw-host/helper.js`
  - `src/nemoclaw-host/common.sh`
  - `bin/install-host.sh`
  - `config/host.env.example`
  - `bin/validate-host.sh`
- limitacoes: `nenhuma`
