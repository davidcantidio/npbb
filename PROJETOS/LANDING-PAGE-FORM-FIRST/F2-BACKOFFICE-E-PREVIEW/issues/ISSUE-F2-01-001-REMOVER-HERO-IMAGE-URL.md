---
doc_id: "ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# ISSUE-F2-01-001 - Remover hero_image_url do Painel

## User Story

Como operador do backoffice, quero que o campo `hero_image_url` nao apareca mais no painel "Contexto da landing" para nao criar expectativa errada de que uma hero image sera exibida na landing.

## Contexto Tecnico

O campo `hero_image_url` existe no formulario do backoffice que configura o contexto visual da landing page. Com o novo layout form-only, a hero image nao e mais exibida na view publica. O campo deve ser removido do formulario, mas a coluna no banco de dados permanece para uso futuro (ex: OG tags, thumbnails).

## Plano TDD

- Red: operador ve o campo hero_image_url no painel e preenche — imagem nao aparece na landing.
- Green: remover o campo do formulario do backoffice; dado permanece no modelo.
- Refactor: verificar que nenhuma outra referencia ao campo no frontend espera que ele esteja no formulario.

## Criterios de Aceitacao

- Given o painel "Contexto da landing", When o operador abre o formulario, Then o campo `hero_image_url` nao e visivel
- Given o modelo de dados, When a coluna `hero_image_url` e consultada, Then o dado permanece intacto no banco
- Given o payload da API, When o frontend recebe dados da landing, Then `hero_image_url` pode estar presente no payload sem causar erro

## Definition of Done da Issue

- [ ] campo hero_image_url removido do formulario do backoffice
- [ ] coluna hero_image_url preservada no banco de dados
- [ ] nenhum erro no frontend por ausencia do campo no formulario

## Tarefas Decupadas

- [ ] T1: localizar o componente do formulario "Contexto da landing" no backoffice
- [ ] T2: remover o campo hero_image_url da renderizacao do formulario
- [ ] T3: verificar que o schema de validacao do formulario nao exige o campo
- [ ] T4: testar que o painel carrega e salva sem o campo

## Arquivos Reais Envolvidos

- componente do formulario "Contexto da landing" no backoffice (a identificar)

## Artifact Minimo

- formulario de contexto atualizado sem campo hero_image_url

## Dependencias

- [Epic](../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Fase](../F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [PRD](../../PRD-LANDING-FORM-ONLY-v1.0.md)

## Navegacao Rapida

- `[[../EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO]]`
- `[[../../PRD-LANDING-FORM-ONLY-v1.0]]`
