---
doc_id: "PHASE-F1-EPICS"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-06"
---

# F1 Fundacao Dados e Contratos - Epicos

## Objetivo da Fase

Preparar o modelo `Lead` e os contratos tipados da analise etaria para que o backend consiga expor a nova leitura sem quebrar o dashboard de leads ja existente.

## Gate de Saida da Fase

Uma migration unica adiciona `is_cliente_bb` e `is_cliente_estilo` com upgrade e downgrade validos, os schemas da analise etaria estao tipados e `backend/tests/test_dashboard_leads_endpoint.py` junto de `backend/tests/test_dashboard_leads_report_endpoint.py` continuam verdes com os novos campos.

## Epicos da Fase

| Epic ID | Nome | Objetivo | Status | Documento |
|---|---|---|---|---|
| `EPIC-F1-01` | Migracao Lead Cliente BB | Adicionar os campos nullable e os indices necessarios para suportar cobertura BB e Estilo no modelo `Lead`. | `todo` | [EPIC-F1-01-MIGRACAO-LEAD-CLIENTE-BB.md](./EPIC-F1-01-MIGRACAO-LEAD-CLIENTE-BB.md) |
| `EPIC-F1-02` | Schemas e Contratos Analise Etaria | Definir o contrato Pydantic e o alinhamento de tipos backend/frontend para a resposta `AgeAnalysisResponse`. | `todo` | [EPIC-F1-02-SCHEMAS-E-CONTRATOS-ANALISE-ETARIA.md](./EPIC-F1-02-SCHEMAS-E-CONTRATOS-ANALISE-ETARIA.md) |

## Escopo desta Entrega

Inclui migration, atualizacao do modelo `Lead`, contratos tipados de filtros e resposta, e alinhamento inicial de tipos para consumo do frontend. Exclui a query analitica final, a rota HTTP nova e a interface do dashboard.
