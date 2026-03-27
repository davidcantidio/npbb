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

Como PM, quero validar o scaffold base da vertical para que o backlog real de Trading passe a usar PRD e wrappers atuais, sem ficar preso ao placeholder inicial.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: scaffold base reconciliado com o worktree atual.

## Contexto Tecnico

O intake do projeto ja descrevia a vertical Trading real. Esta issue encerra a trilha bootstrap: substitui o PRD placeholder, atualiza wrappers e aprova a F1 como base documental antes do planning das fases de risco, validator e gateway.

## Plano TDD

- Red: apontar drift entre intake real, PRD placeholder e wrappers congelados na F1
- Green: atualizar PRD, wrappers e manifests para o backlog real da vertical
- Refactor: manter o bootstrap apenas como registro historico do arranque do projeto

## Criterios de Aceitacao

- [x] intake e PRD estao coerentes com o worktree atual
- [x] wrappers locais deixam explicito que o ponto atual e planning
- [x] fase F1, epic e issue bootstrap continuam rastreaveis
- [x] `SESSION-PLANEJAR-PROJETO.md` aponta para o backlog real da vertical
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

- `INTAKE-OC-TRADING.md`
- `PRD-OC-TRADING.md`
- `SESSION-MAPA.md`
- `SESSION-CRIAR-INTAKE.md`
- `SESSION-CRIAR-PRD.md`
- `SESSION-PLANEJAR-PROJETO.md`
- `SESSION-IMPLEMENTAR-ISSUE.md`
- `SESSION-REVISAR-ISSUE.md`
- `SESSION-AUDITAR-FASE.md`
- `F1-FUNDACAO/...`

## Handoff para Revisao Pos-Issue

- resumo_execucao: a auditoria do worktree atual encerrou o bootstrap documental; PRD placeholder e wrappers antigos foram reconciliados para liberar planning da vertical Trading real
- base_commit: `worktree`
- target_commit: `worktree`
- evidencia: leitura direta de `INTAKE-OC-TRADING.md`, `PRD-OC-TRADING.md` e wrappers locais atualizados
- commits_execucao:
  - `nao_aplicavel`
- validacoes_executadas:
  - `rg -n 'signal_intent|validator|execution_gateway|TRADING_BLOCKED' PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md` -> ok
  - revisao documental de `PRD-OC-TRADING.md` e wrappers locais -> ok
- arquivos_de_codigo_relevantes:
  - `PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md`
  - `PROJETOS/OC-TRADING/PRD-OC-TRADING.md`
  - `PROJETOS/OC-TRADING/SESSION-MAPA.md`
  - `PROJETOS/OC-TRADING/SESSION-PLANEJAR-PROJETO.md`
- limitacoes: reconciliacao documental; a execucao das fases reais de Trading fica para o proximo ciclo de planning

## Dependencias

- [Epic](PROJETOS/OC-TRADING/F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Fase](PROJETOS/OC-TRADING/F1-FUNDACAO/F1_OC-TRADING_EPICS.md)
- [PRD](PROJETOS/OC-TRADING/PRD-OC-TRADING.md)

## Navegacao Rapida

- [TASK-1](PROJETOS/OC-TRADING/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md)
