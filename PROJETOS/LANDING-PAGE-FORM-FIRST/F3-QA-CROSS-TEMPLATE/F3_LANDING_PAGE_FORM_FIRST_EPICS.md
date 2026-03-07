---
doc_id: "F3_LANDING_PAGE_FORM_FIRST_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# Epicos - LANDING-PAGE-FORM-FIRST / F3 - QA-CROSS-TEMPLATE

## Objetivo da Fase

Validar regressao visual, contraste WCAG AA, conformidade com a marca BB e fluxo funcional de gamificacao no novo layout form-only em todos os 7 templates e 3 breakpoints (375px, 768px, 1280px).

## Gate de Saida da Fase

Todos os 7 templates validados nos 3 breakpoints com fundo tematico correto, contraste minimo WCAG AA, amarelo BB presente, tagline BB presente, e fluxo de gamificacao funcional sem regressao.

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Regressao Visual e Conformidade | Validar fundo tematico, contraste WCAG AA e conformidade BB em todos os templates e breakpoints | nenhuma | todo | [EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md](./EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: nenhuma — fase F2 deve estar concluida antes de iniciar F3

## Escopo desta Fase

### Dentro

- validar fundo tematico dos 7 templates em 3 breakpoints
- validar contraste WCAG AA do card e rodape
- validar conformidade BB (amarelo #FCFC30, tagline, paleta)
- validar fluxo de gamificacao e estados no novo layout

### Fora

- correcoes de bugs encontrados (serao novas issues em F1 ou F2)
- testes de performance (LCP, TTI)
- testes de carga ou stress

## Definition of Done da Fase

- [ ] 7 templates × 3 breakpoints validados visualmente
- [ ] contraste WCAG AA nos campos e titulo do card (minimo 4.5:1)
- [ ] contraste minimo 3:1 do rodape contra fundo tematico
- [ ] amarelo BB (#FCFC30) presente em todos os templates
- [ ] tagline BB presente no rodape de todos os templates
- [ ] nenhuma cor fora do catalogo do Manual BB usada no fundo
- [ ] fluxo PRESENTING → ACTIVE → COMPLETED sem regressao em todos os templates

## Navegacao Rapida

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Epic F3-01](./EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE.md)
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
- `[[./EPIC-F3-01-REGRESSAO-VISUAL-E-CONFORMIDADE]]`
