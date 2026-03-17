---
doc_id: "EPIC-F4-01-RETIRADA-CONTROLADA-DO-HEURISTICO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
---

# EPIC-F4-01 - Retirada controlada do heuristico

## Objetivo

Eliminar codigo residual de uniao heuristica que nao faca mais parte do caminho aprovado.

## Resultado de Negocio Mensuravel

O codigo de leitura por evento fica coerente com a fonte canonica final.

## Contexto Arquitetural

- a analise etaria ja usa base canonica em partes centrais
- a fase final deve remover residuos sem reabrir o modelo antigo

## Definition of Done do Epico

- [ ] residuos heuristicas removidos
- [ ] nenhum consumidor analitico principal depende do caminho antigo

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-01-001 | Remover heuristicos residuais e codigo morto | Eliminar helpers, fallbacks e residuos de leitura por evento que nao pertencam mais ao caminho oficial. | 3 | todo | [README](./issues/ISSUE-F4-01-001-REMOVER-HEURISTICOS-RESIDUAIS-E-CODIGO-MORTO/README.md) |

## Artifact Minimo do Epico

- `backend/app/services/dashboard_service.py`
- `backend/app/services/lead_event_service.py`
- `backend/app/routers/dashboard_leads.py`

## Dependencias

- [PRD](../../PRD-DASHBOARD-LEADS.md)
- [Fase](./F4_DASHBOARD_LEADS_EPICS.md)
