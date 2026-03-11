---
doc_id: "EPIC-F4-02-VISUALIZACAO-CONVERSOES-METRICAS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F4-02 - Visualização de Conversões e Métricas

## Objetivo

Expor visualização de conversões por ativação e métricas (leading: ativações por evento, conversões por ativação, taxa de reconhecimento; lagging: conversões atribuíveis, redução de abandono). Conforme PRD seções 9 e 12 (Fase 4).

## Resultado de Negocio Mensuravel

O operador visualiza conversões por ativação e métricas para avaliar desempenho das ativações.

## Contexto Arquitetural

- Backend: endpoints ou extensão de endpoints para agregar conversões
- Frontend: tabela ou cards de conversões por ativação; KPIs
- Métricas: número de ativações por evento, conversões por ativação, taxa de reconhecimento

## Definition of Done do Epico

- [ ] Endpoint ou dados para listar conversões por ativação
- [ ] Interface exibe conversões por ativação
- [ ] Métricas leading acessíveis (ativações, conversões, taxa reconhecimento)
- [ ] Observabilidade básica (logs, métricas expostas)
- [ ] Testes

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F4-02-001 | Endpoint e UI de conversões por ativação | Backend: agregar conversões; Frontend: exibir | 3 | todo | [ISSUE-F4-02-001-ENDPOINT-E-UI-CONVERSOES.md](./issues/ISSUE-F4-02-001-ENDPOINT-E-UI-CONVERSOES.md) |
| ISSUE-F4-02-002 | Métricas e observabilidade | KPIs leading/lagging; logs e métricas | 2 | todo | [ISSUE-F4-02-002-METRICAS-E-OBSERVABILIDADE.md](./issues/ISSUE-F4-02-002-METRICAS-E-OBSERVABILIDADE.md) |

## Artifact Minimo do Epico

- `backend/app/api/` ou `backend/app/services/`
- `frontend/src/` (visualização)
- `backend/tests/`

## Dependencias

- [F1](../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [F2](../F2-FLUXO-CPF-FIRST-E-CONVERSAO/F2_LP_EPICS.md)
- [F3](../F3-RECONHECIMENTO-E-EXPERIENCIA-FLUIDA/F3_LP_EPICS.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F4_LP_EPICS.md)
