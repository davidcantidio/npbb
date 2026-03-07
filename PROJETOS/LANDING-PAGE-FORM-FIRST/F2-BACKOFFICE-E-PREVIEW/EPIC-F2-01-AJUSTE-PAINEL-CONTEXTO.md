---
doc_id: "EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# EPIC-F2-01 - Ajuste do Painel Contexto da Landing

## Objetivo

Remover o campo `hero_image_url` do formulario "Contexto da landing" no backoffice e atualizar a mensagem de customizacao controlada para refletir que o visual do fundo e determinado pelo template selecionado.

## Resultado de Negocio Mensuravel

O operador do backoffice nao ve mais o campo `hero_image_url` (evitando expectativa errada de que uma hero image sera exibida) e le uma mensagem atualizada sobre customizacao controlada.

## Contexto Arquitetural

- o campo `hero_image_url` existe no formulario do backoffice mas nao e mais exibido na view publica
- o dado permanece no modelo de dados para uso futuro (ex: OG tags, thumbnails)
- apenas o campo do formulario do backoffice e removido, nao a coluna do banco
- a mensagem de customizacao controlada precisa ser atualizada conforme PRD secao 06.3

## Definition of Done do Epico

- [ ] campo `hero_image_url` removido do formulario "Contexto da landing"
- [ ] mensagem de customizacao controlada atualizada conforme PRD
- [ ] nenhuma alteracao no modelo de dados ou banco

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Remover hero_image_url do Painel | Remover o campo hero_image_url do formulario de contexto da landing no backoffice | 2 | todo | [ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md](./issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL.md) |
| ISSUE-F2-01-002 | Atualizar Mensagem Customizacao | Atualizar a mensagem de customizacao controlada no backoffice | 1 | todo | [ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md](./issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO.md) |

## Artifact Minimo do Epico

- formulario "Contexto da landing" atualizado no backoffice

## Dependencias

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Fase](./F2_LANDING_PAGE_FORM_FIRST_EPICS.md)
- [Decision Protocol](../DECISION-PROTOCOL.md)

## Navegacao Rapida

- `[[./issues/ISSUE-F2-01-001-REMOVER-HERO-IMAGE-URL]]`
- `[[./issues/ISSUE-F2-01-002-ATUALIZAR-MENSAGEM-CUSTOMIZACAO]]`
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
