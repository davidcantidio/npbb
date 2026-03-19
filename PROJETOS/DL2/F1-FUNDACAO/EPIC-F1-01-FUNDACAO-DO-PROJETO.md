---
doc_id: "EPIC-F1-01-FUNDACAO-DO-PROJETO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-19"
---

# EPIC-F1-01 - Fundacao do projeto

## Objetivo

Estabilizar o projeto novo com docs canônicos, wrappers e um primeiro issue granularizado.

## Resultado de Negocio Mensuravel

O PM consegue iniciar o planejamento e materializar `F2/F3/F4` sem reconstruir manualmente o bootstrap documental do projeto.

## Feature de Origem

- **Feature**: nao_aplicavel
- **Comportamento coberto**: bootstrap estrutural do projeto, anterior ao eixo de valor do PRD.

## Contexto Arquitetural

- raiz do projeto pronta para fases futuras
- wrappers locais apontando para caminhos repo-relative
- issue granularizada inicial para validar o bootstrap
- fase preservada como base historica enquanto as features de negocio passam a viver em `F2/F3/F4`

## Definition of Done do Epico

- [ ] intake e PRD existem com frontmatter preenchido
- [ ] wrappers de sessao estao completos
- [ ] fase F1, epico, issue e task existem
- [ ] audit log aponta para o bootstrap inicial

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Estabilizar scaffold inicial do projeto | Validar e ajustar o bootstrap canonico do projeto. | 3 | todo | [README](./issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO/README.md) | nao_aplicavel |

## Artifact Minimo do Epico

- `README.md` da issue bootstrap
- `TASK-1.md`
- `F1_DL2_EPICS.md`

## Dependencias

- [Intake](../INTAKE-DL2.md)
- [PRD](../PRD-DL2.md)
- [Fase](./F1_DL2_EPICS.md)
