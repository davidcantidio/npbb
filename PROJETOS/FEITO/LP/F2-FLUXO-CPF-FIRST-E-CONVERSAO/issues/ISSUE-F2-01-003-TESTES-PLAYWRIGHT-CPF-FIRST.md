---
doc_id: "ISSUE-F2-01-003-TESTES-PLAYWRIGHT-CPF-FIRST.md"
version: "1.0"
status: "done"
owner: "PM"
last_updated: "2026-03-12"
task_instruction_mode: "required"
decision_refs:
  - "PRD 4 - Fluxo Principal"
  - "PRD 13.2 - Fluxo CPF-first"
  - "PRD 13.5 - URL e QR"
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

- [x] Testes Playwright para fluxo CPF-first
- [x] Cenários: primeiro acesso, CPF inválido, CPF válido, submit
- [x] Testes executam em CI ou localmente
- [x] Documentação de como rodar os testes

## Tarefas Decupadas

- [x] T1: Configurar Playwright no projeto (se não existir)
- [x] T2: Implementar testes do fluxo CPF-first
- [x] T3: Integrar com script de teste ou CI

## Instructions por Task

### T1
- objetivo: confirmar ou instalar a base de Playwright necessária para a suíte da landing
- precondicoes: frontend executa localmente e a rota da landing existe
- arquivos_a_ler_ou_tocar:
  - `frontend/package.json`
  - `frontend/e2e/` ou `tests/e2e/`
  - `playwright.config.*`
- passos_atomicos:
  1. Verificar se Playwright já está configurado no projeto
  2. Se não estiver, adicionar configuração mínima compatível com o frontend atual
  3. Definir comando de execução local previsível
  4. Preparar fixtures básicas para evento/ativação
- comandos_permitidos:
  - `cd frontend && npx playwright test --list`
- resultado_esperado: infraestrutura de Playwright pronta para receber os cenários
- testes_ou_validacoes_obrigatorias:
  - listagem ou dry-run dos testes
- stop_conditions:
  - parar se existir framework E2E canônico conflitante no projeto

### T2
- objetivo: implementar os cenários E2E do fluxo CPF-first
- precondicoes: T1 concluída e landing funcional
- arquivos_a_ler_ou_tocar:
  - `frontend/e2e/` ou `tests/e2e/`
- passos_atomicos:
  1. Cobrir primeiro acesso exibindo apenas CPF
  2. Cobrir CPF inválido com mensagem de erro
  3. Cobrir CPF válido com transição para formulário completo
  4. Cobrir submit final e resposta de sucesso ou bloqueio
- comandos_permitidos:
  - `cd frontend && npx playwright test`
- resultado_esperado: cenários principais do fluxo documentados e automatizados
- testes_ou_validacoes_obrigatorias:
  - execução da suíte Playwright
- stop_conditions:
  - parar se não houver ambiente ou mocks suficientes para o fluxo E2E

### T3
- objetivo: integrar a suíte ao fluxo padrão de testes do projeto
- precondicoes: T1 e T2 concluídas
- arquivos_a_ler_ou_tocar:
  - `frontend/package.json`
  - documentação de setup/testes relevante
- passos_atomicos:
  1. Adicionar script de execução de Playwright
  2. Documentar como rodar localmente
  3. Integrar ao CI se já houver pipeline equivalente no frontend
- comandos_permitidos:
  - `cd frontend && npm run`
- resultado_esperado: suíte Playwright pode ser executada sem conhecimento implícito
- testes_ou_validacoes_obrigatorias:
  - validação do script/documentação
- stop_conditions:
  - parar se o pipeline CI estiver fora do escopo do diretório atual

## Arquivos Reais Envolvidos

- `frontend/e2e/` ou `tests/e2e/`
- `package.json` ou `playwright.config.ts`

## Artifact Minimo

- Testes em `frontend/e2e/` ou similar
- Configuração Playwright

## Dependencias

- [ISSUE-F2-01-001](./ISSUE-F2-01-001-ROTA-E-PAGINA-LANDING.md)
- [ISSUE-F2-01-002](./ISSUE-F2-01-002-FLUXO-CPF-FIRST-E-VALIDACAO.md)
- [PRD](../../PRD-LP-QR-ATIVACOES.md)
