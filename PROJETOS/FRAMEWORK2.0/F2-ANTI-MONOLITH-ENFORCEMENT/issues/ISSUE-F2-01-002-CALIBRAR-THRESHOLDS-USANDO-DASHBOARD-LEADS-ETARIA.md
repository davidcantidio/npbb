---
doc_id: "ISSUE-F2-01-002-CALIBRAR-THRESHOLDS-USANDO-DASHBOARD-LEADS-ETARIA.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-002 - Calibrar thresholds usando dashboard leads etaria

## User Story

Como mantenedor do framework, quero calibrar o spec com um projeto ativo para
evitar thresholds arbitrarios ou inviaveis.

## Contexto Tecnico

O PRD aponta `dashboard-leads-etaria` como referencia de calibracao. Esta issue
usa medidas reais do projeto para justificar a primeira versao do spec.

## Plano TDD

- Red: medir arquivos e funcoes relevantes no projeto de referencia.
- Green: registrar os achados de calibracao no spec.
- Refactor: revisar se os thresholds continuam discriminando monolito real.

## Criterios de Aceitacao

- Given o projeto `dashboard-leads-etaria`, When a calibracao for concluida,
  Then os thresholds do spec possuem referencia empirica documentada
- Given o spec anti-monolito, When for lido, Then fica claro de onde sairam os
  valores iniciais
- Given a calibracao minima, When o auditor usar o spec, Then ele entende que
  os valores sao operacionais e nao hipoteticos

## Definition of Done da Issue

- [x] amostra minima do projeto de referencia analisada
- [x] nota de calibracao registrada no spec
- [x] thresholds revisados se necessario

## Tasks Decupadas

- [x] T1: identificar arquivos/funcoes representativos no projeto de referencia
- [x] T2: comparar medidas observadas com os thresholds propostos
- [x] T3: registrar a calibracao no `SPEC-ANTI-MONOLITO.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`
- `PROJETOS/dashboard-leads-etaria/`

## Artifact Minimo

- `PROJETOS/COMUM/SPEC-ANTI-MONOLITO.md`

## Dependencias

- [Issue 001](./ISSUE-F2-01-001-DEFINIR-THRESHOLDS-ANTI-MONOLITO-POR-LINGUAGEM.md)
- [Epic](../EPIC-F2-01-SPEC-ANTI-MONOLITO.md)
- [Fase](../F2_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
