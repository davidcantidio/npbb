---
doc_id: "EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F3-01 - Regressao Visual e Conformidade

## Objetivo

Validar sistematicamente o novo layout form-only em todos os 7 templates e 3 breakpoints, garantindo fundo tematico correto, contraste WCAG AA, conformidade com marca BB e fluxo funcional de gamificacao.

## Resultado de Negocio Mensuravel

Relatorio de QA com 21 combinacoes (7 templates × 3 breakpoints) validadas, zero falhas de contraste, zero regressoes no fluxo de gamificacao.

## Contexto Arquitetural

- templates: corporativo, esporte_convencional, esporte_radical, evento_cultural, show_musical, tecnologia, generico
- breakpoints: 375px (mobile), 768px (tablet), 1280px (desktop)
- criterios visuais detalhados no PRD secao 05
- criterios de contraste: WCAG AA (4.5:1 para texto normal, 3:1 para texto grande/caption)
- conformidade BB: amarelo #FCFC30, tagline, paleta homologada

## Definition of Done do Epico

- [ ] 21 combinacoes template × breakpoint validadas
- [ ] nenhuma falha de contraste WCAG AA
- [ ] amarelo BB presente em todos os templates
- [ ] tagline BB presente no rodape de todos os templates
- [x] fluxo de gamificacao funcional em todos os templates

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Validar Fundo Tematico Cross-Template | Verificar que cada template exibe gradiente e overlay corretos em 3 breakpoints | 5 | done | [ISSUE-F3-01-001-VALIDAR-FUNDO-TEMATICO.md](./issues/ISSUE-F3-01-001-VALIDAR-FUNDO-TEMATICO.md) |
| ISSUE-F3-01-002 | Validar Contraste WCAG AA | Verificar contraste minimo do card e rodape contra fundo em todos os templates | 3 | todo | [ISSUE-F3-01-002-VALIDAR-CONTRASTE-WCAG.md](./issues/ISSUE-F3-01-002-VALIDAR-CONTRASTE-WCAG.md) |
| ISSUE-F3-01-003 | Validar Gamificacao no Novo Layout | Verificar fluxo PRESENTING-ACTIVE-COMPLETED sem regressao em todos os templates | 3 | done | [ISSUE-F3-01-003-VALIDAR-GAMIFICACAO.md](./issues/ISSUE-F3-01-003-VALIDAR-GAMIFICACAO.md) |

## Artifact Minimo do Epico

- relatorio de QA cross-template com evidencias visuais

## Dependencias

- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Fase](./F3_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F3-01-001-VALIDAR-FUNDO-TEMATICO]]`
- `[[./issues/ISSUE-F3-01-002-VALIDAR-CONTRASTE-WCAG]]`
- `[[./issues/ISSUE-F3-01-003-VALIDAR-GAMIFICACAO]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
