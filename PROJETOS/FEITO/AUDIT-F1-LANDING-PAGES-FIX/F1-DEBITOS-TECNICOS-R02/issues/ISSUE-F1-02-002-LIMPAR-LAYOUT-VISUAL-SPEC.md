---
doc_id: "ISSUE-F1-02-002-LIMPAR-LAYOUT-VISUAL-SPEC.md"
version: "1.0"
status: "done"
owner: "PM"
task_instruction_mode: "required"
last_updated: "2026-03-08"
---

# ISSUE-F1-02-002 - Limpar LayoutVisualSpec de campos mortos de hero

## User Story

Como engenheiro que le o tipo LayoutVisualSpec, quero que ele nao contenha campos semanticos de hero nao consumidos pelo layout form-only, para evitar confusao e investigacao desnecessaria.

## Contexto Tecnico

Apos a decomposicao (ISSUE-F1-02-001), LayoutVisualSpec e getLayoutVisualSpec estao em `landingLayout.ts`. Campos mortos (sem consumidor em componentes de renderizacao): heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight. Campo a renomear: heroTextColor -> pageTextColor (consumido por LandingPreviewBadge para contraste do badge).

## Plano TDD

- Red: nao aplicavel (refatoracao de tipo e removendo codigo morto)
- Green: remover campos mortos, renomear heroTextColor, atualizar consumidor e testes
- Refactor: garantir que formOnlySurface, FormCard, LandingPageView e LandingPreviewBadge continuem funcionando

## Criterios de Aceitacao

- Given LayoutVisualSpec, When inspecionado, Then nao contem heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight
- Given LayoutVisualSpec, When inspecionado, Then contem pageTextColor (renomeado de heroTextColor)
- Given LandingPreviewBadge, When renderizado, Then usa layout.pageTextColor
- Given grep por campos removidos em *.tsx e *.ts, When executado, Then zero ocorrencias (exceto testes atualizados)
- Given tsc --noEmit e suite de testes da landing, When executados, Then passam

## Definition of Done da Issue

- [x] Inventario de campos mortos documentado (comentario ou issue)
- [x] Campos mortos removidos do tipo LayoutVisualSpec em landingLayout.ts
- [x] heroTextColor renomeado para pageTextColor em tipo, getLayoutVisualSpec e LandingPreviewBadge
- [x] landingSections.types.ts e formOnlySurface.ts atualizados se necessario (tipos derivados)
- [x] Testes que referenciam campos removidos/renomeados atualizados
- [x] tsc --noEmit passa (sem erros em landing; erros pre-existentes em dashboard)
- [x] Suite de testes da landing passa

## Tarefas Decupadas

- [x] T1: Inventariar campos mortos via grep (confirmar lista)
- [x] T2: Remover campos mortos do tipo LayoutVisualSpec em landingLayout.ts
- [x] T3: Renomear heroTextColor para pageTextColor em tipo, getLayoutVisualSpec e LandingPreviewBadge
- [x] T4: Remover calculo dos campos mortos de getLayoutVisualSpec() em landingLayout.ts
- [x] T5: Atualizar testes que referenciam campos removidos/renomeados
- [x] T6: Executar tsc --noEmit e suite de testes da landing

## Instructions por Task

### T1

- Executar grep em frontend/src/components/landing para confirmar quais campos de LayoutVisualSpec sao lidos em componentes de renderizacao (*.tsx)
- Lista esperada de campos mortos: heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight
- Documentar como comentario no topo do PR ou no fechamento da issue

### T2

- Editar `frontend/src/components/landing/landingLayout.ts`
- Remover do tipo LayoutVisualSpec: heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight
- Manter: formCardBackground, formCardBorder, formCardShadow, footerTextColor, buttonVariant, buttonColor, buttonStyles
- Manter heroTextColor temporariamente (sera renomeado em T3)

### T3

- Em landingLayout.ts: renomear heroTextColor para pageTextColor no tipo LayoutVisualSpec e em todos os retornos de getLayoutVisualSpec()
- Em LandingPreviewBadge.tsx: alterar layout.heroTextColor para layout.pageTextColor
- Em landingSections.types.ts: o tipo LandingFormCardProps e LandingGamificacaoSectionProps usam LayoutVisualSpec — nao precisa alterar (o tipo LayoutVisualSpec ja tera pageTextColor)

### T4

- Em getLayoutVisualSpec() em landingLayout.ts: remover todas as linhas que atribuem valores a heroBackground, heroMinHeight, heroGridColumns, heroTextCardBackground, heroTextCardBorder, contentGridColumns, imageMinHeight
- Manter apenas: formCardSpec (spread), footerTextColor, buttonVariant, buttonColor, buttonStyles, pageTextColor
- Simplificar os branches (editorial, dark-overlay, full-bleed) para retornar apenas os campos usados

### T5

- Em FormCard.test.tsx: se houver expectativas que leem layout.formCardBackground, layout.formCardBorder, layout.formCardShadow — manter (esses campos permanecem)
- Em landingStyle.test.tsx: se houver expectativas que leem getLayoutVisualSpec ou campos do retorno — atualizar para pageTextColor onde havia heroTextColor
- Em LandingPreviewBadge: nenhum teste direto de heroTextColor esperado; validar que testes de acessibilidade ou snapshot nao quebram

### T6

- Executar `cd frontend && npx tsc --noEmit`
- Executar suite de testes da landing (mesmo comando da ISSUE-F1-02-001)
- Registrar resultado no fechamento da issue

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/landingLayout.ts`
- `frontend/src/components/landing/LandingPreviewBadge.tsx`
- `frontend/src/components/landing/landingSections.types.ts`
- `frontend/src/components/landing/__tests__/FormCard.test.tsx`
- `frontend/src/components/landing/__tests__/landingStyle.test.tsx` (se existir)

## Artifact Minimo

- LayoutVisualSpec sem campos mortos; pageTextColor em uso; tsc e testes passando

## Dependencias

- [Epic](../EPIC-F1-02-REFATORACAO-LANDING-STYLE.md)
- [Fase](../F1_AUDIT_F1_LANDING_PAGES_FIX_EPICS.md)
- [ISSUE-F1-02-001](./ISSUE-F1-02-001-DECOMPOR-LANDING-STYLE.md) (deve estar done)

## Navegacao Rapida

- `[[../EPIC-F1-02-REFATORACAO-LANDING-STYLE]]`
- `[[./ISSUE-F1-02-001-DECOMPOR-LANDING-STYLE]]`
