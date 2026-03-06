# EPIC-F1-01 — Redesign Layout Form-First e Ajustes Visuais
**version:** 1.0.0 | **last_updated:** 2026-03-06
**projeto:** AJUSTE-FINO-LANDING-PAGES-DINAMICAS | **fase:** F1 | **status:** 🔲

---
## 1. Resumo do Épico
Reestruturar o grid de `LandingPageView.tsx` para posicionar o formulário acima da
dobra em todos os breakpoints (form-first), reduzir o `borderRadius` de 48px para
24px em todos os `Paper`, remover os chips de `mood` e `categoria` da view pública
(mantendo-os no modo `preview`), tornar a hero image condicional e substituir o logo
BB de texto por imagem SVG.

**Resultado de Negócio Mensurável:** O formulário de captação fica imediatamente
visível sem scroll, eliminando a barreira de interação que causa abandono. A
identidade visual fica alinhada à linguagem do Banco do Brasil.

## 2. Contexto Arquitetural
- Componente principal: `frontend/src/components/landing/LandingPageView.tsx`
- Tema MUI construído por `buildLandingTheme(data)` — não será alterado
- `renderGraphicOverlay(data)` aplica diferenciação visual por template — não será alterada
- `getLayoutVisualSpec(data)` retorna specs de layout por template — não será alterado
- Grid atual: 2 colunas no hero, formulário posicionado abaixo no fluxo de documento
- Logo BB: atualmente é texto `"BB"` em `Box`; será substituído por `<img src="/logo-bb.svg">`
- Asset `/logo-bb.svg` deve existir em `frontend/public/`

## 3. Riscos e Armadilhas
- Alterar a ordem do grid pode quebrar `renderGraphicOverlay()` se ela depender de posição DOM — verificar antes
- Reduzir `borderRadius` globalmente pode afetar elementos que não são cards — escopo restrito a `Paper`
- Remoção de chips sem guardar condição `isPreview` pode eliminar informação útil no backoffice
- Hero image condicional precisa de fallback visual (background gradient) para não deixar espaço vazio

## 4. Definition of Done do Épico
- [ ] Grid reestruturado: formulário acima da dobra em 375px, 768px e 1280px
- [ ] Mobile: formulário com `order: -1`, aparece antes do hero contextual
- [ ] `borderRadius` de todos os `Paper` alterado de `6` para `3`
- [ ] Chips `mood` e `categoria` removidos da view pública, mantidos dentro de `isPreview`
- [ ] Hero image renderizada apenas quando `url_hero_image` presente e não vazia
- [ ] Fallback visual (background com gradient/cor do tema) quando hero image ausente
- [ ] Logo BB substituído por `<img>` ou SVG do grafema BB
- [ ] `renderGraphicOverlay()` sem regressão visual em todos os templates existentes
- [ ] Nenhuma alteração em `buildLandingTheme`, `getLayoutVisualSpec` ou `ThemeProvider`

---
## Issues

### AFLPD-F1-01-001 — Reestruturar grid para form-first e ajustar order mobile
**tipo:** feature | **sp:** 5 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Alterar a estrutura de grid do hero em `LandingPageView.tsx` para que o formulário
ocupe a posição primária (coluna direita em desktop, `order: -1` em mobile). O bloco
hero contextual (nome da ativação, descrição, imagem) fica na coluna esquerda em
desktop e abaixo em mobile.

**Plano TDD:**
- **Red:** Escrever teste que renderiza `LandingPageView` com dados mock e verifica que o formulário aparece antes do hero contextual no DOM em viewport mobile (375px).
- **Green:** Reestruturar o grid MUI de 2 colunas invertendo a ordem: formulário à direita em desktop, `order: -1` em mobile.
- **Refactor:** Extrair constantes de breakpoint e order para o spec de layout, consolidar media queries.

**Critérios de Aceitação:**
- Given viewport 375px, When a landing page é renderizada, Then o formulário é o primeiro bloco interativo visível sem scroll
- Given viewport 1280px, When a landing page é renderizada, Then o formulário ocupa a coluna direita do grid hero e fica visível acima da dobra
- Given viewport 768px, When a landing page é renderizada, Then o formulário é visível sem scroll vertical

**Tarefas:**
- [ ] T1: Mapear a estrutura atual do grid em `LandingPageView.tsx` e identificar pontos de alteração
- [ ] T2: Reestruturar `Grid` container do hero: formulário na coluna direita (desktop), `order: -1` (mobile)
- [ ] T3: Ajustar `minHeight` do hero para garantir form above the fold em 375px
- [ ] T4: Verificar que `renderGraphicOverlay()` continua funcional com a nova ordem DOM
- [ ] T5: Testar em 375px, 768px e 1280px — formulário visível sem scroll

**Notas técnicas:**
A propriedade CSS `order` no `Grid item` do formulário garante reordenação em mobile
sem duplicar markup. Manter `sx={{ order: { xs: -1, md: 0 } }}` para que desktop
preserve a ordem natural do grid.

---
### AFLPD-F1-01-002 — Reduzir borderRadius e remover chips internos da view pública
**tipo:** refactor | **sp:** 3 | **prioridade:** alta | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Alterar o `borderRadius` de todos os `Paper` de `6` (48px) para `3` (24px) em
`LandingPageView.tsx`. Remover os chips que exibem `data.template.mood`,
`data.template.categoria` e o chip condicional "Radical" da view pública, mantendo-os
exclusivamente dentro do bloco condicionado por `isPreview`.

**Plano TDD:**
- **Red:** Escrever teste que renderiza a landing em modo público (não preview) e asserta que nenhum `Chip` com texto `mood` ou `categoria` está no DOM.
- **Green:** Envolver os chips em `{isPreview && (...)}` e alterar `borderRadius` nos `Paper`.
- **Refactor:** Consolidar props de `Paper` em constante reutilizável para evitar repetição de `borderRadius`.

**Critérios de Aceitação:**
- Given modo público (isPreview=false), When a landing é renderizada, Then nenhum Chip com texto de `mood`, `categoria` ou "Radical" aparece no DOM
- Given modo preview (isPreview=true), When a landing é renderizada, Then os chips `mood`, `categoria` e "Radical" continuam visíveis
- Given qualquer modo, When a landing é renderizada, Then todos os `Paper` têm `borderRadius` máximo de 24px

**Tarefas:**
- [ ] T1: Localizar todos os `Paper` em `LandingPageView.tsx` e alterar `borderRadius` de `6` para `3`
- [ ] T2: Envolver chip `mood` em `{isPreview && (...)}`
- [ ] T3: Envolver chip `categoria` e chip condicional "Radical" em `{isPreview && (...)}`
- [ ] T4: Verificar que modo preview mantém chips visíveis
- [ ] T5: Teste visual: confirmar que 24px está alinhado com linguagem visual BB

**Notas técnicas:**
O valor `borderRadius: 3` no tema MUI equivale a `3 * 8px = 24px` por padrão. Se o
projeto usar fator de escala diferente, ajustar proporcionalmente.

---
### AFLPD-F1-01-003 — Hero image condicional e substituição do logo BB
**tipo:** feature | **sp:** 3 | **prioridade:** média | **status:** 🔲
**depende de:** nenhuma

**Descrição:**
Tornar a renderização da hero image condicional — exibida apenas quando
`data.marca.url_hero_image` estiver presente e não for string vazia. Quando ausente,
renderizar fallback visual (box com background gradient do tema). Substituir o logo
BB de texto `"BB"` em `Box` por `<img src="/logo-bb.svg">` no header e footer.

**Plano TDD:**
- **Red:** Escrever teste que renderiza landing com `url_hero_image: ""` e verifica que nenhum `<img>` de hero existe no DOM, mas um box de fallback com background está presente.
- **Green:** Adicionar condicional `{data.marca.url_hero_image ? <img> : <Box fallback>}` e substituir logo BB por `<img>`.
- **Refactor:** Extrair componente `HeroImage` para encapsular lógica condicional.

**Critérios de Aceitação:**
- Given `url_hero_image` vazia ou ausente, When a landing é renderizada, Then nenhuma tag `<img>` de hero aparece e um box com background gradient é exibido
- Given `url_hero_image` com URL válida, When a landing é renderizada, Then a imagem é exibida normalmente
- Given qualquer landing, When a página é renderizada, Then o logo BB é uma imagem SVG, não texto

**Tarefas:**
- [ ] T1: Adicionar asset `/logo-bb.svg` em `frontend/public/` (grafema BB oficial)
- [ ] T2: Substituir `Box` com texto "BB" por `<Box component="img" src="/logo-bb.svg" alt="Banco do Brasil" />` no header e footer
- [ ] T3: Envolver hero image em condicional: renderizar apenas se `url_hero_image` presente e não vazia
- [ ] T4: Implementar fallback: `<Box sx={{ background: layout.heroBackground, minHeight: layout.imageMinHeight }} />`
- [ ] T5: Testar com dados que possuem hero image e sem hero image

**Notas técnicas:**
O asset `logo-bb.svg` deve ser o grafema oficial do BB (duas letras estilizadas).
O fallback visual utiliza `layout.heroBackground` que já é calculado por
`getLayoutVisualSpec(data)`.

## 5. Notas de Implementação Globais
- Todas as alterações concentram-se em `LandingPageView.tsx` e seus estilos
- Funções utilitárias (`renderGraphicOverlay`, `buildLandingTheme`, `getLayoutVisualSpec`) não devem ser tocadas
- Testar com pelo menos 2 templates diferentes (ex: esporte_convencional, evento_cultural) para garantir ausência de regressão
- O modo `preview` deve continuar exibindo todos os chips — é a forma do backoffice visualizar a configuração
