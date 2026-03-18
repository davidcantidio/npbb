---
doc_id: "EPIC-F2-03-Modulo-Admin-Integrado-ao-Dashboard.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F2-03 - Modulo Admin Integrado ao Dashboard

## Objetivo

Entregar a superficie administrativa do FRAMEWORK3 no dashboard NPBB com acesso protegido navegacao edicao e timeline.

## Resultado de Negocio Mensuravel

O PM consegue operar o backlog do FRAMEWORK3 pela UI sem recorrer ao filesystem como unica interface.

## Contexto Arquitetural

O dashboard existente ja possui autenticacao e roteamento. Este epic adiciona o modulo Framework apoiado pelos endpoints da fase.

## Definition of Done do Epico
- [ ] shell admin protegido disponivel no frontend
- [ ] navegacao hierarquica e edicao de artefatos funcionando
- [ ] timeline de execucoes aprovacoes e proxima acao visivel

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-03-001 | Implantar shell admin e guardas de acesso do modulo Framework | Entrada protegida do modulo Framework disponivel no dashboard. | 2 | todo | [ISSUE-F2-03-001-Implantar-shell-admin-e-guardas-de-acesso-do-modulo-Framework](./issues/ISSUE-F2-03-001-Implantar-shell-admin-e-guardas-de-acesso-do-modulo-Framework/) |
| ISSUE-F2-03-002 | Entregar navegacao hierarquica e edicao de artefatos | Hierarquia completa navegavel e artefatos persistidos editaveis no modulo admin. | 2 | todo | [ISSUE-F2-03-002-Entregar-navegacao-hierarquica-e-edicao-de-artefatos](./issues/ISSUE-F2-03-002-Entregar-navegacao-hierarquica-e-edicao-de-artefatos/) |
| ISSUE-F2-03-003 | Expor timeline de execucoes aprovacoes e proxima acao | Historico operacional e painel de proxima acao visiveis ao PM. | 1 | todo | [ISSUE-F2-03-003-Expor-timeline-de-execucoes-aprovacoes-e-proxima-acao](./issues/ISSUE-F2-03-003-Expor-timeline-de-execucoes-aprovacoes-e-proxima-acao/) |

## Artifact Minimo do Epico

Entrada administrativa do FRAMEWORK3 integrada ao dashboard.

## Dependencias
- [Intake](../INTAKE-FRAMEWORK3.md)
- [PRD](../PRD-FRAMEWORK3.md)
- [Fase](./F2_FRAMEWORK3_EPICS.md)
- dependencias operacionais:
- EPIC-F2-01
- EPIC-F2-02
