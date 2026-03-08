---
doc_id: "ISSUE-F2-02-002-MOVER-CHIPS-SECAO-COLAPSAVEL.md"
version: "1.1"
status: "cancelled"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-02-002 - Mover Chips para Secao Colapsavel

## User Story

Como operador do backoffice, eu queria ver chips de mood e categoria dentro do card do formulario em uma secao colapsavel no preview, mas essa necessidade foi removida pela decisao de produto de manter o preview identico a landing publicada.

## Contexto Tecnico

Os chips de `mood` e `categoria` eram exibidos no hero/header do layout antigo. A decisao registrada em `DECISION-PROTOCOL.md` removeu esse escopo: o preview nao deve exibir metadados extras, para continuar fiel a landing publicada.

## Plano TDD

- status_final: cancelada por decisao de produto
- motivo: o preview ficou restrito a badge discreto de `Preview`, sem chips, checklist ou bloco de marca
- acao_substituta: nenhuma implementacao necessaria; cobertura de testes deve garantir ausencia desses elementos

## Criterios de Aceitacao

- Given o modo isPreview, When o card do formulario renderiza, Then nenhuma secao colapsavel de metadados aparece
- Given a view publica (isPreview=false), When o card renderiza, Then nenhum chip de mood/categoria e visivel

## Definition of Done da Issue

- [x] issue cancelada formalmente
- [x] nenhuma implementacao aberta permanece associada a chips de preview

## Tarefas Decupadas

- [x] T1: registrar cancelamento canonico da issue
- [x] T2: remover a expectativa de chips/metadados dos testes de preview

## Arquivos Reais Envolvidos

- `frontend/src/components/landing/FormCard.tsx` (ou LandingPageView.tsx)

## Artifact Minimo

- nenhuma; issue cancelada

## Dependencias

- [Epic](../EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Issue 001](./ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY.md)

## Navegacao Rapida

- `[[../EPIC-F2-02-ADAPTACAO-PREVIEW]]`
- `[[./ISSUE-F2-02-001-ADAPTAR-PREVIEW-FORM-ONLY]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
