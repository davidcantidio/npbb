---
doc_id: "EPIC-F3-02-SESSION-CRIAR-PRD.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-09"
---

# EPIC-F3-02 - SESSION-CRIAR-PRD

## Objetivo

Criar o prompt de sessao que transforma um intake aprovado em PRD com paradas
HITL antes de cada gravacao.

## Resultado de Negocio Mensuravel

O PM consegue gerar PRD em chat sem adaptar manualmente o prompt canonico.

## Contexto Arquitetural

- cria `SESSION-CRIAR-PRD.md`
- usa `PROMPT-INTAKE-PARA-PRD.md`

## Definition of Done do Epico

- [ ] sessao de PRD criada
- [ ] validacao do intake e gravacao estao separadas por confirmacao

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-02-001 | Redigir SESSION-CRIAR-PRD com passagens HITL | Criar o fluxo base do prompt. | 3 | todo | [ISSUE-F3-02-001-REDIGIR-SESSION-CRIAR-PRD-COM-PASSAGENS-HITL.md](./issues/ISSUE-F3-02-001-REDIGIR-SESSION-CRIAR-PRD-COM-PASSAGENS-HITL.md) |
| ISSUE-F3-02-002 | Validar criterios de parada e geracao segura do PRD | Completar os guardrails de gravacao e bloqueio. | 2 | todo | [ISSUE-F3-02-002-VALIDAR-CRITERIOS-DE-PARADA-E-GERACAO-SEGURA-DO-PRD.md](./issues/ISSUE-F3-02-002-VALIDAR-CRITERIOS-DE-PARADA-E-GERACAO-SEGURA-DO-PRD.md) |

## Artifact Minimo do Epico

- `PROJETOS/COMUM/SESSION-CRIAR-PRD.md`

## Dependencias

- [Fase](./F3_FRAMEWORK2_0_EPICS.md)
- [Epic Dependente](./EPIC-F3-01-REGISTRO-E-VALIDACAO-DOS-PROMPTS-ANTECIPADOS.md)
