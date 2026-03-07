---
doc_id: "ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-03-003 - Integrar Layout Form-Only

## User Story

Como participante de evento, quero que a landing page funcione como uma tela unica com fundo tematico, formulario centralizado, gamificacao e rodape minimo para ter uma experiencia coesa e rapida.

## Contexto Tecnico

Esta issue e a integracao final que monta o `LandingPageView.tsx` com a nova arvore de componentes:

```
FullPageBackground (z-index 0: gradiente + overlay)
  └── Container Flexbox (column, center)
        ├── FormCard (z-index 1: titulo + campos + LGPD + CTA)
        ├── GamificacaoBlock (se gamificacoes.length > 0)
        └── MinimalFooter
```

Os handlers existentes (`handleSubmitSuccess`, `handleReset`, `handleGamificacaoComplete`) devem ser preservados sem alteracao. O ThemeProvider via `buildLandingTheme` continua envolvendo todo o componente.

## Plano TDD

- Red: componentes novos existem isoladamente mas nao estao montados juntos em LandingPageView.
- Green: refatorar LandingPageView para usar FullPageBackground como wrapper, FormCard como corpo principal, GamificacaoBlock reposicionado e MinimalFooter no final.
- Refactor: limpar codigo morto do layout antigo; garantir que scroll funciona com fundo fixo.

## Criterios de Aceitacao

- Given a landing page completa, When carregada em mobile 375px, Then exibe fundo tematico + card do formulario above the fold
- Given a landing page completa, When carregada em desktop 1280px, Then o card esta centralizado com max 520px de largura
- Given o formulario preenchido e submetido, When handleSubmitSuccess executa, Then a mensagem de sucesso aparece dentro do card
- Given handleReset acionado, When o formulario e limpo, Then o card volta ao estado inicial
- Given a landing com gamificacao, When o usuario faz scroll, Then o GamificacaoBlock aparece abaixo do card com fundo tematico visivel
- Given o fundo tematico, When o usuario faz scroll pela pagina, Then o fundo permanece fixo e o conteudo rola sobre ele

## Definition of Done da Issue

- [ ] LandingPageView usa FullPageBackground como wrapper externo
- [ ] FormCard renderiza como corpo principal dentro do container Flexbox
- [ ] GamificacaoBlock aparece condicionalmente abaixo do FormCard
- [ ] MinimalFooter aparece no final do fluxo
- [ ] handlers existentes preservados e funcionais
- [ ] scroll funciona com fundo fixo
- [ ] layout responsivo em 375px, 768px e 1280px

## Tarefas Decupadas

- [ ] T1: refatorar LandingPageView: substituir arvore de componentes pelo novo layout
- [ ] T2: montar container Flexbox (column, center) dentro do FullPageBackground
- [ ] T3: renderizar FormCard com passagem de props de ativacao, evento e tema
- [ ] T4: renderizar GamificacaoBlock condicionalmente abaixo do FormCard
- [ ] T5: renderizar MinimalFooter no final do container
- [ ] T6: testar fluxo completo: submit → sucesso → reset → gamificacao
- [ ] T7: validar scroll com fundo fixo em mobile e desktop

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/FullPageBackground.tsx`
- `frontend/src/components/landing/FormCard.tsx`
- `frontend/src/components/landing/MinimalFooter.tsx`
- `frontend/src/components/landing/GamificacaoBlock.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado com novo layout)

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Issue FullPageBackground](./ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND.md)
- [Issue Overlay](./ISSUE-F1-01-002-ADAPTAR-RENDER-GRAPHIC-OVERLAY.md)
- [Issue FormCard](./ISSUE-F1-02-001-CRIAR-FORMCARD.md)
- [Issue MinimalFooter](./ISSUE-F1-02-002-CRIAR-MINIMAL-FOOTER.md)
- [Issue Remover Blocos](./ISSUE-F1-03-001-REMOVER-BLOCOS-LEGADOS.md)
- [Issue GamificacaoBlock](./ISSUE-F1-03-002-REPOSICIONAR-GAMIFICACAO-BLOCK.md)

## Navegacao Rapida

- `[[../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO]]`
- `[[./ISSUE-F1-01-001-CRIAR-FULLPAGEBACKGROUND]]`
- `[[./ISSUE-F1-02-001-CRIAR-FORMCARD]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
