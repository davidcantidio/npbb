---
doc_id: "ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
task_instruction_mode: "optional"
decision_refs: []
---

# ISSUE-F2-01-003 - Testes Playwright do fluxo CPF-first

## User Story

Como desenvolvedor, quero testes E2E com Playwright cobrindo o fluxo CPF-first para garantir regressão e documentar o comportamento esperado.

## Contexto Tecnico

Playwright para testes E2E. Cobrir: acesso à landing, exibição inicial só CPF, validação de CPF inválido, CPF válido e transição para formulário. Conforme observação do planejamento (prever testes com playwright).

## Plano TDD

- Red: cenários de teste definidos
- Green: implementar testes Playwright
- Refactor: extrair fixtures e helpers

## Criterios de Aceitacao

- Given landing carregada, When visito URL, Then vejo apenas campo CPF
- Given CPF inválido, When preencho e submeto, Then mensagem de erro exibida
- Given CPF válido, When preencho e submeto, Then formulário completo exibido
- Given formulário preenchido, When submeto, Then sucesso ou tratamento de bloqueio

## Definition of Done da Issue

- [ ] Testes Playwright para fluxo CPF-first
- [ ] Cenários: primeiro acesso, CPF inválido, CPF válido, submit
- [ ] Testes executam em CI ou localmente
- [ ] Documentação de como rodar os testes

## Tarefas Decupadas

- [ ] T1: Configurar Playwright no projeto (se não existir)
- [ ] T2: Implementar testes do fluxo CPF-first
- [ ] T3: Integrar com script de teste ou CI

## Arquivos Reais Envolvidos

- `frontend/e2e/` ou `tests/e2e/`
- `package.json` ou `playwright.config.ts`

## Artifact Minimo

- Testes em `frontend/e2e/` ou similar
- Configuração Playwright

## Dependencias

- [ISSUE-F2-01-001](./ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md)
- [ISSUE-F2-01-002](./ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [PRD](../../../PRD-LP-QR-ATIVACOES.md)
