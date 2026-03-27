---
doc_id: "ISSUE-F2-02-002-SINCRONIZAR-WORKSPACE-VERSIONADO-NO-HOST"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-02-002 - Sincronizar workspace versionado no host

## User Story

Como operador do toolkit host-side, quero que o `main` local carregue automaticamente o workspace versionado para que a persona Assis e as regras QMD/OpenClaw sobrevivam a restore, `install-host.sh` e `git pull`.

## Feature de Origem

- **Feature**: Feature 3
- **Comportamento coberto**: sync local do workspace versionado com backup, toggle operacional e validação do `main`.

## Contexto Tecnico

O bootstrap local já cria a topologia `main/planner/builder/auditor`, mas o workspace `main` ainda dependia de cópia manual do snapshot versionado em `openclaw-workspace/`. O follow-up desta issue fecha esse drift sem tocar nos workspaces `planner`, `builder` e `auditor`.

## Plano TDD

- Red: demonstrar que `install-host.sh` e os hooks locais não propagam o workspace versionado
- Green: criar sync idempotente com backup e acoplá-lo ao install e aos hooks
- Refactor: alinhar validação e documentação ao novo comportamento operacional

## Criterios de Aceitacao

- [x] existe um comando operador para sincronizar `openclaw-workspace/` em `~/.openclaw/workspace`
- [x] o sync cria backup apenas quando há mudança efetiva
- [x] `install-host.sh` e os hooks locais acionam o sync do workspace principal
- [x] `bin/validate-host.sh` valida os marcadores Assis/QMD no `main`
- [x] README e `openclaw-workspace/README.md` documentam rollout, automação e autoridade do repo

## Definition of Done da Issue

- [x] sync local do workspace versionado implementado
- [x] toggle `OPENCLAW_LOCAL_WORKSPACE_SYNC_ENABLED` documentado
- [x] automação `install-host.sh` + hooks locais aplicada
- [x] validação e runbook atualizados

## Tasks

- [T1 - Sincronizar workspace versionado com backup e automação local](./TASK-1.md)

## Arquivos Reais Envolvidos

- `bin/sync-openclaw-workspace.sh`
- `bin/install-host.sh`
- `.githooks/_run-refresh-host-sync.sh`
- `config/host.env.example`
- `bin/validate-host.sh`
- `README.md`
- `openclaw-workspace/README.md`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)
