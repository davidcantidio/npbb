---
doc_id: "EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# EPIC-F1-01 - Validar Fluxo Issue-First

## Objetivo

Demonstrar, em um projeto novo e pequeno, que o framework atualizado permite navegar e executar trabalho no nivel de issue sem depender de um epico detalhado demais.

## Resultado de Negocio Mensuravel

Um leitor ou agente consegue identificar rapidamente o escopo da proxima issue, seus criterios e suas dependencias, sem precisar reler um bloco longo com todas as outras issues do epico.

## Contexto Arquitetural

- projeto documental em `PROJETOS/PILOTO-ISSUE-FIRST/`
- fase unica de validacao em `F1-VALIDACAO-DO-FRAMEWORK/`
- manifesto do epico neste arquivo
- detalhamento executavel em `issues/ISSUE-*.md`
- consolidacao temporal em `sprints/SPRINT-F1-01.md`

## Definition of Done do Epico

- [ ] o epico contem apenas contexto, DoD, dependencias e indice das issues
- [ ] os criterios detalhados vivem apenas nos arquivos de issue
- [ ] a sprint aponta para as issues sem duplicar criterios
- [ ] os links Markdown e wikilinks qualificados permitem consulta fluida

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Estruturar Piloto | Criar a arvore documental minima do piloto `issue-first`. | 3 | todo | [ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md](./issues/ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md) |
| ISSUE-F1-01-002 | Validar Navegacao e Status | Comprovar navegacao, rastreabilidade e uso correto de status e sprint. | 2 | todo | [ISSUE-F1-01-002-VALIDAR-NAVEGACAO-E-STATUS.md](./issues/ISSUE-F1-01-002-VALIDAR-NAVEGACAO-E-STATUS.md) |

## Artifact Minimo do Epico

- `artifacts/projetos/piloto-issue-first/f1-validation-summary.md`

## Dependencias

- [PRD](../PRD-PILOTO-ISSUE-FIRST.md)
- [Fase](./F1_PILOTO_ISSUE_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F1-01-001-ESTRUTURAR-PILOTO]]`
- `[[./issues/ISSUE-F1-01-002-VALIDAR-NAVEGACAO-E-STATUS]]`
- `[[../PRD-PILOTO-ISSUE-FIRST]]`
