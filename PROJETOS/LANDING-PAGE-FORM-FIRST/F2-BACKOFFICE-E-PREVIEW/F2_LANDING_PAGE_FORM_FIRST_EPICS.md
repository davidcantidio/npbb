---
doc_id: "F2_LANDING_PAGE_FORM_FIRST_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-07"
---

# Epicos - LANDING-PAGE-FORM-FIRST / F2 - BACKOFFICE-E-PREVIEW

## Objetivo da Fase

Ajustar o backoffice para refletir a remocao da hero image e atualizar o modo preview para exibir o novo layout form-only com badge de identificacao e chips de mood/categoria em secao colapsavel.

## Gate de Saida da Fase

Campo `hero_image_url` removido do painel "Contexto da landing", mensagem de customizacao atualizada, preview exibe layout form-only com badge "Preview" e chips colapsaveis.

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Ajuste do Painel Contexto da Landing | Remover campo hero_image_url e atualizar mensagem de customizacao controlada no backoffice | nenhuma | todo | [EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md](./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md) |
| EPIC-F2-02 | Adaptacao do Modo Preview | Adaptar o modo isPreview para exibir o novo layout form-only com badge e chips colapsaveis | nenhuma | todo | [EPIC-F2-02-ADAPTACAO-PREVIEW.md](./EPIC-F2-02-ADAPTACAO-PREVIEW.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: nenhuma — pode iniciar imediatamente
- `EPIC-F2-02`: nenhuma — pode ser paralelo ao EPIC-F2-01

```
EPIC-F2-01 (independente)
EPIC-F2-02 (independente)
```

## Escopo desta Fase

### Dentro

- remover campo `hero_image_url` do formulario "Contexto da landing"
- atualizar mensagem de customizacao controlada
- adaptar preview para novo layout form-only
- adicionar badge "Preview" flutuante
- mover chips mood/categoria para secao colapsavel dentro do card
- exibir bloco de info de marca abaixo do GamificacaoBlock apenas em preview

### Fora

- alteracoes no modelo de dados (hero_image_url continua no banco para uso futuro)
- QA cross-template sistematico (fase F3)
- alteracoes no layout da view publica (ja concluido em F1)

## Definition of Done da Fase

- [ ] campo hero_image_url removido do painel "Contexto da landing"
- [ ] mensagem de customizacao controlada atualizada conforme PRD
- [ ] preview exibe layout form-only (nao o layout antigo com hero)
- [ ] badge "Preview" visivel no canto superior direito em modo isPreview
- [ ] chips mood/categoria em secao colapsavel dentro do card em preview
- [ ] bloco de info de marca visivel apenas em preview

## Navegacao Rapida

- [PRD](../PRD-LANDING-FORM-ONLY-v1.0.md)
- [Epic F2-01](./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Epic F2-02](./EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- `[[../PRD-LANDING-FORM-ONLY-v1.0]]`
- `[[./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO]]`
- `[[./EPIC-F2-02-ADAPTACAO-PREVIEW]]`
