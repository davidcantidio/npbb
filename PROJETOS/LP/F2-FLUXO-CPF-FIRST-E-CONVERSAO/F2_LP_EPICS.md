---
doc_id: "F2_LP_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-12"
audit_gate: "pending"
---

# Epicos - LP / F2 - Fluxo CPF-first e Conversão

## Objetivo da Fase

Implementar o fluxo CPF-first na landing (primeiro acesso exibe apenas CPF), validação de dígito verificador, registro de conversão por ativação e bloqueio de CPF duplicado em ativação de conversão única.

## Gate de Saida da Fase

O visitante acessa a landing via QR, vê apenas o campo CPF no primeiro acesso, valida dígito verificador, preenche o formulário completo e submete; a conversão é registrada na ativação. Em ativação de conversão única, CPF duplicado é bloqueado.

## Estado do Gate de Auditoria

- gate_atual: `pending`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semântica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [x] todos os epicos estao `done`
- [x] todas as issues filhas estao `done`
- [x] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F2-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F2-01 | Fluxo CPF-first e Validação | Landing exibe apenas CPF no primeiro acesso; validação de dígito verificador | F1 | done | [EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md](./EPIC-F2-01-FLUXO-CPF-FIRST-E-VALIDACAO.md) |
| EPIC-F2-02 | Registro de Conversão e Bloqueio | POST /leads com ativacao_id; registro de conversão; bloqueio CPF duplicado | F1, EPIC-F2-01 | done | [EPIC-F2-02-REGISTRO-CONVERSAO-E-BLOQUEIO.md](./EPIC-F2-02-REGISTRO-CONVERSAO-E-BLOQUEIO.md) |

## Dependencias entre Epicos

- `EPIC-F2-01`: depende de F1
- `EPIC-F2-02`: depende de F1 e EPIC-F2-01

## Escopo desta Fase

### Dentro
- Fluxo CPF-first na landing (primeiro acesso)
- Validação de dígito verificador (algoritmo padrão)
- Extensão de POST /leads com ativacao_id
- Registro de conversão em conversao_ativacao
- Bloqueio de CPF duplicado em ativação de conversão única
- Testes Playwright conforme observação do planejamento

### Fora
- Mecanismo de reconhecimento (cookie/token)
- Opção "Registrar outro CPF"
- Interface de operador

## Definition of Done da Fase

- [x] Primeiro acesso exibe apenas campo CPF
- [x] Validação de dígito verificador antes de exibir formulário completo
- [x] CPF inválido exibe mensagem de erro clara
- [x] POST /leads com ativacao_id registra conversão
- [x] Ativação única: bloqueio ao tentar cadastrar mesmo CPF novamente
- [x] Testes backend e Playwright cobrindo fluxo

## Navegacao Rapida

- [Intake](../INTAKE-LP-QR-ATIVACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Audit Log](../AUDIT-LOG.md)
