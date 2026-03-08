---
doc_id: "F1_LANDING_PAGE_FORM_FIRST_EPICS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - LANDING-PAGE-FORM-FIRST / F1 - LAYOUT-FORM-ONLY

## Objetivo da Fase

Implementar o novo layout form-only da landing page: fundo tematico full-page via tokens do template, card do formulario centralizado, rodape minimo e remocao completa dos blocos legados (header, hero, about). O resultado e uma tela unica onde o formulario e o unico elemento de primeiro plano.

## Gate de Saida da Fase

O novo layout renderiza corretamente nos 7 templates, o formulario funciona sem regressao, o GamificacaoBlock esta reposicionado abaixo do card, e nenhum bloco legado aparece na view publica.

## Gate de Auditoria da Fase

- estado_do_gate: `not_ready`
- ultima_auditoria: `nenhuma`
- veredito_atual: `n-a`
- relatorio_mais_recente: `n-a`
- log_do_projeto: [AUDIT-LOG](../AUDIT-LOG.md)
- convencao_de_relatorios: [README](./auditorias/README.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Fundo Tematico e Container Principal | Criar o wrapper FullPageBackground e adaptar renderGraphicOverlay como layer de fundo fixa | nenhuma | done | [EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md) |
| EPIC-F1-02 | Card do Formulario e Rodape Minimo | Criar o FormCard centralizado e o MinimalFooter | nenhuma | done | [EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md) |
| EPIC-F1-03 | Remocao de Blocos Legados e Integracao | Remover header, hero, about da view publica; reposicionar GamificacaoBlock; integrar todos os componentes novos em LandingPageView | EPIC-F1-01, EPIC-F1-02 | done | [EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md](./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md) |

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

- [x] componente FullPageBackground renderiza gradiente + overlay em todos os 7 templates
- [x] componente FormCard exibe formulario centralizado com titulo, subtitulo, callout, campos, LGPD e CTA
- [x] componente MinimalFooter exibe tagline BB e link de politica sem logo
- [x] header, HeroContextCard e AboutEventCard nao aparecem na view publica
- [x] GamificacaoBlock posicionado abaixo do FormCard com mesma largura maxima
- [x] formulario funcional sem regressao (submit, reset, estados)
- [x] layout responsivo em 375px, 768px e 1280px
- [ ] gate de auditoria preparado para futura rodada em `auditorias/`

## Estado Atual vs Refacao Necessaria

### Ja Entregue

- runtime publico e preview consolidados no layout form-only
- blocos legados removidos da composicao principal e arquivos antigos retirados do diretório de landing
- FormCard, GamificacaoBlock e MinimalFooter compartilham o mesmo fluxo visual final

### Refacao Residual para Alinhamento Total ao Paradigma Atual

- rebatizar o contrato `LayoutVisualSpec` em `landingStyle.tsx` para eliminar semantica herdada de hero
- remover campos visuais mortos ou nao mais consumidos pelo layout final, como `heroMinHeight`, `heroGridColumns`, `heroTextCardBackground`, `heroTextCardBorder`, `contentGridColumns` e `imageMinHeight`
- reduzir o contrato de `FormCard` e `MinimalFooter` para depender apenas dos tokens realmente usados no layout form-only
- manter `template.hero_layout` apenas como seletor tecnico interno enquanto existir, sem propagar a nomenclatura de hero para novos componentes ou docs

## Navegacao Rapida

- [Intake](../INTAKE-LANDING-PAGE-FORM-FIRST.md)
- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Audit Log](../AUDIT-LOG.md)
- [Epic F1-01](./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER.md)
- [Epic F1-02](./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Epic F1-03](./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- `[[../INTAKE-LANDING-PAGE-FORM-FIRST]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
- `[[./EPIC-F1-01-FUNDO-TEMATICO-E-CONTAINER]]`
- `[[./EPIC-F1-02-CARD-FORMULARIO-E-RODAPE]]`
- `[[./EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
