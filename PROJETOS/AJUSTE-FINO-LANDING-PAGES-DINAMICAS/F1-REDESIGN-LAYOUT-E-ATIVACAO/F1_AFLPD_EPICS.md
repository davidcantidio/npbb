# Épicos — Ajuste Fino Landing Pages Dinâmicas / F1 — Redesign Layout e Ativação
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F1
**prd:** ../PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md
**status:** aprovado

---
## Objetivo da Fase
Reestruturar o layout da landing page para posicionar o formulário acima da dobra
(form-first) em todos os breakpoints, remover chips de dados internos (`mood`,
`categoria`) da view pública, ajustar border-radius e hero image condicional, e
alimentar título, subtítulo, callout e CTA com dados reais da ativação.

Ao final da fase, a landing renderiza o formulário above the fold, exibe conteúdo
derivado de `ativacao.nome`, `ativacao.descricao`, `ativacao.mensagem_qrcode` e
`evento.cta_personalizado`, sem expor campos de configuração interna ao usuário final.

## Épicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Redesign Layout Form-First e Ajustes Visuais | Reestruturar grid para form-first, reduzir border-radius, remover chips internos, condicionar hero image e substituir logo BB por SVG. | nenhuma | 🔲 | `EPIC-F1-01-REDESIGN-LAYOUT-FORM-FIRST.md` |
| EPIC-F1-02 | Conteúdo Derivado da Ativação | Alimentar título, subtítulo, callout de orientação e texto do CTA com dados da ativação e evento, sem renderizar campos de template como texto. | EPIC-F1-01 | 🔲 | `EPIC-F1-02-CONTEUDO-DERIVADO-DA-ATIVACAO.md` |

## Dependências entre Épicos
`EPIC-F1-01` → `EPIC-F1-02`

O EPIC-F1-02 depende do EPIC-F1-01 porque o novo layout define os slots visuais
(título do formulário, callout, CTA) que serão alimentados com dados da ativação.

## Definition of Done da Fase
- [ ] Formulário visível sem scroll em viewports 375px, 768px e 1280px
- [ ] `borderRadius` máximo nos cards = 24px (valor `3` no tema MUI)
- [ ] Chips `mood` e `categoria` ausentes na view pública; presentes no modo `preview`
- [ ] `renderGraphicOverlay()` sem regressão visual entre templates existentes
- [ ] Hero image renderizada condicionalmente (apenas se `url_hero_image` presente e não vazia)
- [ ] Logo BB via `<img>` ou SVG (não mais texto `"BB"` em `Box`)
- [ ] Título do formulário usa `ativacao.nome` quando disponível
- [ ] Callout de orientação exibido quando `mensagem_qrcode` presente
- [ ] CTA resolve `evento.cta_personalizado` antes do default do template
- [ ] Nenhum campo de `template` (`mood`, `categoria`, `tema`, `tone_of_voice`) renderizado como texto na view pública
- [ ] Bloco "Sobre o evento" condicional — apenas se descrição disponível

## Notas e Restrições
- `renderGraphicOverlay()`, `buildLandingTheme()`, `getLayoutVisualSpec()` e `ThemeProvider` não devem ser alterados
- `mood` e `categoria` permanecem no payload `LandingTemplateConfig` — apenas a renderização como texto é removida
- `graphics_style` permanece no payload — consumido funcionalmente por `renderGraphicOverlay()`
- Mobile: formulário aparece primeiro (`order: -1`), antes do bloco hero contextual
