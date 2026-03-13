---
doc_id: "EPIC-F2-01-Layout-Side-by-Side.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F2-01 - Layout Side-by-Side

## Objetivo

Converter o layout das 5 paginas do wizard para duas colunas fixas (configuracao a esquerda, contexto a direita) e implementar tratamento de breakpoint para viewports menores.

## Resultado de Negocio Mensuravel

Operador visualiza painel de configuracao a esquerda e conteudo contextual a direita em todas as etapas; layout colapsa adequadamente em tablets e mobile.

## Contexto Arquitetural

As 5 paginas (EventWizardPage, EventLeadFormConfig, EventGamificacao, EventAtivacoes, EventQuestionario) possuem estruturas distintas. O resultado da F1 deve informar componentes e conteudo da coluna direita. Pode ser necessario extrair componente de layout compartilhado.

## Definition of Done do Epico
- [ ] Layout de duas colunas em todas as 5 etapas
- [ ] Breakpoint implementado (colapso para coluna unica conforme F1)
- [ ] Padrao visual consistente (respiro, fontes, espacamentos)

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Converter Layout para Duas Colunas | Aplicar layout side-by-side em todas as 5 etapas | 3 | todo | [ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md](./issues/ISSUE-F2-01-001-Converter-Layout-Duas-Colunas.md) |
| ISSUE-F2-01-002 | Implementar Breakpoint para Viewports Menores | Colapso para coluna unica abaixo do breakpoint | 2 | todo | [ISSUE-F2-01-002-Implementar-Breakpoint-Viewports-Menores.md](./issues/ISSUE-F2-01-002-Implementar-Breakpoint-Viewports-Menores.md) |

## Artifact Minimo do Epico

Layout side-by-side funcional em todas as etapas; breakpoint funcional.

## Dependencias
- [Intake](../../INTAKE-UX.md)
- [PRD](../../PRD-UX.md)
- [Fase](./F2_UX_EPICS.md)
- [F1](../../F1-Discovery-Tecnico/F1_UX_EPICS.md) — concluida
