---
doc_id: "EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# EPIC-F2-01 - Ajuste do Painel Contexto da Landing

## Objetivo

Remover o campo `hero_image_url` do formulario "Contexto da landing", atualizar a mensagem de customizacao controlada e alinhar schema, payloads e banco ao novo contrato sem hero image.

## Resultado de Negocio Mensuravel

O operador do backoffice nao ve mais o campo `hero_image_url`, a API rejeita esse campo explicitamente e o banco deixa de persisti-lo. A mensagem de customizacao controlada passa a refletir o novo modelo.

## Contexto Arquitetural

- o campo `hero_image_url` existia no formulario do backoffice mas deixou de existir no produto
- o contrato passa a ser estrito para rejeitar esse campo em create/update
- a coluna do banco e removida por migration
- a mensagem de customizacao controlada precisa ser atualizada conforme PRD secao 06.3

## Definition of Done do Epico

- [x] campo `hero_image_url` removido do formulario "Contexto da landing"
- [x] mensagem de customizacao controlada atualizada conforme PRD
- [x] schema, payloads e banco alinhados ao novo contrato sem hero image

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Remover hero_image_url do Painel | Remover o campo hero_image_url do formulario de contexto da landing e do contrato de dados | 2 | done | [ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md](./issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md) |
| ISSUE-F2-01-002 | Atualizar Mensagem Customizacao | Atualizar a mensagem de customizacao controlada no backoffice | 1 | done | [ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md](./issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md) |

## Artifact Minimo do Epico

- formulario "Contexto da landing" atualizado no backoffice

## Dependencias

- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Fase](./F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL]]`
- `[[./issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
