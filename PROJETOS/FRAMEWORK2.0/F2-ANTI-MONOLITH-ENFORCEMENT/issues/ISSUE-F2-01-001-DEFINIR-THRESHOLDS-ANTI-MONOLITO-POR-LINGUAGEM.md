---
doc_id: "ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-001 - Definir thresholds anti-monolito por linguagem

## User Story

Como auditor do framework, quero thresholds objetivos por linguagem para abrir
achados de monolito com criterio repetivel.

## Contexto Tecnico

Esta issue inaugura `SPEC-ANTI-MONOLITO.md` como fonte canonica para
`monolithic-file` e `monolithic-function` em TypeScript/React e Python.

## Plano TDD

- Red: listar as dimensoes de complexidade que hoje ainda estao implicitas.
- Green: registrar thresholds operacionais e linguagem alvo no spec.
- Refactor: revisar a clareza dos nomes, unidades e niveis `warn` e `block`.

## Criterios de Aceitacao

- Given o spec anti-monolito, When for lido, Then existem thresholds separados
  por dimensao estrutural
- Given TypeScript/React e Python como linguagens alvo, When o spec for lido,
  Then fica explicito que os thresholds cobrem ambas
- Given um auditor, When consultar o spec, Then consegue distinguir `warn` de
  `block` sem inferencia adicional

## Definition of Done da Issue

- [ ] thresholds definidos por dimensao estrutural
- [ ] linguagens cobertas declaradas
- [ ] sem criterio subjetivo residual no spec

## Tasks Decupadas

- [ ] T1: definir dimensoes estruturais obrigatorias do spec
- [ ] T2: registrar thresholds `warn` e `block`
- [ ] T3: revisar legibilidade e operacionalidade do texto

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Artifact Minimo

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Dependencias

- [Epic](../EPIC-F2-01-SPEC-ANTI-MONOLITO.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
