---
doc_id: "EPIC-F4-04-Sincronizacao-de-Estado-e-Notificacao-HITL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F4-04 - Sincronizacao de Estado e Notificacao HITL

## Objetivo

Sincronizar a cascata issue epic fase sprint apos execucao e review e expor proxima acao nos gates obrigatorios.

## Resultado de Negocio Mensuravel

O PM passa a ver estado derivado consistente e o sistema deixa explicita a proxima decisao humana necessaria.

## Contexto Arquitetural

Sem sincronizacao de estado e proxima acao visivel o modulo perderia o valor operacional do fluxo hierarquico e dos gates HITL.

## Definition of Done do Epico
- [ ] cascata de status atualizada apos execucao e review
- [ ] reabertura por follow-up local tratada sem drift
- [ ] proxima acao e notificacoes de gate visiveis ao PM

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-04-001 | Sincronizar cascata documental e persistida apos execucao | Cascata `issue -> epic -> fase -> sprint` sincronizada apos execucao e review. | 2 | todo | [ISSUE-F4-04-001-Sincronizar-cascata-documental-e-persistida-apos-execucao](./issues/ISSUE-F4-04-001-Sincronizar-cascata-documental-e-persistida-apos-execucao/) |
| ISSUE-F4-04-002 | Notificar PM e expor proxima acao nos gates obrigatorios | Proxima acao e eventos de gate visiveis ao PM em backend e frontend. | 1 | todo | [ISSUE-F4-04-002-Notificar-PM-e-expor-proxima-acao-nos-gates-obrigatorios](./issues/ISSUE-F4-04-002-Notificar-PM-e-expor-proxima-acao-nos-gates-obrigatorios/) |

## Artifact Minimo do Epico

Cascata de estado coerente e proxima acao visivel.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F4_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F4-02
- EPIC-F4-03
