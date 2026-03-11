---
doc_id: "EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F2-01 - Fluxo CPF-first e Validação

## Objetivo

Implementar na landing o fluxo CPF-first: estado inicial exibe apenas o campo CPF; após validação do dígito verificador, exibe o formulário completo. Conforme PRD seções 4 e 7.2.

## Resultado de Negocio Mensuravel

O visitante no primeiro acesso vê apenas CPF, valida e só então acessa o restante do formulário, reduzindo fricção e garantindo CPF válido antes do cadastro.

## Contexto Arquitetural

- Rota frontend: `/eventos/:evento_id/ativacoes/:ativacao_id`
- Validação de CPF: apenas dígito verificador (algoritmo padrão), sem consulta Receita Federal
- Formulário de leads existente em `frontend/`; adaptar para fluxo em etapas

## Definition of Done do Epico

- [ ] Primeiro acesso exibe apenas campo CPF
- [ ] Validação de dígito verificador no frontend (e/ou backend)
- [ ] CPF válido → exibe formulário completo
- [ ] CPF inválido → mensagem de erro clara
- [ ] Testes Playwright cobrindo fluxo CPF-first

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F2-01-001 | Rota e página landing com contexto de ativação | Nova rota e página que carrega contexto de evento/ativação | 3 | todo | [ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md](./issues/ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md) |
| ISSUE-F2-01-002 | Fluxo CPF-first e validação de dígito | Estado inicial só CPF; validação; exibir formulário completo | 3 | todo | [ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md](./issues/ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md) |
| ISSUE-F2-01-003 | Testes Playwright do fluxo CPF-first | Testes E2E cobrindo primeiro acesso e validação | 2 | todo | [ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md](./issues/ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md) |

## Artifact Minimo do Epico

- `frontend/src/` (rotas, páginas, componentes)
- `frontend/e2e/` ou `tests/e2e/` (Playwright)

## Dependencias

- [F1](../F1-FUNDACAO-MODELO-BACKEND/F1_LP_EPICS.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F2_LP_EPICS.md)
