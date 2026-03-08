---
doc_id: "F2_LANDING_PAGE_FORM_FIRST_EPICS.md"
version: "1.3"
status: "done"
owner: "PM"
last_updated: "2026-03-08"
---

# Epicos - LANDING-PAGE-FORM-FIRST / F2 - BACKOFFICE-E-PREVIEW

## Objetivo da Fase

Ajustar o backoffice, o preview e os contratos de dados para refletir a remocao definitiva da hero image e do modelo legado. O preview passa a espelhar a landing publicada com apenas um badge discreto de identificacao.

## Gate de Saida da Fase

Campo `hero_image_url` removido do painel, da API e do banco; mensagem de customizacao atualizada; preview exibe layout form-only com badge "Preview" e sem blocos operacionais extras.

## Gate de Auditoria da Fase

- estado_do_gate: `approved`
- ultima_auditoria: `R01`
- veredito_atual: `go`
- relatorio_mais_recente: [RELATORIO-AUDITORIA-F2-R01](./auditorias/RELATORIO-AUDITORIA-F2-R01.md)
- log_do_projeto: [AUDIT-LOG](../AUDIT-LOG.md)
- convencao_de_relatorios: [README](./auditorias/README.md)

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Ajuste do Painel Contexto da Landing | Remover campo hero_image_url, atualizar mensagem e alinhar contratos/schema/banco ao novo produto | nenhuma | done | [EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md](./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md) |
| EPIC-F2-02 | Adaptacao do Modo Preview | Adaptar o modo isPreview para espelhar o layout form-only com badge discreto e sem blocos extras | nenhuma | done | [EPIC-F2-02-ADAPTACAO-PREVIEW.md](./EPIC-F2-02-ADAPTACAO-PREVIEW.md) |

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
- remover `hero_image_url` dos schemas, payloads e banco

### Fora

- QA cross-template sistematico (fase F3)
- alteracoes no layout da view publica (ja concluido em F1)

## Definition of Done da Fase

- [x] campo hero_image_url removido do painel "Contexto da landing"
- [x] mensagem de customizacao controlada atualizada conforme PRD
- [x] preview exibe layout form-only (nao o layout antigo com hero)
- [x] badge "Preview" visivel no canto superior direito em modo isPreview
- [x] hero_image_url removido dos schemas, payloads e banco
- [x] nenhum bloco de marca, checklist ou chip operacional aparece no preview
- [x] gate de auditoria aprovado em `auditorias/RELATORIO-AUDITORIA-F2-R01.md`

## Navegacao Rapida

- [Intake](../INTAKE-LANDING-PAGE-FORM-FIRST.md)
- [PRD](../PRD-LANDING-PAGE-FORM-FIRST.md)
- [Audit Log](../AUDIT-LOG.md)
- [Epic F2-01](./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO.md)
- [Epic F2-02](./EPIC-F2-02-ADAPTACAO-PREVIEW.md)
- `[[../INTAKE-LANDING-PAGE-FORM-FIRST]]`
- `[[../PRD-LANDING-PAGE-FORM-FIRST]]`
- `[[./EPIC-F2-01-AJUSTE-PAINEL-CONTEXTO]]`
- `[[./EPIC-F2-02-ADAPTACAO-PREVIEW]]`
