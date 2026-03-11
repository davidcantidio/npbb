---
doc_id: "EPIC-F1-03-QR-E-ENDPOINT-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F1-03 - Geração de QR e Endpoint de Landing

## Objetivo

Implementar serviço de geração de QR-code único por ativação e endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing` que retorna payload da landing com contexto de evento, ativação e formulário configurado.

## Resultado de Negocio Mensuravel

Cada ativação possui QR-code único; a landing pode ser carregada com contexto correto de evento e ativação via API.

## Contexto Arquitetural

- URL do QR: `/eventos/:evento_id/ativacoes/:ativacao_id` (ou `/e/:evento_id/a/:ativacao_id`)
- Lib `qrcode` em Python ou endpoint que retorna SVG/PNG
- Endpoint de landing público (sem login) para preenchimento de leads
- Payload inclui: evento, ativação, formulário configurado, template; flag `lead_reconhecido` quando cookie/token válido presente

## Definition of Done do Epico

- [ ] Serviço gera QR-code único por ativação (imagem ou URL)
- [ ] Campo `qr_code_url` da ativação populado na criação/atualização
- [ ] Endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing` retorna payload esperado
- [ ] Payload inclui flag `lead_reconhecido` (inicialmente false)
- [ ] Testes backend cobrindo geração de QR e endpoint de landing

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-03-001 | Serviço de geração de QR | Implementar geração de QR-code por ativação | 2 | todo | [ISSUE-F1-03-001-SERVICO-GERACAO-QR.md](./issues/ISSUE-F1-03-001-SERVICO-GERACAO-QR.md) |
| ISSUE-F1-03-002 | Endpoint GET landing | Endpoint que retorna payload da landing com contexto | 3 | todo | [ISSUE-F1-03-002-ENDPOINT-GET-LANDING.md](./issues/ISSUE-F1-03-002-ENDPOINT-GET-LANDING.md) |

## Artifact Minimo do Epico

- `backend/app/services/` (QR)
- `backend/app/api/` ou `backend/app/routers/`
- `backend/tests/`

## Dependencias

- [EPIC-F1-01](./EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F1_LP_EPICS.md)
