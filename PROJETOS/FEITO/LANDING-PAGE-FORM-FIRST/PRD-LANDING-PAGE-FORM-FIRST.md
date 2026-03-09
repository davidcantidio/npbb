# PRD - LANDING-PAGE-FORM-FIRST
**Banco do Brasil · Plataforma NPBB — Módulo de Landing Pages Dinâmicas**

| Campo | Valor |
|---|---|
| Produto | LANDING-PAGE-FORM-FIRST |
| Iniciativa | BB-LANDING-PAGES-DINAMICAS — Sprint de Simplificação |
| Versão | 1.0 |
| Data | Março 2026 |
| Status | active |
| Origem do Intake | [INTAKE-LANDING-PAGE-FORM-FIRST.md](./INTAKE-LANDING-PAGE-FORM-FIRST.md) |
| Log de Auditoria | [AUDIT-LOG.md](./AUDIT-LOG.md) |
| Referência | `frontend/src/components/landing/LandingPageView.tsx` · `PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md` |

---

## Histórico de Revisões

| Versão | Descrição |
|---|---|
| 1.0 | Rascunho inicial — proposta de substituição do layout form-first por layout form-only temático |

---

## Sumário Executivo

O layout atual da landing page, mesmo após o redesign da v1.2, ainda carrega blocos que
distraem o participante da única ação esperada: **preencher o formulário**. O header com logo,
o bloco hero contextual, a hero image e o bloco "Sobre o evento" são informação que o
participante já possui — ele está fisicamente presente no evento.

Este PRD define uma nova camada de apresentação: **uma única tela com o formulário**,
sobre um fundo que traduz o território visual da ativação. Sem header, sem hero, sem blocos
de conteúdo. Apenas o formulário, flutuando sobre um fundo temático que reforça o contexto
emocional do evento sem explicá-lo.

---

## 01 · Diagnóstico — O Problema do Layout Atual

### 1.1 Contexto de Uso Real

O participante que acessa a landing page via QR code **já está no evento**. Ele está de pé,
provavelmente com o celular na mão, a alguns metros de um stand ou promotor do Banco do
Brasil. O participante não precisa:

- Ser informado do nome do evento
- Ver uma imagem hero do evento
- Ler uma "curta descrição" do que está acontecendo
- Ver o bloco "Sobre o evento"
- Reconhecer a logo do BB via header

Ele já sabe de tudo isso. O que ele precisa é **preencher o formulário o mais rápido
possível e voltar ao evento**.

### 1.2 O que o Layout Atual Faz de Errado

| Elemento | Problema |
|---|---|
| Header com logo BB | Ocupa espaço valioso acima da dobra; o BB já está fisicamente no espaço |
| Bloco hero contextual (nome, descrição, hero image) | Informação redundante para quem está no evento |
| Bloco "Sobre o evento" | Conteúdo que o participante não vai ler enquanto está em pé |
| Grid de 2 colunas em desktop | Complexidade de layout desnecessária para um produto mobile-first |
| Chips mood/categoria (mesmo em isPreview) | Polui o backoffice com dado que não tem uso operacional claro |

### 1.3 O que o Layout Atual Faz Certo e Deve Ser Preservado

- O formulário em si (campos, validação, LGPD, CTA) está correto e não deve ser alterado
- O sistema de templates visuais (`buildLandingTheme`, `renderGraphicOverlay`, `getLayoutVisualSpec`) é a infraestrutura certa — só precisa ser reaproveitado em um container mais simples
- O bloco de gamificação (`GamificacaoBlock`) é correto em conceito — será posicionado logo abaixo do formulário
- A lógica de derivação de conteúdo da ativação (`ativacao.nome`, `ativacao.mensagem_qrcode`, `evento.cta_personalizado`) está correta

---

## 02 · Proposta — Layout Form-Only Temático

### 2.1 Princípio de Design

> **Uma tela. Um formulário. Um fundo que fala pelo evento.**

A landing page é reduzida a um único elemento visual de primeiro plano: o card do formulário.
O fundo da página inteira é o sistema de temas — gradientes, grafismos e paletas que o
sistema já sabe calcular via `buildLandingTheme` e `renderGraphicOverlay`. O participante
não lê o tema, ele o **sente**.

### 2.2 Anatomia da Nova Tela

```
┌─────────────────────────────────────────────────┐  ← Viewport inteiro
│                                                 │
│  [fundo temático: gradiente + grafismo overlay] │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │  [nome da ativação ou evento]           │    │  ← Título mínimo, sem header
│  │  [callout mensagem_qrcode se presente]  │    │
│  │                                         │    │
│  │  [campos do formulário]                 │    │  ← Card branco/semitransparente
│  │                                         │    │     com borderRadius 24px
│  │  [checkbox LGPD]                        │    │
│  │  [botão CTA]                            │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  [GamificacaoBlock — se gamificacoes.length > 0]│
│                                                 │
│  [tagline BB e link política — rodapé mínimo]   │  ← Sem logo, só texto
│                                                 │
└─────────────────────────────────────────────────┘
```

**Mobile (375px):** o card do formulário ocupa 92% da largura, centralizado.
**Tablet (768px):** o card tem largura máxima de 480px, centralizado verticalmente.
**Desktop (1280px):** o card tem largura máxima de 520px, centralizado na página.

### 2.3 O Fundo Temático

O fundo **não é uma imagem**. É o sistema de tokens visuais do template aplicado ao `body`
da página:

| Template | Fundo |
|---|---|
| `corporativo` | Gradiente azul escuro → azul médio, grafismo geométrico sutil |
| `esporte_convencional` | Gradiente azul escuro → azul, acento amarelo nas bordas |
| `esporte_radical` | Gradiente rosa-escuro → azul, grafismos angulados dinâmicos |
| `evento_cultural` | Gradiente roxo claro → branco, formas orgânicas suaves |
| `show_musical` | Gradiente roxo escuro → preto, partículas/brilhos |
| `tecnologia` | Gradiente azul escuro → verde escuro, grid de pontos |
| `generico` | Gradiente azul BB → azul médio, grafema BB como watermark |

**A hero image nao faz mais parte do produto.**
O visual e personalizado apenas por `template_override` e pelos tokens homologados do template.

### 2.4 O Card do Formulário

O card é o único elemento de primeiro plano:

- **Background:** branco com 90–95% de opacidade (permite o tema vazar levemente)
  ou branco sólido — a definir por template (tokens controlam isso)
- **borderRadius:** `3` (24px) — consistente com o sistema atual
- **Sombra:** `elevation 8` do MUI — destaca o card sobre o fundo
- **Padding:** `24px` mobile, `32px` tablet+

**Dentro do card:**

| Elemento | Fonte | Comportamento |
|---|---|---|
| Título | `ativacao.nome ?? evento.nome` | Sempre presente; typography `h5` bold |
| Subtítulo | `ativacao.descricao ?? evento.descricao_curta` | Opcional; typography `body2` |
| Callout | `ativacao.mensagem_qrcode` | Opcional; `<Alert severity="info">` acima dos campos |
| Campos | configurados em `formulario.campos` | Sem alteração |
| LGPD | checkbox obrigatório | Sem alteração |
| CTA | `evento.cta_personalizado ?? template.cta_text` | Sem alteração |

---

## 03 · Requisitos Funcionais

### RF-01 — Remoção do Header

O header com logo BB deve ser **completamente removido** da view pública da landing page.

- A logo BB não aparece no topo da página
- O nome "Banco do Brasil" não aparece como elemento visual destacado
- **Exceção:** o modo `isPreview` no backoffice pode manter um indicador mínimo para o operador saber que está visualizando a landing (ex: badge "Preview" no canto, fora do fluxo de conteúdo)

**Justificativa:** o participante está no evento e já está interagindo com infraestrutura física do BB. O header é redundante e desperdiça espaço acima da dobra.

### RF-02 — Remoção do Bloco Hero Contextual

O bloco que exibe nome da ativação, descrição e hero image **como seção separada** deve ser removido.

- `HeroContextCard` (ou equivalente) não é renderizado na view pública
- nenhum asset de hero image é exibido ou mantido no runtime da landing
- Nome e descrição da ativação/evento são exibidos **apenas dentro do card do formulário** como título e subtítulo

### RF-03 — Remoção do Bloco "Sobre o Evento"

O card `AboutEventCard` (ou equivalente) não é renderizado na view pública.

- Os dados de quando/onde continuam disponiveis no payload para uso futuro
- Nenhum bloco adicional de marca e exibido nem na view publica nem no preview

### RF-04 — Fundo Temático Full-Page

O background da página inteira (`body` ou wrapper principal) deve receber os tokens visuais
do template resolvido.

- `buildLandingTheme(data)` já fornece os tokens — reutilizar sem modificar
- `renderGraphicOverlay(data)` já fornece o overlay gráfico — posicionado como layer `fixed`
  ou `absolute` cobrindo o fundo, atrás do card
- O resultado visual é: **gradiente de fundo + grafismo do template, preenchendo 100vw × 100vh**

**O fundo nunca é uma imagem de evento.** É sempre calculado pelos tokens do template.

### RF-05 — Card do Formulário Centralizado

O formulário deve ser apresentado em um único card centralizado na tela:

- Centralização horizontal e vertical na viewport (Flexbox com `alignItems: center`, `justifyContent: center`)
- Em mobile: largura `min(92vw, 440px)`, padding `20px`
- Em tablet+: largura `min(480px, 90vw)`, padding `32px`
- O card inicia visível sem necessidade de scroll em 375px × 667px (iPhone SE)
- Se o conteúdo do card for maior que a viewport, o card deve ser scrollável internamente
  **ou** a página deve permitir scroll com o fundo fixo

### RF-06 — Rodapé Mínimo

Substituir o `BrandFooter` atual por um rodapé mínimo de texto:

```
Banco do Brasil. Pra tudo que você imaginar.   Política de privacidade e LGPD
```

- Apenas texto, sem logo
- `typography variant="caption"`, cor adaptada ao tema (legível sobre o fundo)
- Link para política de privacidade mantido
- Posicionamento: abaixo do card (ou do GamificacaoBlock se presente), dentro do fluxo normal

### RF-07 — GamificacaoBlock Posicionado Abaixo do Card

O `GamificacaoBlock` continua funcionando exatamente como especificado no
`PRD-LANDING-REDESIGN-ATIVACAO-v1.2.md`, com as seguintes adaptações de layout:

- Posicionado abaixo do card do formulário, dentro do mesmo container de rolagem
- Mesma largura máxima do card do formulário
- Mesmo estilo de card (borderRadius 24px, elevação, opacidade de fundo similar)
- O fundo temático continua visível por trás do GamificacaoBlock

### RF-08 — Modo Preview no Backoffice

O modo `isPreview` deve continuar funcionando, com as seguintes adaptações:

- Exibe o mesmo layout form-only (não o layout antigo com hero)
- Exibe um badge flutuante de "Preview" no canto superior direito, fora do card
- Mantém os chips `mood`, `categoria` **dentro do card**, em seção colapsável abaixo dos campos — não no hero (que foi removido)
- O bloco "Marca BB" com tagline e informações do template é exibido abaixo do GamificacaoBlock, apenas em preview

---

## 04 · Requisitos Não-Funcionais

### RNF-01 — Performance

- O card do formulário deve ser visível (LCP) em menos de 1.5s em 4G — mais fácil de atingir sem hero image
- O fundo temático (gradiente + overlay) deve ser gerado via CSS/SVG, sem requisições de imagem externa
- Nenhuma requisição de imagem deve bloquear a renderização inicial

### RNF-02 — Responsividade Mobile-First

- Breakpoint base: 375px (iPhone SE) — esse é o tamanho de referência de design
- O formulário **nunca** requer scroll horizontal
- Em orientação landscape em mobile, o card deve ser scrollável verticalmente sem perder o fundo temático

### RNF-03 — Acessibilidade

- Contraste do título e campos do formulário contra o background do card: mínimo 4.5:1 (WCAG AA)
- Contraste do rodapé mínimo contra o fundo temático: mínimo 3:1 (texto grande/caption)
- O fundo temático é puramente decorativo — nenhum elemento do fundo carrega informação
- `aria-label` e labels visíveis nos campos: mantidos conforme v1.2

### RNF-04 — Conformidade com Marca BB

- **O fundo temático usa exclusivamente as paletas de cores do Manual BB** por categoria
- Nenhuma cor fora do catálogo homologado é usada como fundo
- O grafismo de overlay usa os `graphicsStyle` já definidos (`dynamic`, `geometric`, `organic`, `grid`, etc.)
- A tagline *"Banco do Brasil. Pra tudo que você imaginar."* continua presente no rodapé mínimo
- O amarelo BB (`#FCFC30`) está sempre presente como elemento de identidade — seja no CTA, na borda do card ou em acento no fundo

---

## 05 · Especificação Visual por Template — Fundo Temático

### 5.1 `corporativo`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(135deg, #1A237E 0%, #3333BD 60%, #465EFF 100%)` |
| Overlay gráfico | Linhas retas e grid modular, opacidade 8–12%, cor branca |
| Card background | `#FFFFFF` sólido |
| Card border | `2px solid rgba(252, 252, 48, 0.6)` (acento amarelo BB) |
| CTA button | Background `#FCFC30`, texto `#1A237E` |
| Rodapé texto | `rgba(255, 255, 255, 0.75)` |

### 5.2 `esporte_convencional`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(160deg, #3333BD 0%, #1A237E 50%, #3333BD 100%)` |
| Overlay gráfico | Formas geométricas sólidas, opacidade 10%, amarelo e branco |
| Card background | `rgba(255, 255, 255, 0.96)` |
| Card border | `none`; sombra `0 8px 32px rgba(0,0,0,0.35)` |
| CTA button | Background `#FCFC30`, texto `#1A237E` |
| Rodapé texto | `rgba(255, 255, 255, 0.75)` |

### 5.3 `esporte_radical`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(145deg, #3333BD 0%, #FF6E91 55%, #FCFC30 100%)` |
| Overlay gráfico | Formas anguladas dinâmicas, opacidade 15%, branco |
| Card background | `rgba(255, 255, 255, 0.95)` |
| Card border | `3px solid #FF6E91` |
| CTA button | Background `#FF6E91`, texto `#FFFFFF` |
| Rodapé texto | `rgba(255, 255, 255, 0.85)` |

### 5.4 `evento_cultural`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(150deg, #BDB6FF 0%, #E8E4FF 50%, #83FFEA 100%)` |
| Overlay gráfico | Formas orgânicas suaves, opacidade 12%, roxo escuro |
| Card background | `#FFFFFF` sólido |
| Card border | `none`; sombra `0 4px 24px rgba(115, 92, 198, 0.25)` |
| CTA button | Background `#735CC6`, texto `#FFFFFF` |
| Rodapé texto | `rgba(51, 51, 189, 0.75)` |

### 5.5 `show_musical`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(160deg, #0D0D1A 0%, #2D1B4E 50%, #4A1942 100%)` |
| Overlay gráfico | Partículas e brilhos, opacidade 20%, rosa e amarelo |
| Card background | `rgba(255, 255, 255, 0.97)` |
| Card border | `2px solid rgba(255, 110, 145, 0.5)` |
| CTA button | Background `#735CC6`, texto `#FFFFFF` |
| Rodapé texto | `rgba(255, 255, 255, 0.65)` |

### 5.6 `tecnologia`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(135deg, #0D1B2E 0%, #0A2440 40%, #0B3340 100%)` |
| Overlay gráfico | Grid de pontos e hexágonos, opacidade 15%, azul claro |
| Card background | `rgba(255, 255, 255, 0.97)` |
| Card border | `2px solid rgba(84, 220, 252, 0.5)` |
| CTA button | Background `#54DCFC`, texto `#0D1B2E` |
| Rodapé texto | `rgba(255, 255, 255, 0.70)` |

### 5.7 `generico`

| Elemento | Valor |
|---|---|
| Background gradient | `linear-gradient(150deg, #3333BD 0%, #465EFF 100%)` |
| Overlay gráfico | Grafema BB watermark, opacidade 5%, branco |
| Card background | `#FFFFFF` sólido |
| Card border | `none`; sombra padrão `elevation 4` |
| CTA button | Background `#FCFC30`, texto `#1A237E` |
| Rodapé texto | `rgba(255, 255, 255, 0.75)` |

---

## 06 · Impacto no Backoffice — "Contexto da Landing"

### 6.1 Campos a Manter

Os campos do painel "Contexto da landing" continuam existindo e fazem sentido:

| Campo | Justificativa |
|---|---|
| `template_override` | Controla o fundo temático — mais importante do que antes |
| `cta_personalizado` | Texto do botão dentro do card |
| `descricao_curta` | Subtítulo dentro do card |

### 6.2 Campo Removido do Produto

| Campo | Justificativa |
|---|---|
| `hero_image_url` | O campo foi removido do formulario, dos payloads e do banco. A volta desse conceito exigira nova decisao de produto, novo contrato e nova migration. |

### 6.3 Ajuste na Mensagem de Customização Controlada

O aviso do painel deve ser:
> "Customizacao controlada: somente `template_override`, `cta_personalizado` e `descricao_curta` podem ser alterados sem sair do catalogo homologado da marca BB. O visual do fundo e determinado pelo template selecionado."

---

## 07 · Impacto no Código Existente

### 7.1 O que é Removido de `LandingPageView.tsx` (ou equivalente)

| Bloco | Ação |
|---|---|
| Header com logo BB | **Remover** definitivamente da view publica e do preview |
| `HeroContextCard` (nome, descrição, hero image como seção separada) | **Remover** |
| `<Box component="img" src={heroImageUrl}>` | **Remover** |
| `AboutEventCard` (quando/onde/link) | **Remover** da view pública |
| `BrandSummaryCard` | **Remover** do produto |
| Grid de 2 colunas do hero | **Substituir** por Flexbox de coluna única centralizado |

### 7.2 O que é Mantido

| Elemento | Ação |
|---|---|
| `buildLandingTheme(data)` | **Manter** — ainda gera o ThemeProvider |
| `renderGraphicOverlay(data)` | **Manter** — agora é layer de fundo full-page |
| `getLayoutVisualSpec(data)` | **Manter** — seus tokens alimentam o fundo e o card |
| Formulário e campos | **Manter sem alteração** |
| `GamificacaoBlock` | **Manter** — posicionado abaixo do card |
| Lógica de fallback de conteúdo | **Manter** — título, subtítulo, CTA derivados da ativação |
| Estados `leadSubmitted` / `ativacaoLeadId` | **Manter** |
| `handleSubmitSuccess`, `handleReset`, `handleGamificacaoComplete` | **Manter** |

### 7.3 O que é Adicionado

| Elemento | Descrição |
|---|---|
| `FullPageBackground` | Wrapper que aplica gradient + overlay como layer fixo (z-index 0) |
| `FormCard` | Container do formulário: card centralizado, elevado, com borderRadius 24px (z-index 1) |
| `MinimalFooter` | Tagline + link de política, typography caption, sem logo |

---

## 08 · Casos de Uso Atualizados

### UC-01 — Ativação sem gamificação (novo layout)
1. Participante escaneia QR; tela carrega com fundo temático preenchendo toda a viewport
2. Card do formulário visível imediatamente, sem scroll, com título = `ativacao.nome`
3. Preenche campos, marca LGPD, clica CTA
4. Vê mensagem de sucesso dentro do card (fundo temático permanece)

### UC-02 — Ativação com mensagem de orientação
1. Callout `mensagem_qrcode` visível dentro do card, acima dos campos
2. Fluxo de formulário normal

### UC-03 — Ativação com gamificação
1. Participante vê o fundo temático e o card do formulário above the fold
2. Faz scroll suave e vê o card do GamificacaoBlock abaixo
3. Preenche e submete o formulário
4. GamificacaoBlock habilita botão "Quero participar"
5. Fluxo completo de gamificação dentro do card abaixo
6. Reset → formulário limpo, GamificacaoBlock volta a PRESENTING

### UC-04 — Preview no backoffice
1. Operador vê o novo layout form-only com badge "Preview" flutuante
2. Fundo temático calculado pelo `template_override` configurado
3. O preview replica a mesma composicao publicada: FormCard, GamificacaoBlock e MinimalFooter
4. Nenhum chip, checklist ou bloco de marca extra aparece no preview

---

## 09 · Critérios de Aceite

**FORM-ONLY-01 — Layout:**
- [ ] Nenhum header com logo BB na view pública
- [ ] Nenhuma hero image exibida na view pública
- [ ] Nenhum bloco "Sobre o evento" na view pública
- [ ] Card do formulário visível above the fold em 375px × 667px sem scroll
- [ ] Card do formulário centralizado horizontalmente em todos os breakpoints
- [ ] Fundo temático preenche 100vw × 100vh sem gap ou cor padrão do browser

**FORM-ONLY-02 — Fundo Temático:**
- [ ] Cada um dos 7 templates exibe fundo com gradiente e overlay distintos
- [ ] Nenhuma imagem externa é carregada para compor o fundo
- [ ] `renderGraphicOverlay()` funciona sem regressão visual no novo container
- [ ] `template_override` no backoffice muda o fundo temático em tempo de preview

**FORM-ONLY-03 — Card do Formulário:**
- [ ] Título usa `ativacao.nome ?? evento.nome`
- [ ] Subtítulo usa `ativacao.descricao ?? evento.descricao_curta` (opcional, só aparece se presente)
- [ ] Callout `mensagem_qrcode` aparece acima dos campos (se presente)
- [ ] CTA usa `evento.cta_personalizado ?? template.cta_text`
- [ ] Card tem `borderRadius: 3` (24px), elevação e fundo branco/semitransparente

**FORM-ONLY-04 — Rodapé Mínimo:**
- [ ] Tagline BB presente como texto
- [ ] Link para política de privacidade funcional
- [ ] Nenhuma logo ou imagem no rodapé

**FORM-ONLY-05 — GamificacaoBlock:**
- [ ] Posicionado abaixo do card do formulário
- [ ] Mesma largura máxima do card do formulário
- [ ] Fundo temático visível por trás do GamificacaoBlock
- [ ] Fluxo de estados PRESENTING → ACTIVE → COMPLETED sem regressão

**FORM-ONLY-06 — Backoffice:**
- [ ] Campo `hero_image_url` removido do painel "Contexto da landing"
- [ ] Mensagem de customização controlada atualizada
- [ ] Preview mostra o novo layout form-only (não o layout antigo)
- [ ] Badge "Preview" visível no modo `isPreview`
- [ ] `hero_image_url` removido dos payloads de evento e landing
- [ ] `hero_image_url` removido do schema e do banco de dados

**FORM-ONLY-07 — Conformidade BB:**
- [ ] Amarelo BB (`#FCFC30`) presente em todos os templates (CTA, borda ou fundo)
- [ ] Tagline *"Banco do Brasil. Pra tudo que você imaginar."* presente no rodapé
- [ ] Nenhuma cor fora do catálogo do Manual BB usada no fundo
- [ ] Contraste WCAG AA nos campos e título do card
- [ ] Contraste mínimo 3:1 do rodapé contra o fundo temático

---

## 10 · Fora de Escopo

- Edição visual do fundo pelo operador (cores, gradientes) — o catálogo de templates é a fonte de verdade
- Reintroduzir hero image, bloco de marca ou metadados visuais extras no preview sem nova decisao formal
- Animações de entrada do card ou do fundo — melhoria futura de UX
- Múltiplos cards ou etapas de formulário (multi-step form)
- Exibição de header/logo BB sob qualquer condição na view pública

---

## 11 · Dependências e Riscos

| Dependência | Impacto | Mitigação |
|---|---|---|
| `renderGraphicOverlay()` assumir posicionamento DOM específico | Pode quebrar com novo container full-page | Verificar e adaptar o container antes de remover o layout antigo |
| `getLayoutVisualSpec()` retornar valores que dependiam do hero | Tokens de `imageMinHeight` etc. serão inutilizados | Mapear quais tokens ainda são relevantes; ignorar os de hero |
| Operadores que usavam `hero_image_url` para personalizar landings | Quebra explicita de fluxo e de expectativa | Comunicar mudanca, remover campo do formulario e bloquear o campo por schema estrito |
| Clientes integrados ao payload antigo | Quebra de contrato ao remover `hero_image_url` e metadados de marca nao usados | Versionar comunicacao interna, atualizar fixtures e invalidar caches dependentes do shape antigo |

---

## 12 · Fases Previstas

| Fase | Nome | Objetivo | DoD resumido | Status |
|---|---|---|---|---|
| F1 | LAYOUT-FORM-ONLY | Implementar o novo layout form-only com fundo tematico, card centralizado, rodape minimo e remocao definitiva dos blocos legados | Novo layout renderizavel, formulario funcional, gamificacao reposicionada e runtime legado removido | done |
| F2 | BACKOFFICE-E-PREVIEW | Ajustar o backoffice, o preview e os contratos para refletir o novo layout | Campo hero_image_url removido do painel, mensagem atualizada, preview espelha a landing publica com badge discreto, schema e banco atualizados | done |
| F3 | QA-CROSS-TEMPLATE | Validar regressão visual, contraste e conformidade BB em todos os templates e breakpoints | 7 templates × 3 breakpoints validados, contraste WCAG AA, fluxo de gamificação sem regressão | todo |

## 13 · Roadmap Sugerido

| Sprint | Entrega |
|---|---|
| Sprint F1-01 | EPIC-F1-01 (Fundo Temático) + EPIC-F1-02 (Card e Rodapé): 13 SP |
| Sprint F1-02 | EPIC-F1-03 (Remoção de Blocos e Integração): 9 SP |
| Sprint F2-01 | EPIC-F2-01 (Ajuste Backoffice) + EPIC-F2-02 (Preview): 9 SP |
| Sprint F3-01 | EPIC-F3-01 (Regressão Visual e Conformidade): 11 SP |

---

*Banco do Brasil · PRD Landing Form-Only v1.0 · Confidencial Interno*
*Pra tudo que você imaginar.*
