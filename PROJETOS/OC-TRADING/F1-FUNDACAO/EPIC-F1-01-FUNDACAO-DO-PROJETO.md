---
doc_id: "EPIC-F1-01-FUNDACAO-DO-PROJETO.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-23"
---

# EPIC-F1-01 - Fundacao do projeto

## Objetivo

Reconciliar o scaffold base do projeto com o backlog real da vertical Trading.

## Resultado de Negocio Mensuravel

O bootstrap deixa de competir com o backlog principal e a vertical passa a apontar para planning do risco real.

## Feature de Origem

- **Feature**: Feature 1
- **Comportamento coberto**: scaffold base validado e PRD/wrappers alinhados ao worktree atual.

## Contexto Arquitetural

- intake real ja existia e foi preservado
- PRD placeholder foi substituido por backlog Trading real
- wrappers locais deixaram de apontar para a issue bootstrap como fila principal

## Definition of Done do Epico

- [x] intake e PRD estao coerentes com o worktree atual
- [x] wrappers de sessao estao completos
- [x] fase F1, epico, issue e task existem
- [x] audit log aponta para o bootstrap aprovado

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento | Feature |
|---|---|---|---|---|---|---|
| ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO | Estabilizar scaffold inicial do projeto | Validar o scaffold base e liberar o backlog real da vertical. | 3 | done | [ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO](PROJETOS/OC-TRADING/F1-FUNDACAO/issues/ISSUE-F1-01-001-ESTABILIZAR-SCAFFOLD-INICIAL-DO-PROJETO) | Feature 1 |

## Artifact Minimo do Epico

- `README.md` da issue bootstrap
- `TASK-1.md`
- `F1_OC-TRADING_EPICS.md`

## Dependencias

- [Intake](PROJETOS/OC-TRADING/INTAKE-OC-TRADING.md)
- [PRD](PROJETOS/OC-TRADING/PRD-OC-TRADING.md)
- [Fase](PROJETOS/OC-TRADING/F1-FUNDACAO/F1_OC-TRADING_EPICS.md)
