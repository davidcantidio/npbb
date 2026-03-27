---
doc_id: "ISSUE-F2-03-001-DOCUMENTAR-E-VALIDAR-OPERACAO-HIBRIDA"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-20"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-03-001 - Documentar e validar operação híbrida

## User Story

Como operador, quero um runbook curto e uma validação objetiva da topologia para que eu saiba quando usar `planner`, `builder` e `auditor` e consiga checar se o ambiente ficou pronto.

## Feature de Origem

- **Feature**: Feature 4
- **Comportamento coberto**: README operacional e validações locais do toolkit.

## Contexto Tecnico

O estado versionado atual do repositório já materializa o escopo desta issue em `README.md` e `bin/validate-host.sh`. A reconciliação desta issue é principalmente documental: sincronizar o backlog com o comportamento real já disponível para a operação diária.

## Plano TDD

- Red: demonstrar que o README e o validate-host não explicam nem verificam a topologia
- Green: publicar runbook curto e checks automatizados
- Refactor: manter a explicação alinhada ao comportamento real do bootstrap

## Criterios de Aceitacao

- [x] README traz bootstrap, matriz tarefa -> agente e checks manuais
- [x] validate-host checa config local, agentes, bindings e catálogo
- [x] a validação não depende de credencial OpenRouter ou Telegram real para passar

## Definition of Done da Issue

- [x] runbook operacional curto publicado
- [x] validações locais automatizadas
- [x] topologia local inspecionável sem abrir o código

## Tasks

- [T1 - Publicar runbook e checks da topologia](./TASK-1.md)

## Arquivos Reais Envolvidos

- `README.md`
- `bin/validate-host.sh`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-03-DOCUMENTACAO-E-VALIDACAO-OPERACIONAL.md)
- [Epic anterior](PROJETOS/OC-MISSION-CONTROL/F2-OPENROUTER-E-AGENTES/EPIC-F2-02-AUTOMACAO-HOST-SIDE-DO-BOOTSTRAP-OPENCLAW.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)

## Handoff para Revisao Pos-Issue

- resumo_execucao: o backlog foi reconciliado com o estado versionado atual; `README.md` e `bin/validate-host.sh` já cobrem o runbook operacional, a matriz tarefa -> agente e os checks automatizados da topologia
- base_commit: `nao_informado`
- target_commit: `worktree`
- evidencia: leitura direta de `README.md` e `bin/validate-host.sh`
- commits_execucao:
  - `c69f3172d067f471b34922459e2e442b18fd4a27`
- validacoes_executadas:
  - `rg -n 'planner|builder|auditor|OpenRouter|agents list --bindings|validate-host' README.md` -> ok
  - `rg -n 'has_planner_binding|has_openrouter_catalog|agent_ids|OPENCLAW_LOCAL_WORKSPACE_SYNC_ENABLED' bin/validate-host.sh` -> ok
- arquivos_de_codigo_relevantes:
  - `README.md`
  - `bin/validate-host.sh`
- limitacoes: reconciliacao documental baseada no worktree atual; nenhuma alteracao adicional de codigo foi necessaria para fechar o escopo declarado
