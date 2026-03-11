---
doc_id: "ISSUE-F1-03-002-ENDPOINT-GET-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F1-03-002 - Endpoint GET landing

## User Story

Como visitante, quero que a landing carregue com contexto de evento e ativação via API, para preencher o formulário de lead no contexto correto.

## Contexto Tecnico

Endpoint público: `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing`. Retorna payload com: evento, ativação, formulário configurado, template. Inclui flag `lead_reconhecido` quando cookie/token válido presente (na F1, sempre false). Conforme PRD seção 8.1.

## Plano TDD

- Red: testes para GET landing retornando payload esperado
- Green: implementar endpoint
- Refactor: extrair lógica de montagem do payload

## Criterios de Aceitacao

- Given evento e ativação existentes, When GET landing, Then payload com evento, ativação, formulário retornado
- Given requisição sem cookie/token, When GET landing, Then lead_reconhecido = false
- Given evento ou ativação inexistentes, When GET landing, Then 404
- Given query param ?token= presente, When GET landing, Then payload inclui (validação de token na F3)

## Definition of Done da Issue

- [ ] Endpoint GET landing implementado
- [ ] Payload inclui evento, ativação, formulário configurado, template
- [ ] Flag lead_reconhecido = false (validação real na F3)
- [ ] Endpoint público (sem autenticação obrigatória)
- [ ] Testes backend cobrindo cenários

## Tarefas Decupadas

- [ ] T1: Criar schema de resposta LandingPayload
- [ ] T2: Implementar endpoint e serviço de montagem do payload
- [ ] T3: Adicionar testes

## Instructions por Task

### T1
- objetivo: criar schema LandingPayload com estrutura esperada pelo frontend
- precondicoes: modelos Evento, Ativacao existentes
- arquivos_a_ler_ou_tocar:
  - `backend/app/schemas/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Definir LandingPayload com: evento (resumo), ativacao (resumo), formulario, template, lead_reconhecido (bool)
  2. Usar schemas aninhados ou referências para evento e ativação
- comandos_permitidos:
  - `cd backend && python -c "from app.schemas.landing import LandingPayload; print(LandingPayload)"`
- resultado_esperado: schema importável
- testes_ou_validacoes_obrigatorias:
  - validação com dados de exemplo
- stop_conditions:
  - parar se estrutura de formulário for diferente do existente

### T2
- objetivo: implementar endpoint GET e lógica de montagem
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/` ou `backend/app/routers/`
  - `backend/app/services/` (se necessário)
- passos_atomicos:
  1. Criar rota GET /eventos/{evento_id}/ativacoes/{ativacao_id}/landing
  2. Buscar evento e ativação; retornar 404 se não existir
  3. Montar payload com evento, ativação, formulário do evento, template
  4. Incluir lead_reconhecido = False (sem validação de cookie/token nesta fase)
- comandos_permitidos:
  - `cd backend && python -m uvicorn app.main:app --reload`
- resultado_esperado: endpoint retorna 200 com payload válido
- testes_ou_validacoes_obrigatorias:
  - chamada HTTP GET
- stop_conditions:
  - parar se estrutura de formulário não existir no modelo

### T3
- objetivo: adicionar testes para o endpoint
- precondicoes: T2 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
- passos_atomicos:
  1. Teste: GET com evento e ativação válidos retorna 200 e payload
  2. Teste: GET com evento inexistente retorna 404
  3. Teste: GET com ativação inexistente retorna 404
  4. Teste: lead_reconhecido presente e false
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k landing`
- resultado_esperado: testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest
- stop_conditions:
  - parar se fixtures de evento/ativação não existirem

## Arquivos Reais Envolvidos

- `backend/app/schemas/`
- `backend/app/api/` ou `backend/app/routers/`
- `backend/tests/`

## Artifact Minimo

- `backend/app/schemas/landing.py` ou similar
- Endpoint em router
- Testes em `backend/tests/`

## Dependencias

- [EPIC-F1-01](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
