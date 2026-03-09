---
doc_id: "ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs:
  - "dec-2026-03-09-001"
---

# ISSUE-F1-04-001 - Avaliar PROMPT-PLANEJAR-FASE e registrar decisao

## User Story

Como mantenedor do framework, quero decidir o papel de `PROMPT-PLANEJAR-FASE.md`
para nao deixar `SESSION-PLANEJAR-PROJETO` apontando para um artefato ambiguo.

## Contexto Tecnico

O PRD exige uma decisao estrutural. O resultado aprovado foi manter o prompt
como artefato complementar e registrar isso em `GOV-DECISOES.md`.

## Plano TDD

- Red: comparar a funcao do prompt com a sessao de planejamento.
- Green: registrar a decisao em `GOV-DECISOES.md`.
- Refactor: revisar se a decisao e rastreavel dos prompts consumidores.

## Criterios de Aceitacao

- Given `PROMPT-PLANEJAR-FASE.md`, When sua funcao for comparada ao fluxo de sessao, Then a decisao fica explicita em `GOV-DECISOES.md`
- Given a decisao registrada, When ela for lida, Then fica claro que o prompt e complementar e nao depreciado

## Definition of Done da Issue

- [ ] decisao registrada
- [ ] rastreabilidade para o prompt consumidor preservada

## Tasks Decupadas

- [ ] T1: revisar o papel do prompt de planejamento
- [ ] T2: registrar a decisao em `GOV-DECISOES.md`
- [ ] T3: revisar a rastreabilidade resultante

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/PROMPT-PLANEJAR-FASE.md`
- `PROJETOS/COMUM/GOV-DECISOES.md`

## Artifact Minimo

- `PROJETOS/COMUM/GOV-DECISOES.md`

## Dependencias

- [Epic](../EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
