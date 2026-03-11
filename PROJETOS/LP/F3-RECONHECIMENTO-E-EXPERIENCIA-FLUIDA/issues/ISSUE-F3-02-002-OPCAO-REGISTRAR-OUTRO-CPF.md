---
doc_id: "ISSUE-F3-02-002-OPCAO-REGISTRAR-OUTRO-CPF.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-02-002 - Opção "Registrar outro CPF" em ativação única

## User Story

Como lead que já converteu em ativação de conversão única, quero ver a opção "Registrar outro CPF" para cadastrar outra pessoa usando meu celular.

## Contexto Tecnico

Quando ativação tem conversao_unica = true e lead já converteu nessa ativação: exibir mensagem "Você já se cadastrou nesta ativação" e link "Registrar outro CPF" (ou "Cadastrar outra pessoa"). Ao clicar, limpar estado e exibir campo CPF novamente. Conforme PRD seção 5.3.

## Plano TDD

- Red: testes E2E para fluxo
- Green: implementar UI e lógica
- Refactor: extrair copy

## Criterios de Aceitacao

- Given ativação única e lead já converteu, When carrego landing, Then mensagem + link "Registrar outro CPF"
- Given clico em "Registrar outro CPF", When exibo, Then campo CPF visível novamente
- Given novo CPF válido, When submeto, Then nova conversão registrada na mesma ativação

## Definition of Done da Issue

- [ ] Mensagem "Você já se cadastrou" quando aplicável
- [ ] Link "Registrar outro CPF" ou "Cadastrar outra pessoa"
- [ ] Ao clicar: exibir CPF e permitir novo cadastro
- [ ] Testes E2E

## Tarefas Decupadas

- [ ] T1: Detectar estado "já converteu nesta ativação"
- [ ] T2: Exibir mensagem e link
- [ ] T3: Implementar fluxo ao clicar (limpar estado, exibir CPF)
- [ ] T4: Testes Playwright

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Componente com mensagem e link
- Lógica de estado
- Testes

## Dependencias

- [ISSUE-F3-02-001](./ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md)
- [EPIC-F3-02](../EPIC-F3-02-EXPERIENCIA-FLUIDA.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
