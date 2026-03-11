---
doc_id: "ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F3-02-001 - Lead reconhecido pula CPF e ativação múltipla

## User Story

Como lead que já converteu em uma ativação, quero acessar outra ativação do mesmo evento e ir direto ao formulário sem repetir CPF, para ter experiência fluida.

## Contexto Tecnico

Quando GET landing retorna lead_reconhecido = true, frontend pula etapa CPF e exibe formulário completo. Em ativação múltipla, submit registra nova conversão. Conforme PRD seções 5.4 e 5.5.

## Plano TDD

- Red: testes E2E para lead reconhecido
- Green: implementar lógica de pular CPF
- Refactor: consolidar estados

## Criterios de Aceitacao

- Given lead_reconhecido = true, When carrego landing, Then exibo formulário completo (não CPF)
- Given ativação múltipla e lead reconhecido, When preencho e submeto, Then nova conversão registrada
- Given ativação única e lead já converteu, When carrego, Then mensagem "já cadastrou" (issue F3-02-002)

## Definition of Done da Issue

- [ ] lead_reconhecido = true → pular etapa CPF
- [ ] Ativação múltipla: formulário direto, submit registra conversão
- [ ] Testes E2E

## Tarefas Decupadas

- [ ] T1: Verificar lead_reconhecido no payload e ajustar estado inicial
- [ ] T2: Em ativação múltipla, permitir submit e registrar conversão
- [ ] T3: Testes Playwright

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Lógica de fluxo no frontend
- Testes E2E

## Dependencias

- [EPIC-F3-01](../EPIC-F3-01-MECANISMO-RECONHECIMENTO.md)
- [ISSUE-F3-01-002](./ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
