---
doc_id: "ISSUE-F1-03-003-INTEGRAR-LAYOUT-FORM-ONLY.md"
version: "1.2"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
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

- [x] LandingPageView usa FullPageBackground como wrapper externo
- [x] FormCard renderiza como corpo principal dentro do container Flexbox
- [x] GamificacaoBlock aparece condicionalmente abaixo do FormCard
- [x] MinimalFooter aparece no final do fluxo
- [x] handlers existentes preservados e funcionais
- [x] scroll funciona com fundo fixo
- [x] layout responsivo em 375px, 768px e 1280px

## Tarefas Decupadas

- [x] T1: refatorar LandingPageView: substituir arvore de componentes pelo novo layout
- [x] T2: montar container Flexbox (column, center) dentro do FullPageBackground
- [x] T3: renderizar FormCard com passagem de props de ativacao, evento e tema
- [x] T4: renderizar GamificacaoBlock condicionalmente abaixo do FormCard
- [x] T5: renderizar MinimalFooter no final do container
- [x] T6: testar fluxo completo: submit → sucesso → reset → gamificacao
- [x] T7: validar scroll com fundo fixo em mobile e desktop

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/FullPageBackground.tsx`
- `frontend/src/components/landing/FormCard.tsx`
- `frontend/src/components/landing/MinimalFooter.tsx`
- `frontend/src/components/landing/GamificacaoBlock.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (refatorado com novo layout)

## Validacao de Encerramento Tecnico

### Composicao Final Confirmada

- `LandingPageView.tsx` monta `ThemeProvider` via `buildLandingTheme(data)`, aplica `FullPageBackground` como wrapper externo, centraliza o fluxo em coluna unica e renderiza `FormCard`, `LandingGamificacaoSection` e `MinimalFooter` nesta ordem
- `FullPageBackground.tsx` preserva gradiente e overlay como layers `fixed` atras do conteudo, com `pointerEvents: none` no overlay decorativo
- `FormCard.tsx` preserva os breakpoints canonicos (`92vw/440px`, `480px`, `520px`) e mantem os estados de formulario, sucesso e reset sem alterar o fluxo funcional
- `landingSections.gamificacao.tsx` mantem a gamificacao abaixo do card e compartilha a mesma largura maxima do layout form-only

### Encadeamento de Handlers Confirmado

- `EventLandingPage.tsx` continua entregando `onSubmit` e `onReset` diretamente para `LandingPageView`
- `EventLandingPage.tsx` continua entregando `gamificacao.onComplete` e `gamificacao.onReset` para `LandingPageView` sem adaptacao funcional intermediaria
- `LandingPageView.tsx` apenas encaminha esses callbacks para `FormCard` e `LandingGamificacaoSection`, preservando o contrato de integracao ja em uso

### Mudanca de API Publica

- nenhuma mudanca de API publica foi introduzida nesta validacao
- props de `LandingPageView`, `FormCard`, `GamificacaoBlock` e o contrato visual de tema permanecem inalterados

## Evidencias de Validacao

### Mapeamento dos Criterios de Aceitacao

| Criterio | Evidencia |
|---|---|
| mobile 375px exibe fundo tematico + card above the fold | `frontend/src/components/landing/__tests__/LandingVisualRegression.test.tsx` valida breakpoints `375/768/1280` e renderizacao do formulario sem blocos legados |
| desktop 1280px centraliza card com max 520px | `frontend/src/components/landing/__tests__/LandingVisualRegression.test.tsx` cobre `1280px`; `FormCard.tsx` fixa largura maxima em `520px` |
| submit mostra sucesso dentro do card | `frontend/src/components/landing/__tests__/LandingUCFlows.test.tsx` valida mensagem de sucesso apos submit |
| reset retorna estado inicial | `frontend/src/components/landing/__tests__/LandingUCFlows.test.tsx` valida reset da gamificacao para estado inicial; `FormCard.tsx` mantem CTA de reset do cadastro no estado de sucesso |
| gamificacao aparece abaixo do card | `frontend/src/components/landing/LandingPageView.tsx` renderiza `LandingGamificacaoSection` logo apos `FormCard`; `frontend/src/components/landing/__tests__/LandingPageView.test.tsx` cobre presenca/ausencia do bloco |
| fundo permanece fixo durante scroll | `frontend/src/components/landing/__tests__/LandingVisualRegression.test.tsx` valida integracao do wrapper `FullPageBackground`; `frontend/src/components/landing/__tests__/LandingPageView.test.tsx` valida overlay decorativo sem bloquear interacao |

### Suite Minima Executada

```bash
npm run test -- --run src/components/landing/__tests__/LandingPageView.test.tsx src/components/landing/__tests__/LandingUCFlows.test.tsx src/components/landing/__tests__/LandingVisualRegression.test.tsx
```

Resultado esperado para encerramento desta issue: todos os testes passam sem necessidade de alterar o codigo de runtime.

### Regra de Divergencia

- se alguma validacao futura divergir deste documento, o tratamento correto e abrir follow-up local de correcao
- esta issue nao deve ser reexecutada como se o layout ainda estivesse pendente

## Orientacao de Refacao Pos-Entrega

- a integracao desta issue esta funcionalmente concluida: a composicao ativa ja e form-only
- a refacao derivada desta etapa deve limpar o contrato visual ainda herdado do layout antigo, principalmente onde `LandingPageView` consome nomes como `heroTextColor`
- a meta da limpeza e deixar a integracao final semanticamente coerente com pagina, fundo, card e footer, sem referencias conceituais a hero

## Dependencias

- [Epic](../EPIC-F1-03-REMOCAO-BLOCOS-E-INTEGRACAO.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)
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
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
