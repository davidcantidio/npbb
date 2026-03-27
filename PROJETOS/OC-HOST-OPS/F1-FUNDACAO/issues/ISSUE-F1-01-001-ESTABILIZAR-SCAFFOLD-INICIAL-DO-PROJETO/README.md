---
doc_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Estabilizar scaffold inicial do projeto

## User Story

Como PM, quero validar o scaffold base do projeto para que o backlog real de host-side passe a usar PRD e wrappers atuais, sem ficar preso ao placeholder inicial.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: scaffold base reconciliado com o worktree atual.

## Contexto Tecnico

O intake do projeto ja descrevia a capacidade host-side real. Esta issue encerra a trilha bootstrap: substitui o PRD placeholder, atualiza wrappers e aprova a F1 como base documental antes do planning das fases operacionais.

## Plano TDD

- Red: apontar drift entre intake real, PRD placeholder e wrappers congelados na F1
- Green: atualizar PRD, wrappers e manifests para o backlog real do host-side
- Refactor: manter o bootstrap apenas como registro historico do arranque do projeto

## Criterios de Aceitacao

- [x] intake e PRD estao coerentes com o worktree atual
- [x] wrappers locais deixam explicito que o ponto atual e planning
- [x] fase F1, epic e issue bootstrap continuam rastreaveis
- [x] `SESSION-PLANEJAR-PROJETO.md` aponta para o backlog real do host-side
- [x] issue bootstrap possui `TASK-1.md` sincronizada

## Definition of Done da Issue

- [x] intake e PRD estao coerentes com o worktree atual
- [x] wrappers locais apontam para caminhos repo-relative do projeto
- [x] fase F1, epic e issue bootstrap existem
- [x] bootstrap deixa de competir com a fila real do projeto
- [x] issue bootstrap possui `TASK-1.md` completa

## Tasks

- [T1 - Validar o scaffold inicial](./TASK-1.md)

## Arquivos Reais Envolvidos

- `INTAKE-OC-HOST-OPS.md`
- `PRD-OC-HOST-OPS.md`
- `SESSION-MAPA.md`
- `SESSION-CRIAR-INTAKE.md`
- `SESSION-CRIAR-PRD.md`
- `SESSION-PLANEJAR-PROJETO.md`
- `SESSION-IMPLEMENTAR-ISSUE.md`
- `SESSION-REVISAR-ISSUE.md`
- `SESSION-AUDITAR-FASE.md`
- `F1-FUNDACAO/...`

## Handoff para Revisao Pos-Issue

- resumo_execucao: a auditoria do worktree atual encerrou o bootstrap documental; PRD placeholder e wrappers antigos foram reconciliados para liberar planning do backlog host-side real
- base_commit: `worktree`
- target_commit: `worktree`
- evidencia: leitura direta de `INTAKE-OC-HOST-OPS.md`, `PRD-OC-HOST-OPS.md` e wrappers locais atualizados
- commits_execucao:
  - `nao_aplicavel`
- validacoes_executadas:
  - `rg -n 'install|restore|launchd|dashboard|Telegram' PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md` -> ok
  - revisao documental de `PRD-OC-HOST-OPS.md` e wrappers locais -> ok
- arquivos_de_codigo_relevantes:
  - `PROJETOS/OC-HOST-OPS/INTAKE-OC-HOST-OPS.md`
  - `PROJETOS/OC-HOST-OPS/PRD-OC-HOST-OPS.md`
  - `PROJETOS/OC-HOST-OPS/SESSION-MAPA.md`
  - `PROJETOS/OC-HOST-OPS/SESSION-PLANEJAR-PROJETO.md`
- limitacoes: reconciliacao documental; a execucao das fases operacionais reais fica para o proximo ciclo de planning

## Dependencias

- [Epic](PROJETOS/OC-HOST-OPS/F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Fase](PROJETOS/OC-HOST-OPS/F1-FUNDACAO/F1_OC-HOST-OPS_EPICS.md)
- [PRD](PROJETOS/OC-HOST-OPS/PRD-OC-HOST-OPS.md)

## Navegacao Rapida

- [TASK-1](PROJETOS/OC-HOST-OPS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md)
