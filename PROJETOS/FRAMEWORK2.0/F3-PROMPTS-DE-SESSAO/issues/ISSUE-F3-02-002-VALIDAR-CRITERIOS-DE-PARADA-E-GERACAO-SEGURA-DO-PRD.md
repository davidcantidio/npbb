---
doc_id: "ISSUE-F3-02-002-VALIDAR-CRITERIOS-DE-PARADA-E-GERACAO-SEGURA-DO-PRD.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-02-002 - Validar criterios de parada e geracao segura do PRD

## User Story

Como mantenedor do framework, quero validar criterios de parada da sessao de
PRD para evitar geracao material sem insumo suficiente.

## Contexto Tecnico

Esta issue revisa `SESSION-CRIAR-PRD.md` com foco em guardrails de bloqueio,
confirmacao e seguranca documental.

## Plano TDD

- Red: identificar onde o prompt ainda poderia avancar sem insumo suficiente.
- Green: registrar criterios de parada e de geracao segura.
- Refactor: revisar linguagem para minimizar ambiguidade operacional.

## Criterios de Aceitacao

- Given a sessao de criacao de PRD, When faltar intake aprovado ou contexto
  minimo, Then o prompt manda parar explicitamente
- Given uma etapa de escrita, When o prompt for seguido, Then a confirmacao do
  PM e obrigatoria
- Given o fluxo completo, When for lido, Then fica claro o que pode e o que nao
  pode ser inferido

## Definition of Done da Issue

- [ ] criterios de parada explicitos
- [ ] regras de escrita segura registradas
- [ ] pontos de inferencia proibida revisados

## Tasks Decupadas

- [ ] T1: revisar lacunas de bloqueio no prompt
- [ ] T2: registrar criterios de parada e escrita segura
- [ ] T3: revisar clareza das proibicoes

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`
- `PROJETOS/COMUM/TEMPLATE-INTAKE.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`

## Dependencias

- [Issue 001](./ISSUE-F3-02-001-REDIGIR-SESSION-CRIAR-PRD-COM-PASSAGENS-HITL.md)
- [Epic](../EPIC-F3-02-SESSION-CRIAR-PRD.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
