---
doc_id: "ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-01-002 - Cookie e integração com GET landing

## User Story

Como visitante, quero que meu token de reconhecimento seja armazenado em cookie para que, ao acessar outra ativação, eu não precise repetir o CPF.

## Contexto Tecnico

Cookie `lp_lead_token` com valor do token. Frontend armazena ao receber token_reconhecimento do POST /leads. Ao carregar landing, envia cookie (ou token na URL) para o backend. GET landing usa isso para retornar lead_reconhecido. Conforme PRD seção 5.1.

## Plano TDD

- Red: testes E2E para fluxo com cookie
- Green: implementar armazenamento e envio
- Refactor: extrair lógica de cookie

## Criterios de Aceitacao

- Given POST /leads retorna token_reconhecimento, When frontend recebe, Then armazena em cookie lp_lead_token
- Given cookie presente, When carrego landing, Then GET landing recebe cookie e retorna lead_reconhecido
- Given token na URL ?token=, When carrego landing, Then GET landing usa token e retorna lead_reconhecido
- Cookie com TTL 7 dias (ou equivalente)

## Definition of Done da Issue

- [ ] Frontend armazena token em cookie ao receber do POST /leads
- [ ] GET landing recebe cookie ou token na URL
- [ ] Backend valida e retorna lead_reconhecido no payload
- [ ] Testes E2E cobrindo fluxo

## Tarefas Decupadas

- [ ] T1: Armazenar token em cookie no frontend após submit
- [ ] T2: Incluir cookie ou token na requisição do GET landing
- [ ] T3: Testes E2E

## Arquivos Reais Envolvidos

- `frontend/src/`
- `backend/app/api/`

## Artifact Minimo

- Lógica de cookie no frontend
- Integração com GET landing
- Testes E2E

## Dependencias

- [ISSUE-F3-01-001](./ISSUE-F3-01-001-GERACAO-E-VALIDACAO-TOKEN.md)
- [EPIC-F3-02](../EPIC-F3-02-EXPERIENCIA-FLUIDA.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
