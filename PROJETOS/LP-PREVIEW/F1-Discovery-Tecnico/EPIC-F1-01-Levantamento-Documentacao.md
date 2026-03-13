---
doc_id: "EPIC-F1-01-Levantamento-Documentacao.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-13"
---

# EPIC-F1-01 - Levantamento e Documentacao

## Objetivo

Mapear componentes de preview, estrutura de layout atual e compartilhamento entre contextos (leads e landing page). Validar largura-alvo 390px com design e documentar decisao de arquitetura.

## Resultado de Negocio Mensuravel

Lacunas tecnicas do PRD resolvidas, permitindo implementacao segura na F2 sem retrabalho por falta de informacao.

## Contexto Arquitetural

- Codebase possui `EventLeadFormConfigPage`, `PreviewSection`, `LandingPageView`, `useLandingPreview`
- Preview hoje intercalado em faixa horizontal (stack de secoes)
- PRD indica dois contextos (leads e landing page); F1 deve confirmar se sao o mesmo fluxo ou distintos

## Definition of Done do Epico
- [x] Componentes de preview identificados e documentados
- [x] Estrutura de layout atual documentada
- [x] Decisao sobre compartilhamento registrada
- [x] 390px validado com design
- [x] Issues filhas concluidas

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Mapear componentes de preview e estrutura de layout | Identificar nomes, estrutura CSS, compartilhamento | 3 | done | [ISSUE-F1-01-001-Mapear-Componentes-Layout.md](./issues/ISSUE-F1-01-001-Mapear-Componentes-Layout.md) |
| ISSUE-F1-01-002 | Documentar decisao de arquitetura e validar 390px | Registrar decisao e validacao com design | 2 | done | [ISSUE-F1-01-002-Documentar-Arquitetura-Validar-390px.md](./issues/ISSUE-F1-01-002-Documentar-Arquitetura-Validar-390px.md) |

## Artifact Minimo do Epico

- Documento ou secao na issue com mapeamento de componentes, layout e decisao
- Evidencia de validacao 390px com design

## Dependencias
- [Intake](../INTAKE-LP-PREVIEW.md)
- [PRD](../PRD-LP-PREVIEW.md)
- [Fase](./F1_LP-PREVIEW_EPICS.md)
