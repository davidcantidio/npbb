---
doc_id: "ISSUE-F1-03-001-SERVICO-GERACAO-QR.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.2 - Estrutura de URL do QR"
  - "PRD 7.1 - Backend"
  - "PRD 13.1 - Modelo e Ativações"
---

# ISSUE-F1-03-001 - Serviço de geração de QR

## User Story

Como sistema, quero gerar um QR-code único por ativação que aponta para a URL da landing, para que o visitante possa escanear e acessar o formulário.

## Contexto Tecnico

URL do QR: `/eventos/:evento_id/ativacoes/:ativacao_id` ou `/e/:evento_id/a/:ativacao_id` para URLs mais curtas. Lib `qrcode` em Python ou similar. O QR pode ser gerado como imagem (PNG/SVG) ou URL armazenada. Conforme PRD seção 5.2 e 7.1.

## Plano TDD

- Red: teste que valida geração de QR para URL válida
- Green: implementar serviço
- Refactor: extrair configuração de base URL

## Criterios de Aceitacao

- Given evento_id e ativacao_id, When gero QR, Then imagem ou URL retornada
- Given ativação criada, When QR gerado, Then qr_code_url populado na ativação
- Given URL base configurável, When gero QR, Then URL completa correta

## Definition of Done da Issue

- [ ] Serviço gera QR para URL da landing
- [ ] qr_code_url populado ao criar/atualizar ativação
- [ ] Teste unitário do serviço passa

## Tarefas Decupadas

- [ ] T1: Implementar serviço de geração de QR (lib qrcode ou segno)
- [ ] T2: Integrar geração no fluxo de criação/atualização de ativação
- [ ] T3: Adicionar teste unitário

## Instructions por Task

### T1
- objetivo: criar serviço de geração de QR a partir da URL canônica da ativação
- precondicoes: rota `/eventos/:evento_id/ativacoes/:ativacao_id` definida no PRD
- arquivos_a_ler_ou_tocar:
  - `backend/app/services/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Escolher a biblioteca já compatível com o backend (`qrcode` ou `segno`)
  2. Implementar função que recebe `evento_id`, `ativacao_id` e `base_url`
  3. Gerar URL completa da landing e produzir artefato do QR (imagem, SVG ou URL persistível)
  4. Retornar payload suficiente para persistir em `qr_code_url`
- comandos_permitidos:
  - `cd backend && python -m pytest -q -k qr`
- resultado_esperado: serviço isolado gera QR consistente para a URL da landing
- testes_ou_validacoes_obrigatorias:
  - teste unitário do serviço
- stop_conditions:
  - parar se a estratégia de persistência do QR não puder ser derivada do código atual

### T2
- objetivo: integrar a geração de QR ao fluxo de criação e atualização de ativações
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `backend/app/api/`
  - `backend/app/services/`
  - `backend/app/models/models.py`
- passos_atomicos:
  1. Localizar o ponto de criação/edição de ativação
  2. Chamar o serviço de QR após a ativação possuir `evento_id` e `ativacao_id`
  3. Persistir `qr_code_url` no modelo antes de retornar a resposta
  4. Garantir idempotência em updates sem duplicar artefatos desnecessariamente
- comandos_permitidos:
  - `cd backend && python -m pytest -q -k ativacao`
- resultado_esperado: ativações novas ou alteradas mantêm `qr_code_url` coerente
- testes_ou_validacoes_obrigatorias:
  - teste de integração ou cobertura indireta no CRUD
- stop_conditions:
  - parar se o CRUD de ativações ainda não expuser ponto seguro de integração

### T3
- objetivo: cobrir a geração de QR com testes automatizados
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `backend/tests/`
- passos_atomicos:
  1. Testar geração de QR para URL válida
  2. Testar preenchimento de `qr_code_url` no fluxo de criação/atualização
  3. Validar comportamento quando `base_url` for configurável
- comandos_permitidos:
  - `cd backend && PYTHONPATH=/workspace:/workspace/backend TESTING=true python -m pytest -q -k qr`
- resultado_esperado: suíte cobre serviço e integração principal
- testes_ou_validacoes_obrigatorias:
  - pytest
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `backend/app/services/`
- `backend/app/models/models.py`
- `backend/tests/`

## Artifact Minimo

- `backend/app/services/qr_service.py` ou similar
- Teste em `backend/tests/`

## Dependencias

- [EPIC-F1-01](../EPIC-F1-01-MODELO-E-MIGRACOES.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
