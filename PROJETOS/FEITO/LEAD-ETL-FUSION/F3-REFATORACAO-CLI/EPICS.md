---
doc_id: "PHASE-F3-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-03"
---

# F3 Refatoracao CLI - Epicos

## Objetivo da Fase

Fazer a CLI e o orchestrator consumirem `core/leads_etl/` como nucleo compartilhado, sem alterar a interface publica dos comandos existentes.

## Gate de Saida da Fase

`cli_extract.py` e `cli_spec.py` continuam funcionando sem alteracoes de interface, e `etl/orchestrator/s1_core.py` ate `etl/orchestrator/s4_core.py` importam de `core/leads_etl/` em vez de caminhos relativos internos.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F3-01` | Orchestrator Consume Core | Atualizar o orchestrator para consumir `column_normalize`, `segment_mapper` e validacao a partir do core compartilhado. | `todo` | [EPIC-F3-01-ORCHESTRATOR-CONSUME-CORE.md](./EPIC-F3-01-ORCHESTRATOR-CONSUME-CORE.md) |
| `EPIC-F3-02` | Remocao Duplicacoes | Reduzir `etl/transform/` e `etl/validate/` a reexports e preparar a remocao do normalize legado do backend. | `todo` | [EPIC-F3-02-REMOCAO-DUPLICACOES.md](./EPIC-F3-02-REMOCAO-DUPLICACOES.md) |

## Escopo desta Entrega

Inclui adaptacao do orchestrator, compatibilidade da CLI e reducao de duplicacoes entre caminhos legados e o novo core. Exclui mudancas de UI, novos endpoints HTTP e qualquer alteracao de produto fora do necessario para consolidar a arquitetura compartilhada.
