---
doc_id: "ISSUE-F3-01-001-GERACAO-E-VALIDACAO-TOKEN.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F3-01-001 - Geração e validação de token de reconhecimento

## User Story

Como sistema, quero gerar e validar tokens de reconhecimento para leads que converteram, permitindo que sejam reconhecidos em ativações subsequentes do mesmo evento.

## Contexto Tecnico

Token opaco (hash ou UUID) vinculado a lead_id + evento_id. TTL 7 dias. Persistir em lead_reconhecimento_token. POST /leads retorna token_reconhecimento. GET /leads/reconhecer?token= valida. Conforme PRD seções 5.1 e 6.3.

## Plano TDD

- Red: testes para geração, persistência e validação
- Green: implementar serviço e endpoints
- Refactor: extrair constantes

## Criterios de Aceitacao

- Given lead converteu, When POST /leads retorna, Then token_reconhecimento presente
- Given token válido, When GET /leads/reconhecer?token=, Then lead_reconhecido = true
- Given token expirado, When GET reconhecer, Then lead_reconhecido = false
- Given token de outro evento, When GET reconhecer para evento X, Then não reconhecido para X

## Definition of Done da Issue

- [ ] Serviço gera token e persiste em lead_reconhecimento_token
- [ ] POST /leads retorna token_reconhecimento no response
- [ ] GET /leads/reconhecer?token= valida e retorna status
- [ ] TTL 7 dias
- [ ] Testes backend

## Tarefas Decupadas

- [ ] T1: Implementar serviço de geração e persistência de token
- [ ] T2: Estender POST /leads para retornar token
- [ ] T3: Implementar GET /leads/reconhecer e integrar no GET landing
- [ ] T4: Adicionar testes

## Instructions por Task

### T1
- objetivo: criar serviço que gera token opaco e persiste em lead_reconhecimento_token
- precondicoes: modelo LeadReconhecimentoToken existente
- arquivos_a_ler_ou_tocar:
  - `backend/app/services/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Gerar token opaco (secrets.token_urlsafe ou uuid)
  2. Calcular hash para armazenamento (ou armazenar token diretamente conforme decisão de segurança)
  3. Inserir em lead_reconhecimento_token com lead_id, evento_id, token_hash, expires_at = now + 7 dias
  4. Retornar token em texto para o cliente
- comandos_permitidos:
  - `cd backend && python -c "from app.services.reconhecimento import gerar_token; print(gerar_token(1,1))"`
- resultado_esperado: token gerado e persistido
- testes_ou_validacoes_obrigatorias:
  - teste unitário do serviço
- stop_conditions:
  - parar se modelo LeadReconhecimentoToken não existir

### T2
- objetivo: estender POST /leads para retornar token_reconhecimento
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/` ou routers de leads
  - `backend/app/schemas/`
- passos_atomicos:
  1. Após registrar conversão, chamar serviço de geração de token
  2. Adicionar token_reconhecimento ao response
  3. Só retornar quando ativacao_id presente e conversão registrada
- comandos_permitidos:
  - `cd backend && python -m uvicorn app.main:app --reload`
- resultado_esperado: response inclui token_reconhecimento
- testes_ou_validacoes_obrigatorias:
  - teste de integração
- stop_conditions:
  - parar se fluxo do POST /leads for bloqueado

### T3
- objetivo: implementar GET /leads/reconhecer e integrar no GET landing
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/`
  - `backend/app/services/`
- passos_atomicos:
  1. Criar GET /leads/reconhecer?token=&evento_id=
  2. Validar token, verificar expires_at, verificar evento_id
  3. Retornar lead_reconhecido (bool) e lead_id se reconhecido
  4. No GET landing: se cookie ou token na URL, chamar validação e incluir lead_reconhecido no payload
- comandos_permitidos:
  - `cd backend && python -m uvicorn app.main:app --reload`
- resultado_esperado: GET landing retorna lead_reconhecido correto
- testes_ou_validacoes_obrigatorias:
  - teste de integração
- stop_conditions:
  - parar se contrato do GET landing não permitir extensão

### T4
- objetivo: adicionar testes
- precondicoes: T1, T2, T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
- passos_atomicos:
  1. Teste: POST retorna token
  2. Teste: GET reconhecer com token válido
  3. Teste: GET reconhecer com token expirado
  4. Teste: GET landing com token retorna lead_reconhecido
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k reconhecimento`
- resultado_esperado: testes passam
- testes_ou_validacoes_obrigatorias:
  - pytest
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `backend/app/services/`
- `backend/app/api/`
- `backend/app/schemas/`
- `backend/tests/`

## Artifact Minimo

- Serviço de token
- Endpoints estendidos
- Testes

## Dependencias

- [EPIC-F1-01](../../F1-FUNDACAO-MODELO-BACKEND/EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [EPIC-F2-02](../../F2-FLUXO-CPF-FIRST-E-CONVERSAO/EPIC-F2-02-REGISTRO-CONVERSAO-E-BLOQUEIO.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
