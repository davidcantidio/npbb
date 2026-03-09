---
doc_id: "EPIC-F3-03-SESSION-IMPLEMENTAR-ISSUE.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F3-03 - SESSION-IMPLEMENTAR-ISSUE

## Objetivo

Criar o prompt de sessao para execucao de issue especifica com confirmacoes por acao material.

## Resultado de Negocio Mensuravel

Issues de alto risco passam a poder ser executadas em chat com escopo fechado,
sem descoberta autonoma adicional.

## Contexto Arquitetural

- cria `SESSION-IMPLEMENTAR-ISSUE.md`
- depende de `SPEC-TASK-INSTRUCTIONS.md`

## Definition of Done do Epico

- [ ] sessao de execucao criada
- [ ] guardrails de leitura minima e escrita confirmada descritos

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-03-001 | Redigir SESSION-IMPLEMENTAR-ISSUE com leitura minima e escopo explicito | Criar o fluxo base de execucao guiada. | 3 | todo | [ISSUE-F3-03-001-REDIGIR-SESSION-IMPLEMENTAR-ISSUE-COM-LEITURA-MINIMA.md](./issues/ISSUE-F3-03-001-REDIGIR-SESSION-IMPLEMENTAR-ISSUE-COM-LEITURA-MINIMA.md) |
| ISSUE-F3-03-002 | Validar guardrails de execucao material e fechamento por DoD | Fechar os controles operacionais da sessao. | 2 | todo | [ISSUE-F3-03-002-VALIDAR-GUARDRAILS-DE-EXECUCAO-MATERIAL.md](./issues/ISSUE-F3-03-002-VALIDAR-GUARDRAILS-DE-EXECUCAO-MATERIAL.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/SESSION-IMPLEMENTAR-ISSUE.md`

## Dependencias

- [Fase](./F3_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
