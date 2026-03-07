---
doc_id: "ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F2-02-002 - Mover Chips para Secao Colapsavel

## User Story

Como operador do backoffice, quero ver os chips de mood e categoria dentro do card do formulario em uma secao colapsavel no preview para ter contexto operacional sem poluir a visualizacao do layout real.

## Contexto Tecnico

Os chips de `mood` e `categoria` eram exibidos no hero/header do layout antigo. Com a remocao do hero, eles devem ser movidos para uma secao colapsavel dentro do FormCard, visivel apenas em `isPreview`. A secao deve usar um Accordion/Collapse do MUI, posicionada abaixo dos campos do formulario.

## Plano TDD

- Red: chips de mood/categoria nao aparecem em nenhum lugar apos remocao do hero.
- Green: adicionar secao colapsavel "Metadados" dentro do FormCard, renderizada apenas quando isPreview=true, com chips de mood e categoria.
- Refactor: extrair secao de metadados como componente; garantir que nao interfere com submit do formulario.

## Criterios de Aceitacao

- Given o modo isPreview, When o card do formulario renderiza, Then uma secao colapsavel "Metadados" aparece abaixo dos campos
- Given a secao "Metadados" expandida, When observada, Then os chips de mood e categoria estao presentes
- Given a view publica (isPreview=false), When o card renderiza, Then nenhuma secao de metadados e visivel
- Given a secao de metadados, When o formulario e submetido, Then a secao nao interfere com o submit

## Definition of Done da Issue

- [ ] secao colapsavel com chips de mood e categoria dentro do FormCard
- [ ] visivel apenas em isPreview
- [ ] nao interfere com submit do formulario
- [ ] usa Accordion/Collapse do MUI

## Tarefas Decupadas

- [ ] T1: criar secao colapsavel "Metadados" usando MUI Accordion dentro do FormCard
- [ ] T2: renderizar chips de mood e categoria dentro da secao
- [ ] T3: condicionar renderizacao a isPreview=true
- [ ] T4: testar que submit funciona normalmente com secao presente
- [ ] T5: testar que view publica nao exibe a secao

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/FormCard.tsx` (ou LandingPageView.tsx)

## Artifact Minimo

- secao colapsavel de metadados no FormCard (apenas preview)

## Dependencias

- [Epic](../EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Issue 001](./ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md)

## Navegacao Rapida

- `[[../EPIC-F2-02-ADAPTACAO-PREVIEW]]`
- `[[./ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
