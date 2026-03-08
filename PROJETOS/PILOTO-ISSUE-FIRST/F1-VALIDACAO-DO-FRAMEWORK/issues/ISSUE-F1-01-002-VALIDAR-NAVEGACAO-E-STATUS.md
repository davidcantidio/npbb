---
doc_id: "ISSUE-F1-01-002-VALIDAR-NAVEGACAO-E-STATUS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-01-002 - Validar Navegacao e Status

## User Story

Como operador do framework, quero validar navegacao e atualizacao de status no piloto para confirmar que a sprint referencia as issues sem voltar a concentrar o escopo executavel.

## Contexto Tecnico

Esta issue foca na camada de consulta: links Markdown, wikilinks qualificados, manifestos de sprint e coerencia entre status de fase, epico e issue.

## Plano TDD

- Red: identificar pontos de ambiguidade na consulta quando o leitor sai do epico para a sprint ou para a issue.
- Green: criar uma sprint com tabela de issues e links qualificados, sem duplicar criterios ou tarefas.
- Refactor: revisar nomes e status para garantir alinhamento com `SPRINT-LIMITS.md` e `WORK-ORDER-SPEC.md`.

## Criterios de Aceitacao

- Given o epico F1-01, When o leitor seguir o link da sprint, Then encontra apenas objetivo, capacidade, tabela de issues, riscos e encerramento
- Given a sprint `SPRINT-F1-01.md`, When o leitor abrir uma issue listada, Then encontra os criterios detalhados na issue e nao no arquivo da sprint
- Given os arquivos do piloto, When o leitor consultar a navegacao rapida, Then encontra wikilinks qualificados e nenhum wikilink curto ambiguo como `[[EPICS]]`

## Definition of Done da Issue

- [ ] sprint criada sem duplicar requisitos das issues
- [ ] links Markdown e wikilinks qualificados presentes e coerentes
- [ ] statuses iniciais do piloto alinhados ao modelo `todo`

## Tarefas Decupadas

- [ ] T1: criar `sprints/SPRINT-F1-01.md` com capacidade e tabela de issues
- [ ] T2: adicionar navegacao rapida coerente em fase, epico e sprint
- [ ] T3: revisar os status iniciais dos arquivos novos
- [ ] T4: confirmar que nenhum arquivo de sprint replica criterios ou tarefas detalhadas

## Arquivos Reais Envolvidos

- `PROJETOS/COMUM/SPRINT-LIMITS.md`
- `PROJETOS/COMUM/WORK-ORDER-SPEC.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/issues/ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md`
- `PROJETOS/PILOTO-ISSUE-FIRST/F1-VALIDACAO-DO-FRAMEWORK/sprints/SPRINT-F1-01.md`

## Artifact Minimo

- `artifacts/projetos/piloto-issue-first/f1-navigation-checklist.md`

## Dependencias

- [Epic](../EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST.md)
- [Fase](../F1_PILOTO_ISSUE_FIRST_EPICS.md)
- [PRD](../../PRD-PILOTO-ISSUE-FIRST.md)
- [Issue 001](./ISSUE-F1-01-001-ESTRUTURAR-PILOTO.md)

## Navegacao Rapida

- `[[../EPIC-F1-01-VALIDAR-FLUXO-ISSUE-FIRST]]`
- `[[./ISSUE-F1-01-001-ESTRUTURAR-PILOTO]]`
- `[[../../PRD-PILOTO-ISSUE-FIRST]]`
