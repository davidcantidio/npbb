---
doc_id: "ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F2-01-002 - Atualizar Mensagem Customizacao

## User Story

Como operador do backoffice, quero ver uma mensagem atualizada sobre customizacao controlada para entender que o visual do fundo e determinado pelo template e nao por uma hero image.

## Contexto Tecnico

A mensagem atual diz: "Customizacao controlada: somente template_override, hero_image_url, cta_personalizado e descricao_curta podem ser alterados sem sair do catalogo homologado da marca BB."

Deve ser atualizada para: "Customizacao controlada: somente template_override, cta_personalizado e descricao_curta podem ser alterados sem sair do catalogo homologado da marca BB. O visual do fundo e determinado pelo template selecionado."

## Plano TDD

- Red: mensagem atual menciona hero_image_url — informacao incorreta apos remocao do campo.
- Green: atualizar o texto da mensagem conforme PRD secao 06.3.
- Refactor: verificar se a mensagem e hardcoded ou vem de constante; centralizar se necessario.

## Criterios de Aceitacao

- Given o painel "Contexto da landing", When o operador visualiza o aviso de customizacao, Then a mensagem nao menciona `hero_image_url`
- Given o painel "Contexto da landing", When o operador visualiza o aviso, Then a mensagem inclui "O visual do fundo e determinado pelo template selecionado."

## Definition of Done da Issue

- [ ] mensagem de customizacao controlada atualizada conforme PRD secao 06.3
- [ ] nenhuma referencia a hero_image_url na mensagem

## Tarefas Decupadas

- [ ] T1: localizar a string da mensagem de customizacao no codigo
- [ ] T2: atualizar o texto conforme PRD secao 06.3
- [ ] T3: validar visualmente no painel

## Arquivos Reais Envolvidos

- componente do painel "Contexto da landing" no backoffice (a identificar)

## Artifact Minimo

- mensagem atualizada no painel de contexto

## Dependencias

- [Epic](../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Issue 001](./ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO]]`
- `[[./ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
