---
doc_id: "EPIC-F3-01-MECANISMO-RECONHECIMENTO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F3-01 - Mecanismo de Reconhecimento

## Objetivo

Implementar cookie HTTP-only `lp_lead_token` e token na URL para reconhecimento de leads entre ativações do mesmo evento. POST /leads retorna token; GET landing valida e retorna lead_reconhecido. Conforme PRD seções 5.1, 5.5, 7.1 e 7.2.

## Resultado de Negocio Mensuravel

O lead que converteu em uma ativação é reconhecido ao acessar outra ativação do mesmo evento, sem repetir CPF.

## Contexto Arquitetural

- Cookie: `lp_lead_token`, valor opaco (hash/UUID), TTL 7 dias, domínio do frontend
- Token na URL: `?token=` para fallback (link compartilhado)
- Tabela lead_reconhecimento_token: lead_id, evento_id, token_hash, expires_at
- Endpoint GET /leads/reconhecer?token= valida e retorna se reconhecido

## Definition of Done do Epico

- [ ] POST /leads retorna token_reconhecimento no response
- [ ] Frontend armazena token em cookie lp_lead_token (HTTP-only quando possível)
- [ ] GET landing aceita cookie e/ou ?token= e retorna lead_reconhecido
- [ ] Endpoint GET /leads/reconhecer?token= valida token
- [ ] Token com TTL 7 dias
- [ ] Testes backend e E2E

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F3-01-001 | Geração e validação de token de reconhecimento | Backend: gerar token, persistir, validar | 3 | todo | [ISSUE-F3-01-001-GERACAO-E-VALIDACAO-TOKEN.md](./issues/ISSUE-F3-01-001-GERACAO-E-VALIDACAO-TOKEN.md) |
| ISSUE-F3-01-002 | Cookie e integração com GET landing | Frontend: armazenar cookie; GET landing com lead_reconhecido | 3 | todo | [ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md](./issues/ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md) |

## Artifact Minimo do Epico

- `backend/app/services/` (token)
- `backend/app/api/`
- `frontend/src/` (cookie)
- `backend/tests/`

## Dependencias

- [F1](../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [F2](../F2-FLUXO-CPF-FIRST-E-CONVERSAO/F2_LP_EPICS.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F3_LP_EPICS.md)
