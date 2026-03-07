---
doc_id: "F1_LANDING_PAGE_FORM_FIRST_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# Epicos - LANDING-PAGE-FORM-FIRST / F1 - LAYOUT-FORM-ONLY

## Objetivo da Fase

Implementar o novo layout form-only da landing page: fundo tematico full-page via tokens do template, card do formulario centralizado, rodape minimo e remocao completa dos blocos legados (header, hero, about). O resultado e uma tela unica onde o formulario e o unico elemento de primeiro plano.

## Gate de Saida da Fase

O novo layout renderiza corretamente nos 7 templates, o formulario funciona sem regressao, o GamificacaoBlock esta reposicionado abaixo do card, e nenhum bloco legado aparece na view publica.

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Fundo Tematico e Container Principal | Criar o wrapper FullPageBackground e adaptar renderGraphicOverlay como layer de fundo fixa | nenhuma | todo | [EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md) |
| EPIC-F1-02 | Card do Formulario e Rodape Minimo | Criar o FormCard centralizado e o MinimalFooter | nenhuma | todo | [EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md) |
| EPIC-F1-03 | Remocao de Blocos Legados e Integracao | Remover header, hero, about da view publica; reposicionar GamificacaoBlock; integrar todos os componentes novos em LandingPageView | EPIC-F1-01, EPIC-F1-02 | todo | [EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md](./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma — pode iniciar imediatamente
- `EPIC-F1-02`: nenhuma — pode ser paralelo ao EPIC-F1-01
- `EPIC-F1-03`: depende de EPIC-F1-01 e EPIC-F1-02 (precisa dos componentes novos para integrar)

```
EPIC-F1-01 ──┐
             ├──► EPIC-F1-03
EPIC-F1-02 ──┘
```

## Escopo desta Fase

### Dentro

- criar componente FullPageBackground com gradiente + overlay
- adaptar renderGraphicOverlay para container full-page
- criar componente FormCard centralizado com tokens do tema
- criar componente MinimalFooter
- remover Header, HeroContextCard, AboutEventCard da view publica
- reposicionar GamificacaoBlock abaixo do FormCard
- integrar tudo em LandingPageView.tsx

### Fora

- ajustes no backoffice (fase F2)
- adaptacao do modo preview (fase F2)
- QA cross-template sistematico (fase F3)
- animacoes de entrada ou transicoes visuais
- multi-step form ou multiplos cards

## Definition of Done da Fase

- [ ] componente FullPageBackground renderiza gradiente + overlay em todos os 7 templates
- [ ] componente FormCard exibe formulario centralizado com titulo, subtitulo, callout, campos, LGPD e CTA
- [ ] componente MinimalFooter exibe tagline BB e link de politica sem logo
- [ ] header, HeroContextCard e AboutEventCard nao aparecem na view publica
- [ ] GamificacaoBlock posicionado abaixo do FormCard com mesma largura maxima
- [ ] formulario funcional sem regressao (submit, reset, estados)
- [ ] layout responsivo em 375px, 768px e 1280px

## Navegacao Rapida

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Epic F1-01](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Epic F1-02](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Epic F1-03](./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
- `[[./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER]]`
- `[[./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE]]`
- `[[./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
