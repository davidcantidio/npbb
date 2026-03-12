---
doc_id: "EPIC-F1-02-CRUD-ATIVACOES.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
---

# EPIC-F1-02 - CRUD de Ativações

## Objetivo

Expor endpoints REST para criar, editar, listar e obter ativações, protegidos por autenticação de operador, conforme PRD seção 7.1.

## Resultado de Negocio Mensuravel

O operador pode configurar ativações (nome, descrição, tipo de conversão única/múltipla) via API autenticada.

## Contexto Arquitetural

- Backend FastAPI em `backend/app/`
- Autenticação JWT existente para operadores
- Schemas Pydantic para request/response
- Rotas sob prefixo de eventos: `/eventos/:evento_id/ativacoes`

## Definition of Done do Epico

- [x] Endpoint `POST /eventos/:evento_id/ativacoes` cria ativação
- [x] Endpoint `GET /eventos/:evento_id/ativacoes` lista ativações do evento
- [x] Endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id` retorna ativação
- [x] Endpoint `PATCH /eventos/:evento_id/ativacoes/:ativacao_id` atualiza ativação
- [x] Endpoints protegidos por autenticação de operador
- [x] Testes backend cobrindo CRUD

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Schemas e endpoints CRUD de ativações | Implementar schemas Pydantic e endpoints CRUD | 3 | done | [ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md](./issues/ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md) |

## Artifact Minimo do Epico

- `backend/app/schemas/`
- `backend/app/api/` ou `backend/app/routers/`
- `backend/tests/`

## Dependencias

- [EPIC-F1-01](./EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F1_LP_EPICS.md)
