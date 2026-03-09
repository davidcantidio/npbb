---
doc_id: "ISSUE-F3-01-001-FORMALIZAR-SESSION-MAPA-COM-INVENTARIO-E-STATUS-CORRETOS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-001 - Formalizar SESSION-MAPA com inventario e status corretos

## User Story

Como operador do framework, quero um mapa canonico dos prompts de sessao para
entender qual artefato usar em cada etapa do fluxo.

## Contexto Tecnico

Esta issue consolida `SESSION-MAPA.md` como inventario oficial dos prompts de
sessao, com nomenclatura final, status e finalidade.

## Plano TDD

- Red: localizar o inventario parcial ou com nomes desatualizados.
- Green: registrar o conjunto final de prompts de sessao no mapa.
- Refactor: revisar se a taxonomia separa sessao de prompt autonomo.

## Criterios de Aceitacao

- Given `SESSION-MAPA.md`, When for lido, Then todos os prompts de sessao
  previstos no plano estao listados
- Given o inventario, When for consultado, Then cada prompt tem status e papel
  claros
- Given a convencao final de nomes, When o mapa for lido, Then nao ha aliases
  antigos como nomes canonicos

## Definition of Done da Issue

- [ ] inventario final de prompts de sessao listado
- [ ] status e papel de cada prompt descritos
- [ ] nomes canonicos revisados

## Tasks Decupadas

- [ ] T1: revisar o inventario de prompts de sessao previstos
- [ ] T2: atualizar `SESSION-MAPA.md` com nomes e status corretos
- [ ] T3: revisar coerencia entre mapa e artefatos reais

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Dependencias

- [Epic](../EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
