---
doc_id: "ISSUE-F1-02-001-CRIAR-FORMCARD.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F1-02-001 - Criar FormCard

## User Story

Como participante de evento, quero ver o formulario de cadastro em um card limpo e centralizado na tela para preencher rapidamente sem distracao visual.

## Contexto Tecnico

O FormCard e o unico elemento de primeiro plano do novo layout. Encapsula titulo (derivado da ativacao), subtitulo opcional, callout `mensagem_qrcode`, campos do formulario, checkbox LGPD e botao CTA. Os tokens visuais do card (background, border, sombra) variam por template e sao derivados de `getLayoutVisualSpec(data)`. O card e centralizado via Flexbox no viewport.

Responsividade:
- Mobile (375px): largura `min(92vw, 440px)`, padding `20px`
- Tablet (768px): largura `min(480px, 90vw)`, padding `32px`
- Desktop (1280px): largura `min(520px, 90vw)`, padding `32px`

## Plano TDD

- Red: formulario renderiza sem card (diretamente no body) — sem centralizacao, sem elevacao.
- Green: criar FormCard com Flexbox centralizado, borderRadius 24px, elevacao MUI 8, padding responsivo.
- Refactor: parametrizar background e border do card por template; garantir que titulo, subtitulo e callout sao opcionais e derivados corretamente.

## Criterios de Aceitacao

- Given qualquer template, When a landing carrega em 375px × 667px, Then o card do formulario e visivel above the fold sem scroll
- Given o template `corporativo`, When o card renderiza, Then o background e `#FFFFFF` solido e a borda e `2px solid rgba(252, 252, 48, 0.6)`
- Given o template `esporte_convencional`, When o card renderiza, Then o background e `rgba(255, 255, 255, 0.96)` e a sombra e `0 8px 32px rgba(0,0,0,0.35)`
- Given uma ativacao com `mensagem_qrcode`, When o card renderiza, Then um `<Alert severity="info">` aparece acima dos campos
- Given uma ativacao sem `descricao`, When o card renderiza, Then nenhum subtitulo e exibido
- Given qualquer breakpoint, When o card renderiza, Then o card esta centralizado horizontalmente

## Definition of Done da Issue

- [ ] componente FormCard criado em `frontend/src/components/landing/`
- [ ] card centralizado horizontal e verticalmente com Flexbox
- [ ] responsivo em 375px, 768px e 1280px conforme especificacao
- [ ] titulo usa `ativacao.nome ?? evento.nome`
- [ ] subtitulo usa `ativacao.descricao ?? evento.descricao_curta` (opcional)
- [ ] callout `mensagem_qrcode` renderiza como Alert acima dos campos (se presente)
- [ ] borderRadius 24px, elevacao e fundo conforme template
- [ ] CTA usa `evento.cta_personalizado ?? template.cta_text`

## Tarefas Decupadas

- [ ] T1: criar arquivo `FormCard.tsx` com props para dados da ativacao, evento e tema
- [ ] T2: implementar centralizacao via Flexbox (`alignItems: center`, `justifyContent: center`)
- [ ] T3: aplicar tokens visuais do card por template (background, border, sombra) via `getLayoutVisualSpec`
- [ ] T4: renderizar titulo derivado com typography `h5` bold
- [ ] T5: renderizar subtitulo opcional com typography `body2`
- [ ] T6: renderizar callout `mensagem_qrcode` como `<Alert severity="info">` condicional
- [ ] T7: aplicar breakpoints responsivos (mobile 92vw, tablet 480px, desktop 520px)

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`
- `frontend/src/components/landing/landingThemeBuilder.ts` (ou equivalente)

## Artifact Minimo

- `frontend/src/components/landing/FormCard.tsx`

## Dependencias

- [Epic](../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE.md)
- [Fase](../F1_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F1-02-CARD-FORMULARIO-E-RODAPE]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
