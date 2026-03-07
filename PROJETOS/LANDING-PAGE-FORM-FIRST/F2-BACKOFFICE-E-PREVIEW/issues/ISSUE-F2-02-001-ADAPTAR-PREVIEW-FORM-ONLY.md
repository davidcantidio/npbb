---
doc_id: "ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F2-02-001 - Adaptar Preview Form-Only

## User Story

Como operador do backoffice, quero que o preview da landing exiba o novo layout form-only com um badge "Preview" para saber exatamente como o participante vera a pagina.

## Contexto Tecnico

O modo `isPreview` deve exibir o mesmo layout form-only da view publica, nao o layout antigo com hero. Alem disso, deve incluir:
- Badge "Preview" flutuante no canto superior direito, fora do card, fora do fluxo de conteudo
- O `template_override` configurado no backoffice deve controlar o fundo tematico em tempo real no preview
- O bloco de info de marca (BrandSummaryCard ou equivalente) deve aparecer abaixo do GamificacaoBlock, apenas em preview

## Plano TDD

- Red: preview exibe layout antigo com hero — operador ve interface diferente da que o participante vera.
- Green: preview renderiza layout form-only com FullPageBackground, FormCard, GamificacaoBlock e MinimalFooter; adiciona badge e bloco de marca.
- Refactor: extrair badge como componente reutilizavel; garantir que template_override atualiza fundo em tempo real.

## Criterios de Aceitacao

- Given o modo isPreview, When a landing carrega, Then o layout exibido e form-only (fundo tematico + card centralizado)
- Given o modo isPreview, When a landing carrega, Then um badge "Preview" e visivel no canto superior direito
- Given o modo isPreview, When o template_override e alterado, Then o fundo tematico muda em tempo real
- Given o modo isPreview, When a pagina e rolada, Then o bloco de info de marca (tagline, template info) aparece abaixo do GamificacaoBlock
- Given a view publica (isPreview=false), When a landing carrega, Then nenhum badge ou bloco de marca e visivel

## Definition of Done da Issue

- [ ] preview exibe layout form-only
- [ ] badge "Preview" flutuante no canto superior direito
- [ ] template_override controla fundo tematico no preview
- [ ] bloco de info de marca visivel apenas em preview
- [ ] view publica nao afetada

## Tarefas Decupadas

- [ ] T1: garantir que isPreview usa o novo layout (nao o antigo)
- [ ] T2: criar badge "Preview" com position fixed/absolute no canto superior direito
- [ ] T3: renderizar BrandSummaryCard (ou equivalente) condicionalmente em isPreview, abaixo do GamificacaoBlock
- [ ] T4: verificar que template_override atualiza fundo tematico no preview
- [ ] T5: testar que view publica nao exibe badge nem bloco de marca

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/LandingPageView.tsx`

## Artifact Minimo

- `frontend/src/components/landing/LandingPageView.tsx` (modo preview adaptado)

## Dependencias

- [Epic](../EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F2-02-ADAPTACAO-PREVIEW]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
