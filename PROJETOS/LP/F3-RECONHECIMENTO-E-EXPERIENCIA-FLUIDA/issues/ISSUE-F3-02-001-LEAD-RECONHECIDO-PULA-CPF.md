---
doc_id: "ISSUE-F3-02-001-LEAD-RECONHECIDO-PULA-CPF.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "required"
decision_refs:
  - "PRD 5.4 - Ativação Múltipla — Lead Reconhecido"
  - "PRD 5.5 - Definição de Primeiro Acesso vs Reconhecido"
  - "PRD 13.3 - Reconhecimento"
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

## Instructions por Task

### T1
- objetivo: usar `lead_reconhecido` para definir o estado inicial da landing
- precondicoes: GET landing já retorna `lead_reconhecido`
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
- passos_atomicos:
  1. Localizar o estado inicial do fluxo CPF-first
  2. Quando `lead_reconhecido = true`, iniciar no formulário completo
  3. Preservar o fluxo CPF-first para visitantes não reconhecidos
  4. Garantir que a decisão dependa apenas do payload do backend
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: visitante reconhecido não vê a etapa de CPF
- testes_ou_validacoes_obrigatorias:
  - teste de componente/integrado
- stop_conditions:
  - parar se a landing ainda não consumir o payload de reconhecimento

### T2
- objetivo: manter o fluxo de conversão funcional para ativações múltiplas com lead reconhecido
- precondicoes: T1 concluída
- arquivos_a_ler_ou_tocar:
  - `frontend/src/`
  - integração com submit
- passos_atomicos:
  1. Verificar `conversao_unica`/`conversao_multipla` no contexto da ativação
  2. Em ativação múltipla, permitir submit direto do formulário completo
  3. Garantir que o submit continue registrando a conversão da ativação atual
- comandos_permitidos:
  - `cd frontend && npm run test`
- resultado_esperado: lead reconhecido pode converter normalmente em ativações múltiplas
- testes_ou_validacoes_obrigatorias:
  - teste de integração do submit
- stop_conditions:
  - parar se o payload da ativação não expuser a regra de conversão

### T3
- objetivo: proteger o fluxo com testes E2E
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/`
- passos_atomicos:
  1. Testar lead reconhecido pulando CPF
  2. Testar submit direto em ativação múltipla
  3. Verificar que o caso de ativação única segue para a issue F3-02-002
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: comportamento de reconhecimento fica coberto por regressão
- testes_ou_validacoes_obrigatorias:
  - Playwright ou equivalente
- stop_conditions:
  - nenhuma

## Arquivos Reais Envolvidos

- `frontend/src/`
- `frontend/e2e/`

## Artifact Minimo

- Lógica de fluxo no frontend
- Testes E2E

## Dependencias

- [EPIC-F3-01](../EPIC-F3-01-MECANISMO-RECONHECIMENTO.md)
- [ISSUE-F3-01-002](./ISSUE-F3-01-002-COOKIE-E-INTEGRACAO-LANDING.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
