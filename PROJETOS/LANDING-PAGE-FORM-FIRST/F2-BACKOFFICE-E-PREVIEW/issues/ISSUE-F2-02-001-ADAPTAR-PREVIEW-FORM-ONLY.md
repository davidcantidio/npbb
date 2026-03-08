---
doc_id: "ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-02-001 - Adaptar Preview Form-Only

## User Story

Como operador do backoffice, quero que o preview da landing exiba o novo layout form-only com um badge "Preview" para saber exatamente como o participante vera a pagina.

## Contexto Tecnico

O modo `isPreview` deve exibir o mesmo layout form-only da view publica, nao o layout antigo com hero. Alem disso, deve incluir:
- Badge "Preview" flutuante no canto superior direito, fora do card, fora do fluxo de conteudo
- O `template_override` configurado no backoffice deve controlar o fundo tematico em tempo real no preview
- Nenhum bloco adicional de marca, checklist ou metadado operacional deve aparecer no preview

## Plano TDD

- Red: preview exibe layout antigo com hero — operador ve interface diferente da que o participante vera.
- Green: preview renderiza layout form-only com FullPageBackground, FormCard, GamificacaoBlock e MinimalFooter; adiciona apenas o badge discreto.
- Refactor: extrair badge como componente reutilizavel; garantir que template_override atualiza fundo em tempo real.

## Criterios de Aceitacao

- Given o modo isPreview, When a landing carrega, Then o layout exibido e form-only (fundo tematico + card centralizado)
- Given o modo isPreview, When a landing carrega, Then um badge "Preview" e visivel no canto superior direito
- Given o modo isPreview, When o template_override e alterado, Then o fundo tematico muda em tempo real
- Given o modo isPreview, When a pagina e rolada, Then nenhum bloco extra de marca ou metadados aparece fora do fluxo publicado
- Given a view publica (isPreview=false), When a landing carrega, Then nenhum badge e visivel

## Definition of Done da Issue

- [x] preview exibe layout form-only
- [x] badge "Preview" flutuante no canto superior direito
- [x] template_override controla fundo tematico no preview
- [x] nenhum bloco de info de marca aparece no preview
- [x] view publica nao afetada

## Tarefas Decupadas

- [x] T1: garantir que isPreview usa o novo layout (nao o antigo)
- [x] T2: criar badge "Preview" com position fixed/absolute no canto superior direito
- [x] T3: remover blocos operacionais extras do preview
- [x] T4: verificar que template_override atualiza fundo tematico no preview
- [x] T5: testar que view publica nao exibe badge

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (modo preview adaptado)

## Dependencias

- [Epic](../EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F2-02-ADAPTACAO-PREVIEW]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
