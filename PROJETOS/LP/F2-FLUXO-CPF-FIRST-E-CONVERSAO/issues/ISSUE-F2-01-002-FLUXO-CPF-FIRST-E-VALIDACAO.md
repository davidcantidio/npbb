---
doc_id: "ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs: []
---

# ISSUE-F2-01-002 - Fluxo CPF-first e validação de dígito

## User Story

Como visitante no primeiro acesso, quero ver apenas o campo CPF, validá-lo e só então preencher o restante do formulário, para ter uma experiência guiada e garantir CPF válido.

## Contexto Tecnico

Estado inicial da landing: apenas campo CPF. Validação de dígito verificador (algoritmo padrão). Após CPF válido, exibir formulário completo. Conforme PRD seções 4 e 8.3.

## Plano TDD

- Red: testes para validação de CPF e transição de estado
- Green: implementar fluxo em etapas
- Refactor: extrair lógica de validação

## Criterios de Aceitacao

- Given primeiro acesso, When carrego landing, Then exibo apenas campo CPF
- Given CPF com dígito verificador inválido, When submeto, Then mensagem de erro clara
- Given CPF válido, When submeto validação, Then exibo formulário completo
- Given formulário completo exibido, When preencho e submeto, Then POST /leads com ativacao_id

## Definition of Done da Issue

- [ ] Estado inicial: apenas CPF
- [ ] Validação de dígito verificador (frontend e/ou backend)
- [ ] CPF inválido: mensagem de erro
- [ ] CPF válido: transição para formulário completo
- [ ] Submit final envia ativacao_id no POST /leads

## Tarefas Decupadas

- [ ] T1: Implementar validação de dígito verificador (util ou lib)
- [ ] T2: Implementar estado da landing (só CPF vs formulário completo)
- [ ] T3: Integrar submit com ativacao_id

## Instructions por Task

### T1
- objetivo: implementar ou integrar validação de CPF (dígito verificador)
- precondicoes: nenhuma
- arquivos_a_ler_ou_tocar:
  - `frontend/src/` ou `backend/app/` (onde a validação viver)
- passos_atomicos:
  1. Implementar função que valida dígitos verificadores do CPF (algoritmo padrão)
  2. CPF deve ter 11 dígitos; remover formatação antes de validar
  3. Retornar boolean ou mensagem de erro
- comandos_permitidos:
  - `npm run test` ou `pytest`
- resultado_esperado: testes de validação passam (CPFs válidos/inválidos conhecidos)
- testes_ou_validacoes_obrigatorias:
  - teste com CPF válido (ex: 529.982.247-25) e inválido
- stop_conditions:
  - parar se lib externa de validação for obrigatória e não existir

### T2
- objetivo: implementar estado da landing com duas etapas (CPF first, formulário completo)
- precondicoes: T1 concluída; página de landing existe
- arquivos_a_ler_ou_tocar:
  - `frontend/src/` (componentes da landing)
- passos_atomicos:
  1. Estado: etapa "cpf" ou "formulario"
  2. Inicial: etapa "cpf", exibir apenas campo CPF e botão validar
  3. Ao validar CPF com sucesso: mudar para etapa "formulario"
  4. Exibir formulário completo (campos do lead configurado)
- comandos_permitidos:
  - `npm run dev`
- resultado_esperado: fluxo visual correto
- testes_ou_validacoes_obrigatorias:
  - teste manual ou Playwright
- stop_conditions:
  - parar se estrutura do formulário de leads for diferente do esperado

### T3
- objetivo: integrar submit do formulário com POST /leads e ativacao_id
- precondicoes: T2 concluída; endpoint POST /leads estendido (F2-02)
- arquivos_a_ler_ou_tocar:
  - `frontend/src/` (submit handler)
- passos_atomicos:
  1. No submit, incluir ativacao_id do contexto da página
  2. Incluir cpf e demais campos
  3. Tratar resposta: sucesso, bloqueado_cpf_duplicado
- comandos_permitidos:
  - `npm run dev`
- resultado_esperado: lead criado com conversão registrada
- testes_ou_validacoes_obrigatorias:
  - teste E2E ou integração
- stop_conditions:
  - parar se contrato do POST /leads não estiver definido

## Arquivos Reais Envolvidos

- `frontend/src/`
- `backend/app/` (se validação no backend)

## Artifact Minimo

- Componente/página com fluxo CPF-first
- Função de validação de CPF

## Dependencias

- [ISSUE-F2-01-001](./ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md)
- [EPIC-F2-02](../EPIC-F2-02-REGISTRO-CONVERSAO-E-BLOQUEIO.md) (para contrato POST)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
