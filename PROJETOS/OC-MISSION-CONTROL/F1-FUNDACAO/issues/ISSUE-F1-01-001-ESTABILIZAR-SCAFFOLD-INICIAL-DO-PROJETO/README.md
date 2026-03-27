---
doc_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Estabilizar scaffold inicial do projeto

## User Story

Como PM, quero validar o scaffold inicial do projeto para que intake, PRD, sessoes e estrutura issue-first fiquem prontos sem preenchimento manual.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: scaffold inicial do projeto com documentos e wrappers preenchidos.

## Contexto Tecnico

O script `scripts/criar_projeto.py` gera a raiz do projeto, os docs canônicos, os wrappers locais, a fase F1-FUNDACAO, o epic inicial, a issue granularizada e o primeiro task file.

## Plano TDD

- Red: revisar a árvore gerada e identificar placeholders ou caminhos incorretos
- Green: corrigir qualquer drift de nomes, frontmatter ou links
- Refactor: simplificar os artefatos para manter o bootstrap enxuto e legível

## Criterios de Aceitacao

- [x] intake e PRD existem com `doc_id` e `project` preenchidos
- [x] wrappers locais apontam para caminhos repo-relative do projeto
- [x] fase F1, epic e issue bootstrap existem
- [x] `SESSION-PLANEJAR-PROJETO.md` traz `escopo`, `profundidade`, `task_mode` e `observacoes` preenchidos
- [x] issue bootstrap possui `TASK-1.md` completa

## Definition of Done da Issue

- [x] intake e PRD existem com `doc_id` e `project` preenchidos
- [x] wrappers locais apontam para caminhos repo-relative do projeto
- [x] fase F1, epic e issue bootstrap existem
- [x] `SESSION-PLANEJAR-PROJETO.md` traz `escopo`, `profundidade`, `task_mode` e `observacoes` preenchidos
- [x] issue bootstrap possui `TASK-1.md` completa

## Tasks

- [T1 - Validar o scaffold inicial](./TASK-1.md)

## Arquivos Reais Envolvidos

- `INTAKE-OC-MISSION-CONTROL.md`
- `PRD-OC-MISSION-CONTROL.md`
- `SESSION-PLANEJAR-PROJETO.md`
- `SESSION-CRIAR-INTAKE.md`
- `SESSION-CRIAR-PRD.md`
- `SESSION-IMPLEMENTAR-ISSUE.md`
- `SESSION-REVISAR-ISSUE.md`
- `SESSION-AUDITAR-FASE.md`
- `SESSION-REMEDIAR-HOLD.md`
- `SESSION-REFATORAR-MONOLITO.md`
- `F1-FUNDACAO/...`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Fase](PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/F1_OC-MISSION-CONTROL_EPICS.md)
- [PRD](PROJETOS/OC-MISSION-CONTROL/PRD-OC-MISSION-CONTROL.md)

## Navegacao Rapida

- [TASK-1](PROJETOS/OC-MISSION-CONTROL/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md)
