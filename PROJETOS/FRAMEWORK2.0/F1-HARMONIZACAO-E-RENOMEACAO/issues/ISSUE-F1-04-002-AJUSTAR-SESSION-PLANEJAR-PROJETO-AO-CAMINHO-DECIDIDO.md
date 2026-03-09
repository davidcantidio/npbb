---
doc_id: "ISSUE-F1-04-002-AJUSTAR-SESSION-PLANEJAR-PROJETO-AO-CAMINHO-DECIDIDO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
task_instruction_mode: "optional"
decision_refs:
  - "dec-2026-03-09-001"
---

# ISSUE-F1-04-002 - Ajustar SESSION-PLANEJAR-PROJETO ao caminho decidido

## User Story

Como PM, quero a sessao de planejamento apontando para a referencia correta para
executar planejamento em chat sem adaptacao manual.

## Contexto Tecnico

Esta issue consome a decisao registrada na issue anterior e atualiza
`SESSION-PLANEJAR-PROJETO.md` para apontar para `PROMPT-PLANEJAR-FASE.md`.

## Plano TDD

- Red: localizar referencias antigas ou ambiguas na sessao de planejamento.
- Green: alinhar a sessao ao prompt decidido.
- Refactor: revisar exemplos e parametros.

## Criterios de Aceitacao

- Given `SESSION-PLANEJAR-PROJETO.md`, When for lido, Then ele aponta para `PROMPT-PLANEJAR-FASE.md`
- Given a sessao atualizada, When o PM preencher seus parametros, Then o caminho de planejamento esta coerente com a decisao registrada

## Definition of Done da Issue

- [ ] sessao de planejamento alinhada a decisao
- [ ] exemplos e parametros revisados

## Tasks Decupadas

- [ ] T1: revisar a referencia atual da sessao
- [ ] T2: atualizar a sessao para o caminho decidido
- [ ] T3: revisar exemplos e prompt local de `FRAMEWORK2.0`

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`
- `PROJETOS/FRAMEWORK2.0/SESSION-PLANEJAR-PROJETO-Projeto-completo.md`

## Artifact Minimo

- `PROJETOS/COMUM/SESSION-PLANEJAR-PROJETO.md`

## Dependencias

- [Issue 001](./ISSUE-F1-04-001-AVALIAR-PROMPT-PLANEJAR-FASE-E-REGISTRAR-DECISAO.md)
- [Epic](../EPIC-F1-04-INTEGRACAO-DE-PROMPT-PLANEJAR-FASE.md)
- [Fase](../F1_FRAMEWORK2_0_EPICS.md)
