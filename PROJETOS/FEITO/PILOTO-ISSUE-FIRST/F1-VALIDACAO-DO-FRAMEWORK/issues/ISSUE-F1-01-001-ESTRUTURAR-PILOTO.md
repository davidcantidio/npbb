---
doc_id: "ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-01-001 - Estruturar Piloto

## User Story

Como responsavel pelo framework, quero um projeto piloto pequeno no padrao `issue-first` para validar a nova arvore documental sem depender de retrofit nos projetos existentes.

## Contexto Tecnico

Esta issue cobre a criacao da base documental do piloto: PRD, protocolo de decisao, fase, epico manifesto e estrutura de diretorios `issues/`, `sprints/` e `feito/`.

## Plano TDD

- Red: verificar se o piloto ainda nao oferece um caminho claro `PRD -> fase -> epico -> issue`.
- Green: criar os arquivos e os links minimos para habilitar essa navegacao.
- Refactor: revisar nomes, caminhos e status para manter consistencia com `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`.

## Criterios de Aceitacao

- Given o diretorio `PROJETOS/PILOTO-ISSUE-FIRST`, When o leitor abrir o projeto, Then encontra `PRD`, `DECISION-PROTOCOL`, `feito/` e a fase `F1-VALIDACAO-DO-FRAMEWORK`
- Given a fase F1, When o leitor abrir `F1_PILOTO_ISSUE_FIRST_EPICS.md`, Then encontra o epico `EPIC-F1-01` listado com link funcional
- Given o epico F1-01, When o leitor abrir `EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md`, Then encontra uma tabela indice apontando para duas issues em `issues/`

## Definition of Done da Issue

- [ ] projeto piloto criado na raiz de `PROJETOS/`
- [ ] estrutura basica do piloto navegavel por links Markdown
- [ ] manifesto do epico sem detalhamento redundante das issues

## Tarefas Decupadas

- [ ] T1: criar `PRD-PILOTO-ISSUE-FIRST.md` com objetivo, escopo e DoD do projeto
- [ ] T2: criar `DECISION-PROTOCOL.md` local do piloto
- [ ] T3: criar `F1_PILOTO_ISSUE_FIRST_EPICS.md` com gate, tabela de epicos e links
- [ ] T4: criar `EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md` com indice de issues
- [ ] T5: criar `feito/README.md` explicando a destinacao do diretorio

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/GOV-SCRUM.md`
- `PROJETOS/COMUM/GOV-ISSUE-FIRST.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/PRD-PILOTO-ISSUE-FIRST.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/F1_PILOTO_ISSUE_FIRST_EPICS.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md`

## Artifact Minimo

- `artifacts/projetos/piloto-issue-first/f1-structure-checklist.md`

## Dependencias

- [Epic](../EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md)
- [Fase](../F1_PILOTO_ISSUE_FIRST_EPICS.md)
- [PRD](../../PRD-PILOTO-ISSUE-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST]]`
- `[[../../PRD-PILOTO-ISSUE-FIRST]]`
