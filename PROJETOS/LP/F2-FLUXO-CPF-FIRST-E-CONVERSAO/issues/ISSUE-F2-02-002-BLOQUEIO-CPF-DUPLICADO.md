---
doc_id: "ISSUE-F2-02-002-BLOQUEIO-CPF-DUPLICADO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 4 - Fluxo Principal"
  - "PRD 8.2 - POST /leads/"
  - "PRD 13.4 - Conversão por Ativação"
---

# ISSUE-F2-02-002 - Bloqueio CPF duplicado e integração frontend

## User Story

Como sistema, quero bloquear o cadastro do mesmo CPF em ativação de conversão única quando já houver conversão, e exibir mensagem clara ao visitante.

## Contexto Tecnico

Em ativação com conversao_unica = true, verificar se (ativacao_id, cpf) já existe em conversao_ativacao. Se sim, retornar bloqueado_cpf_duplicado = true e não registrar nova conversão. Frontend exibe mensagem clara. Conforme PRD seções 4 e 8.2.

## Plano TDD

- Red: testes para bloqueio e response
- Green: implementar verificação e tratamento no frontend
- Refactor: extrair mensagens para i18n se aplicável

## Criterios de Aceitacao

- Given ativação com conversao_unica, When POST com CPF já convertido, Then bloqueado_cpf_duplicado = true
- Given bloqueado_cpf_duplicado = true, When frontend recebe, Then mensagem clara exibida
- Given ativação com conversao_multipla, When POST com mesmo CPF, Then nova conversão registrada (não bloqueia)

## Definition of Done da Issue

- [ ] Backend verifica (ativacao_id, cpf) em ativação única antes de registrar
- [ ] Response bloqueado_cpf_duplicado quando bloqueado
- [ ] Frontend exibe mensagem clara
- [ ] Testes backend e frontend

## Tarefas Decupadas

- [ ] T1: Implementar verificação de bloqueio no backend
- [ ] T2: Tratar resposta no frontend e exibir mensagem
- [ ] T3: Adicionar testes

## Instructions por Task

### T1
- objetivo: bloquear CPF duplicado em ativações de conversão única antes do registro da conversão
- precondicoes: extensão de `POST /leads` com `ativacao_id` já implementada
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/` ou `backend/app/services/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Carregar a ativação e verificar `conversao_unica`
  2. Consultar existência de `(ativacao_id, cpf)` em `conversao_ativacao`
  3. Se existir, impedir nova conversão e retornar `bloqueado_cpf_duplicado = true`
  4. Se for conversão múltipla, manter o comportamento normal
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k bloqueio`
- resultado_esperado: backend aplica a regra de unicidade somente quando configurado
- testes_ou_validacoes_obrigatorias:
  - teste de integração backend
- stop_conditions:
  - parar se `conversao_unica` não estiver disponível no modelo de ativação

### T2
- objetivo: refletir no frontend o bloqueio retornado pelo backend
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Mapear `bloqueado_cpf_duplicado` na resposta do submit
  2. Exibir mensagem clara sem perder o contexto da ativação
  3. Garantir que o visitante possa corrigir ou encerrar o fluxo
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: usuário entende que o CPF já converteu naquela ativação
- testes_ou_validacoes_obrigatorias:
  - teste de UI ou integração frontend
- stop_conditions:
  - parar se o contrato real do submit não expuser `bloqueado_cpf_duplicado`

### T3
- objetivo: cobrir backend e frontend com testes da regra de bloqueio
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
  - `frontend/e2e/` ou suíte frontend equivalente
- passos_atomicos:
  1. Testar bloqueio em ativação única com CPF já convertido
  2. Testar ausência de bloqueio em ativação múltipla
  3. Testar mensagem exibida no frontend quando houver bloqueio
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k bloqueio`
  - `cd frontend && npx playwright test`
- resultado_esperado: a regra fica protegida contra regressão nas duas camadas
- testes_ou_validacoes_obrigatorias:
  - pytest
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `backend/app/api/` ou `backend/app/services/`
- `frontend/src/`
- `backend/tests/`

## Artifact Minimo

- Lógica de bloqueio no backend
- Tratamento no frontend
- Testes

## Dependencias

- [ISSUE-F2-02-001](./ISSUE-F2-02-001-EXTENSAO-POST-LEADS.md)
- [EPIC-F2-01](../EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
