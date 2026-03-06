---
doc_id: "PHASE-F1-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F1 Nucleo ETL - Epicos

## Objetivo da Fase

Extrair `transform` e `validate` para `core/leads_etl/` sem quebrar o comportamento atual do pipeline, da CLI ou dos imports legados.

## Gate de Saida da Fase

Todos os testes existentes em `backend/tests/` e `etl/` continuam passando apos a migracao dos modulos para `core/leads_etl/`, sem import de FastAPI, SQLModel ou ORM no novo nucleo compartilhado.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F1-01` | Extrair Nucleo Compartilhado | Migrar normalizacao, segmentacao, framework de validacao e checks para `core/leads_etl/` com reexports compativeis. | `todo` | [EPIC-F1-01-EXTRAIR-NUCLEO-COMPARTILHADO.md](./EPIC-F1-01-EXTRAIR-NUCLEO-COMPARTILHADO.md) |
| `EPIC-F1-02` | Modelo Canonico Lead Row | Definir `core/leads_etl/models/lead_row.py` como contrato unico de linha de lead para ETL e backend. | `todo` | [EPIC-F1-02-MODELO-CANONICO-LEAD-ROW.md](./EPIC-F1-02-MODELO-CANONICO-LEAD-ROW.md) |

## Escopo desta Entrega

Inclui a extracao do nucleo compartilhado, a preservacao de compatibilidade por reexports e a definicao do modelo canonico de uma linha de lead. Exclui endpoints HTTP, persistencia via backend, refatoracao da CLI para consumir o novo core e qualquer mudanca de interface no frontend.
