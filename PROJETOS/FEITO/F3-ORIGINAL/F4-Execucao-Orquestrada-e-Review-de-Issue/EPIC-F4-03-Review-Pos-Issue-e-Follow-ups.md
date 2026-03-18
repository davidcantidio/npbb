---
doc_id: "EPIC-F4-03-Review-Pos-Issue-e-Follow-ups.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F4-03 - Review Pos-Issue e Follow-ups

## Objetivo

Registrar review pos-issue com veredito canonico e materializar follow-ups rastreaveis quando necessario.

## Resultado de Negocio Mensuravel

Cada issue concluida passa por review formal antes de realmente fechar a cadeia operacional.

## Contexto Arquitetural

O modulo precisa separar execucao de review e abrir remediacao com o destino correto quando a issue nao puder ser encerrada diretamente.

## Definition of Done do Epico
- [ ] review pos-issue disponivel por API e UI
- [ ] vereditos canonicos persistidos de forma rastreavel
- [ ] follow-ups nascem como issue local ou new intake conforme o caso

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-03-001 | Preparar e registrar review pos issue com veredito canonico | Review pos-issue disponivel com veredito canonico em backend e frontend. | 2 | todo | [ISSUE-F4-03-001-Preparar-e-registrar-review-pos-issue-com-veredito-canonico](./issues/ISSUE-F4-03-001-Preparar-e-registrar-review-pos-issue-com-veredito-canonico/) |
| ISSUE-F4-03-002 | Materializar follow up de review como issue local ou new intake | Follow-up pos-review nasce no artefato correto com rastreabilidade explicita. | 1 | todo | [ISSUE-F4-03-002-Materializar-follow-up-de-review-como-issue-local-ou-new-intake](./issues/ISSUE-F4-03-002-Materializar-follow-up-de-review-como-issue-local-ou-new-intake/) |

## Artifact Minimo do Epico

Review pos-issue operavel e follow-up rastreavel.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F4_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F4-02
