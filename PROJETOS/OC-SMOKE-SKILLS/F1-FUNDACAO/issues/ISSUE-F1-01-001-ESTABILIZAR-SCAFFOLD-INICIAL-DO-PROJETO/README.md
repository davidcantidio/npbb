---
doc_id: "ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO"
version: "1.1"
status: "todo"
owner: "PM"
last_updated: "2026-03-23"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-01-001 - Estabilizar scaffold inicial do projeto

## User Story

Como mantenedor do framework, quero validar o projeto-canario para que a suite `openclaw-*` continue obedecendo o fluxo issue-first e o guia de smoke atual.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: canario do framework com docs, wrappers e smoke atualizados.

## Contexto Tecnico

Esta issue nao valida um produto de negocio. Ela usa `GUIA-TESTE-SKILLS.md`, os wrappers locais e `./bin/check-openclaw-smoke.sh` para provar que o framework atual continua encontrando a unidade correta e respeitando os gates documentais.

## Plano TDD

- Red: demonstrar drift entre guia, wrappers e backlog bootstrap do canario
- Green: alinhar docs e wrappers ao framework atual e executar o smoke minimo
- Refactor: manter o canario pequeno e focado em detectar regressao do framework

## Criterios de Aceitacao

- [ ] intake, PRD e `GUIA-TESTE-SKILLS.md` descrevem o mesmo escopo canario
- [ ] wrappers locais apontam para a issue e a fase corretas do canario
- [ ] `SESSION-MAPA.md` deixa explicito que o projeto e canario, nao backlog principal
- [ ] `./bin/check-openclaw-smoke.sh` e citado como validacao minima do framework
- [ ] issue bootstrap possui `TASK-1.md` coerente com esse papel de prova controlada

## Definition of Done da Issue

- [ ] intake, PRD e guia do canario estao alinhados
- [ ] wrappers locais apontam para caminhos repo-relative do projeto
- [ ] fase F1, epic e issue bootstrap existem
- [ ] wrappers de execucao/revisao/auditoria refletem o canario atual
- [ ] issue bootstrap possui `TASK-1.md` completa

## Tasks

- [T1 - Validar o canario do framework](./TASK-1.md)

## Arquivos Reais Envolvidos

- `INTAKE-OC-SMOKE-SKILLS.md`
- `PRD-OC-SMOKE-SKILLS.md`
- `GUIA-TESTE-SKILLS.md`
- `SESSION-MAPA.md`
- `SESSION-PLANEJAR-PROJETO.md`
- `SESSION-IMPLEMENTAR-ISSUE.md`
- `SESSION-REVISAR-ISSUE.md`
- `SESSION-AUDITAR-FASE.md`
- `F1-FUNDACAO/...`

## Artifact Minimo

- `README.md`
- `TASK-1.md`

## Dependencias

- [Epic](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/EPIC-F1-01-FUNDACAO-DO-PROJETO.md)
- [Fase](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/F1_OC-SMOKE-SKILLS_EPICS.md)
- [PRD](PROJETOS/OC-SMOKE-SKILLS/PRD-OC-SMOKE-SKILLS.md)
- [Guia](PROJETOS/OC-SMOKE-SKILLS/GUIA-TESTE-SKILLS.md)

## Navegacao Rapida

- [TASK-1](PROJETOS/OC-SMOKE-SKILLS/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/TASK-1.md)
