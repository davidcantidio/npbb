---
doc_id: "ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.1 - Mecanismo de Reconhecimento"
  - "PRD 5.5 - Definição de Primeiro Acesso vs Reconhecido"
  - "PRD 8.1 - GET /eventos/:evento_id/ativacoes/:ativacao_id/landing"
---

# ISSUE-F3-01-002 - Cookie e integração com GET landing

## User Story

Como visitante, quero permanecer reconhecido entre ativações por meio do cookie emitido pelo backend para não precisar repetir o CPF.

## Contexto Tecnico

Cookie `lp_lead_token` com valor do token. O backend emite `Set-Cookie` ao responder o POST /leads; o navegador reenvia o cookie automaticamente nas próximas requisições. Quando houver `?token=` na URL, o frontend deve encaminhá-lo ao backend no carregamento da landing. GET landing usa cookie e/ou token para retornar `lead_reconhecido`. Conforme PRD seções 5.1, 5.5 e 8.1.

## Plano TDD

- Red: testes E2E para fluxo com cookie
- Green: implementar integração com `Set-Cookie`, envio de credenciais e repasse de `?token=`
- Refactor: extrair lógica de cookie

## Criterios de Aceitacao

- Given POST /leads conclui uma conversão, When resposta retorna, Then `Set-Cookie` para `lp_lead_token` é emitido
- Given cookie presente, When carrego landing, Then GET landing recebe cookie e retorna lead_reconhecido
- Given token na URL ?token=, When carrego landing, Then GET landing usa token e retorna lead_reconhecido
- Cookie com TTL 7 dias (ou equivalente)

## Definition of Done da Issue

- [ ] Fluxo de submit depende do cookie emitido pelo backend, sem persistência manual no frontend
- [ ] GET landing recebe cookie ou token na URL
- [ ] Backend valida e retorna lead_reconhecido no payload
- [ ] Testes E2E cobrindo fluxo

## Tarefas Decupadas

- [ ] T1: Integrar o submit ao cookie emitido pelo backend
- [ ] T2: Incluir cookie ou token na requisição do GET landing
- [ ] T3: Testes E2E

## Instructions por Task

### T1
- objetivo: alinhar o fluxo de submit ao cookie `lp_lead_token` emitido pelo backend
- precondicoes: `POST /leads` já retorna resposta com `Set-Cookie`
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - cliente HTTP ou camada de submit do formulário
- passos_atomicos:
  1. Verificar como o frontend faz o submit do lead
  2. Garantir que a requisição aceite e preserve cookies da resposta (`credentials`/config equivalente)
  3. Remover qualquer persistência manual de token no frontend, se existir
  4. Manter `token_reconhecimento` apenas como dado de resposta, sem usá-lo para setar cookie
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: reconhecimento depende do `Set-Cookie` emitido pelo backend
- testes_ou_validacoes_obrigatorias:
  - teste de integração do submit
- stop_conditions:
  - parar se o fluxo HTTP atual impedir o recebimento de cookies do backend

### T2
- objetivo: garantir que o carregamento da landing use cookie automático e `?token=` quando presente
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - cliente HTTP do GET landing
- passos_atomicos:
  1. Garantir envio de credenciais no GET landing quando necessário
  2. Ler o query param `token` da URL
  3. Encaminhar `?token=` ao backend sem sobrescrever o fluxo de cookie
  4. Consumir `lead_reconhecido` do payload para as issues seguintes
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: a landing reconhece o lead tanto por cookie quanto por token na URL
- testes_ou_validacoes_obrigatorias:
  - teste de integração do carregamento
- stop_conditions:
  - parar se o cliente HTTP do frontend não suportar configuração de credenciais

### T3
- objetivo: cobrir o reconhecimento por cookie e por token com testes E2E
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/` ou suíte equivalente
- passos_atomicos:
  1. Testar conversão inicial que gera o cookie
  2. Testar acesso subsequente à landing com cookie válido
  3. Testar acesso com `?token=` na URL
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: reconhecimento automatizado coberto em cenários reais de navegação
- testes_ou_validacoes_obrigatorias:
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

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
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
