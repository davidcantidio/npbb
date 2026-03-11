---
doc_id: "ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.2 - Estrutura de URL do QR"
  - "PRD 7.2 - Frontend"
  - "PRD 8.1 - GET /eventos/:evento_id/ativacoes/:ativacao_id/landing"
---

# ISSUE-F2-01-001 - Rota e página landing com contexto de ativação

## User Story

Como visitante, quero acessar a landing via URL `/eventos/:evento_id/ativacoes/:ativacao_id` para preencher o formulário de lead no contexto correto da ativação.

## Contexto Tecnico

Nova rota no frontend que chama GET /eventos/:evento_id/ativacoes/:ativacao_id/landing e renderiza a página com contexto de evento e ativação. Conforme PRD seção 5.2 e 7.2.

## Plano TDD

- Red: teste que valida rota e carregamento de payload
- Green: implementar rota e página
- Refactor: extrair hooks ou componentes reutilizáveis

## Criterios de Aceitacao

- Given URL /eventos/1/ativacoes/1, When carrego página, Then payload da landing é buscado
- Given payload retornado, When renderizo, Then contexto de evento e ativação disponível
- Given evento ou ativação inexistentes, When carrego, Then tratamento de erro (404)
- Given query param ?token=, When carrego, Then token passado para API (validação na F3)

## Definition of Done da Issue

- [ ] Rota `/eventos/:evento_id/ativacoes/:ativacao_id` criada
- [ ] Página carrega payload do endpoint de landing
- [ ] Contexto de evento e ativação disponível para formulário
- [ ] Tratamento de 404

## Tarefas Decupadas

- [ ] T1: Criar rota e componente de página
- [ ] T2: Integrar chamada ao endpoint de landing
- [ ] T3: Tratar erros (404, loading)

## Instructions por Task

### T1
- objetivo: criar a rota e a página base da landing por ativação no frontend
- precondicoes: endpoint de landing da F1 disponível
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - arquivos de roteamento da aplicação
- passos_atomicos:
  1. Localizar o mecanismo atual de rotas do frontend
  2. Registrar `/eventos/:evento_id/ativacoes/:ativacao_id`
  3. Criar componente/página responsável por carregar o contexto da ativação
  4. Garantir acesso aos params `evento_id`, `ativacao_id` e `token` quando presentes
- comandos_permitidos:
  - `cd frontend && npm run test -- --runInBand`
- resultado_esperado: URL da ativação renderiza uma página dedicada
- testes_ou_validacoes_obrigatorias:
  - teste de roteamento ou cobertura equivalente
- stop_conditions:
  - parar se o roteador ativo da aplicação não puder ser identificado

### T2
- objetivo: integrar a página ao endpoint de landing
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/api/` ou cliente HTTP equivalente
  - `frontend/src/`
- passos_atomicos:
  1. Implementar chamada para `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing`
  2. Encaminhar `?token=` quando presente na URL
  3. Popular estado da página com evento, ativação e formulário configurado
  4. Expor o payload para o fluxo CPF-first das issues seguintes
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: página recebe e disponibiliza o contexto correto da ativação
- testes_ou_validacoes_obrigatorias:
  - teste de integração do carregamento
- stop_conditions:
  - parar se o contrato real do endpoint divergir do PRD

### T3
- objetivo: tratar estados de carregamento e erro da landing
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Exibir estado de loading até o payload chegar
  2. Mapear 404 para mensagem/página coerente
  3. Tratar erros genéricos sem quebrar o fluxo do visitante
  4. Garantir que esses estados sejam cobertos por teste
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: a landing falha de forma controlada para 404 e erros transitórios
- testes_ou_validacoes_obrigatorias:
  - teste de erro/loading
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `frontend/src/` (rotas, páginas)
- `frontend/src/api/` ou similar

## Artifact Minimo

- Página de landing em `frontend/src/`
- Rota configurada

## Dependencias

- [EPIC-F2-01](../EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [F1](../../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
