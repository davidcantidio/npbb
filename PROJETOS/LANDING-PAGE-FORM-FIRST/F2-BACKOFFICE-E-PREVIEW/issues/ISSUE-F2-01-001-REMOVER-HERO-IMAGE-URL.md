---
doc_id: "ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# ISSUE-F2-01-001 - Remover hero_image_url do Painel

## User Story

Como operador do backoffice, quero que o campo `hero_image_url` nao apareca mais no painel "Contexto da landing" para nao criar expectativa errada de que uma hero image sera exibida na landing.

## Contexto Tecnico

O campo `hero_image_url` existia no formulario do backoffice que configura o contexto visual da landing page. Com o novo layout form-only, a hero image saiu do produto: o campo e removido do formulario, dos payloads, dos schemas e do banco de dados.

## Plano TDD

- Red: operador ve o campo hero_image_url no painel e preenche — imagem nao aparece na landing.
- Green: remover o campo do formulario do backoffice e bloquear seu uso no contrato da API.
- Refactor: verificar que nenhuma outra referencia ao campo permanece no frontend, backend ou migration.

## Criterios de Aceitacao

- Given o painel "Contexto da landing", When o operador abre o formulario, Then o campo `hero_image_url` nao e visivel
- Given o payload da API, When o frontend ou cliente envia `hero_image_url`, Then a requisicao falha explicitamente por campo extra
- Given o modelo de dados, When a migration e aplicada, Then a coluna `hero_image_url` deixa de existir no banco

## Definition of Done da Issue

- [x] campo hero_image_url removido do formulario do backoffice
- [x] schema e payloads nao aceitam mais hero_image_url
- [x] coluna hero_image_url removida do banco de dados

## Tarefas Decupadas

- [x] T1: localizar o componente do formulario "Contexto da landing" no backoffice
- [x] T2: remover o campo hero_image_url da renderizacao do formulario
- [x] T3: atualizar schema e validacao para rejeitar o campo
- [x] T4: remover o campo do modelo/payload e adicionar migration

## Arquivos Reais Envolvidos

- componente do formulario "Contexto da landing" no backoffice (a identificar)

## Artifact Minimo

- formulario de contexto, contrato de API e banco atualizados sem hero_image_url

## Dependencias

- [Epic](../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-PAGE-FORM-FIRST.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO]]`
- `[[../../PRD-LANDING-PAGE-FORM-FIRST]]`
