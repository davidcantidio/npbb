---
doc_id: "PHASE-F4-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F4 Validacao Docs e Gate - Epicos

## Objetivo da Fase

Fechar a entrega v1.0 com testes de regressao, documentacao OpenAPI e evidencia objetiva de que os criterios de aceite do PRD foram cumpridos.

## Gate de Saida da Fase

Os testes backend e frontend relevantes passam, o endpoint aparece corretamente na documentacao OpenAPI, existe evidencia consolidada em `artifacts/dashboard-leads-etaria/phase-f4/validation-summary.md` e a decisao de promover a fase fica auditavel para posterior movimentacao em `feito/`.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F4-01` | Testes Backend e Frontend | Cobrir os cenarios criticos de faixa etaria, cobertura BB, autenticacao e renderizacao principal do dashboard. | `todo` | [EPIC-F4-01-TESTES-BACKEND-E-FRONTEND.md](./EPIC-F4-01-TESTES-BACKEND-E-FRONTEND.md) |
| `EPIC-F4-02` | OpenAPI e Documentacao Operacional | Garantir contrato publicado, exemplos de resposta e orientacao operacional sobre cobertura BB e leitura de media/mediana. | `todo` | [EPIC-F4-02-OPENAPI-E-DOCUMENTACAO-OPERACIONAL.md](./EPIC-F4-02-OPENAPI-E-DOCUMENTACAO-OPERACIONAL.md) |
| `EPIC-F4-03` | Gate de Aceite e Evidencias | Consolidar a validacao cross-camada e a decisao de promocao da entrega v1.0. | `todo` | [EPIC-F4-03-GATE-DE-ACEITE-E-EVIDENCIAS.md](./EPIC-F4-03-GATE-DE-ACEITE-E-EVIDENCIAS.md) |

## Escopo desta Entrega

Inclui testes automatizados, revisao da documentacao exposta, artefatos de validacao e checklist final do PRD. Exclui novos requisitos de produto e qualquer dashboard alem da analise etaria por evento.
