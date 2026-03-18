---
doc_id: "ISSUE-F3-02-002-OPCAO-REGISTRAR-OUTRO-CPF.md"
version: "1.1"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.3 - Opção Registrar outro CPF"
  - "PRD 4 - Fluxo Principal"
  - "PRD 13.4 - Conversão por Ativação"
---

# ISSUE-F3-02-002 - Opção "Registrar outro CPF" em ativação única

## User Story

Como lead que já converteu em ativação de conversão única, quero ver a opção "Registrar outro CPF" para cadastrar outra pessoa usando meu celular.

## Contexto Tecnico

Esta issue passa a depender explicitamente de `ISSUE-F3-02-002.1`, que expõe no GET landing o campo `lead_ja_converteu_nesta_ativacao`. Quando ativação tem `conversao_unica = true`, `lead_reconhecido = true` e `lead_ja_converteu_nesta_ativacao = true`, o frontend deve exibir mensagem "Você já se cadastrou nesta ativação" e link "Registrar outro CPF" (ou "Cadastrar outra pessoa"). Ao clicar, limpar apenas esse estado local da sessão e exibir campo CPF novamente. Conforme PRD seção 5.3.

## Plano TDD

- Red: testes E2E para fluxo
- Green: implementar UI e lógica
- Refactor: extrair copy

## Criterios de Aceitacao

- Given ativação única e lead já converteu, When carrego landing, Then mensagem + link "Registrar outro CPF"
- Given clico em "Registrar outro CPF", When exibo, Then campo CPF visível novamente
- Given novo CPF válido, When submeto, Then nova conversão registrada na mesma ativação

## Definition of Done da Issue

- [x] Mensagem "Você já se cadastrou" quando aplicável
- [x] Link "Registrar outro CPF" ou "Cadastrar outra pessoa"
- [x] Ao clicar: exibir CPF e permitir novo cadastro
- [x] Testes E2E

## Tarefas Decupadas

- [x] T1: Detectar estado "já converteu nesta ativação"
- [x] T2: Exibir mensagem e link
- [x] T3: Implementar fluxo ao clicar (limpar estado, exibir CPF)
- [x] T4: Testes Playwright

## Instructions por Task

### T1
- objetivo: detectar o estado de lead reconhecido que já converteu na ativação atual
- precondicoes: reconhecimento já funcional e `ISSUE-F3-02-002.1` concluída, com o GET landing expondo `lead_ja_converteu_nesta_ativacao`
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - contrato do payload da landing
- passos_atomicos:
  1. Consumir `lead_ja_converteu_nesta_ativacao` no fluxo da landing
  2. Distinguir esse caso do lead apenas reconhecido em outra ativação
  3. Persistir estado suficiente para renderizar a mensagem correta
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: tela identifica corretamente quando mostrar a opção de novo CPF
- testes_ou_validacoes_obrigatorias:
  - teste de componente/integrado
- stop_conditions:
  - parar se `ISSUE-F3-02-002.1` não estiver concluída ou o contrato consumido não expuser `lead_ja_converteu_nesta_ativacao`

### T2
- objetivo: renderizar a mensagem de bloqueio suave e o link de novo CPF
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Exibir mensagem "Você já se cadastrou nesta ativação" ou copy equivalente
  2. Exibir link/botão "Registrar outro CPF" ou "Cadastrar outra pessoa"
  3. Posicionar o CTA no fluxo sem conflitar com a confirmação padrão
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: usuário entende por que não pode repetir a mesma conversão e como seguir
- testes_ou_validacoes_obrigatorias:
  - teste de renderização
- stop_conditions:
  - nenhuma

### T3
- objetivo: reabrir a etapa de CPF para um novo cadastro ao acionar o link
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Limpar o estado de "já converteu nesta ativação" apenas para a sessão corrente
  2. Reexibir o campo CPF
  3. Permitir que o novo CPF válido avance até o submit normal
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: fluxo de terceiro CPF funciona sem quebrar o reconhecimento base
- testes_ou_validacoes_obrigatorias:
  - teste de interação
- stop_conditions:
  - parar se a máquina de estados da landing não permitir retorno controlado à etapa CPF

### T4
- objetivo: cobrir o fluxo "Registrar outro CPF" com E2E
- precondicoes: T1, T2 e T3 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/`
- passos_atomicos:
  1. Testar renderização da mensagem e do link
  2. Testar clique no link e retorno do campo CPF
  3. Testar envio de novo CPF válido na mesma ativação
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: o fluxo de exceção fica protegido contra regressão
- testes_ou_validacoes_obrigatorias:
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Componente com mensagem e link
- Lógica de estado
- Testes

## Dependencias

- [ISSUE-F3-02-002.1](./ISSUE-F3-02-002.1-CONTRATO-GET-LANDING-JA-CONVERTEU.md)
- [ISSUE-F3-02-001](./ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md)
- [EPIC-F3-02](../EPIC-F3-02-EXPERIENCIA-FLUIDA.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
