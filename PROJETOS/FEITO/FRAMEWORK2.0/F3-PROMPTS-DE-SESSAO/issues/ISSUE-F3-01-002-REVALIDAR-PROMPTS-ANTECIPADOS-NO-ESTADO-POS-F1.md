---
doc_id: "ISSUE-F3-01-002-REVALIDAR-PROMPTS-ANTECIPADOS-NO-ESTADO-POS-F1.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-002 - Revalidar prompts antecipados no estado pos-F1

## User Story

Como mantenedor do framework, quero revisar os prompts de sessao ja criados
apos a renomeacao para evitar drift entre o inventario e o conteudo real.

## Contexto Tecnico

Os prompts antecipados foram ajustados durante `F1`, mas esta issue fecha a
verificacao de consistencia em estado pos-renomeacao.

## Plano TDD

- Red: procurar referencias antigas ou inconsistencias nos prompts existentes.
- Green: alinhar os prompts ao namespace final.
- Refactor: revisar coerencia com `SESSION-MAPA.md`.

## Criterios de Aceitacao

- Given os prompts de sessao antecipados, When forem revisados, Then nao restam
  referencias normativas aos nomes antigos
- Given `SESSION-MAPA.md`, When for comparado aos prompts reais, Then o status
  e a lista estao coerentes
- Given o estado pos-F1, When um PM usar os prompts existentes, Then o fluxo de
  leitura esta consistente com a governanca nova

## Definition of Done da Issue

- [ ] prompts antecipados revisados no estado final de F1
- [ ] referencias normativas antigas removidas
- [ ] mapa e artefatos reais coerentes

## Tasks Decupadas

- [ ] T1: revisar prompts de sessao ja criados
- [ ] T2: corrigir residuos de nomenclatura antiga
- [ ] T3: comparar artefatos com `SESSION-MAPA.md`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-CRIAR-INTAKE.md`
- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/COMUM/SESSION-MAPA.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-MAPA.md`

## Dependencias

- [Issue 001](./ISSUE-F3-01-001-FORMALIZAR-SESSION-MAPA-COM-INVENTARIO-E-STATUS-CORRETOS.md)
- [Epic](../EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
- [Fase](../F3_FRAMEWORK2_0_EPICS.md)
- [PRD](../../PRD-FRAMEWORK2.0.md)
