---
doc_id: "EPIC-F1-02-CRUD-ATIVACOES.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
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

- [ ] Endpoint `POST /eventos/:evento_id/ativacoes` cria ativação
- [ ] Endpoint `GET /eventos/:evento_id/ativacoes` lista ativações do evento
- [ ] Endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id` retorna ativação
- [ ] Endpoint `PATCH /eventos/:evento_id/ativacoes/:ativacao_id` atualiza ativação
- [ ] Endpoints protegidos por autenticação de operador
- [ ] Testes backend cobrindo CRUD

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-02-001 | Schemas e endpoints CRUD de ativações | Implementar schemas Pydantic e endpoints CRUD | 3 | todo | [ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md](./issues/ISSUE-F1-02-001-SCHEMAS-E-ENDPOINTS-CRUD-ATIVACOES.md) |

## Artifact Minimo do Epico

- `backend/app/schemas/`
- `backend/app/api/` ou `backend/app/routers/`
- `backend/tests/`

## Dependencias

- [EPIC-F1-01](./EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F1_LP_EPICS.md)
