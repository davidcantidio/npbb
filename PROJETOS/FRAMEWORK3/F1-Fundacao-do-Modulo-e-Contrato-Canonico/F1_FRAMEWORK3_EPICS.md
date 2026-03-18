---
doc_id: "F1_FRAMEWORK3_EPICS.md"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-17"
audit_gate: "not_ready"
---

# Epicos - FRAMEWORK3 / F1 - Fundacao do Modulo e Contrato Canonico

## Objetivo da Fase

Fechar o contrato entre governanca Markdown dominio persistido e modos operacionais do FRAMEWORK3 absorvendo a regressao atual do embriao ja acoplado ao runtime.

## Gate de Saida da Fase

A baseline do backend volta a importar com o router framework habilitado o dominio canonico fica alinhado a governanca e existe contrato aprovado para sincronizacao Markdown-banco e modos do orquestrador.

## Estado do Gate de Auditoria

- gate_atual: `not_ready`
- ultima_auditoria: `nao_aplicavel`

## Checklist de Transicao de Gate

> A semantica dos vereditos e as regras de julgamento vivem em `GOV-AUDITORIA.md`.

### `not_ready -> pending`
- [ ] todos os epicos estao `done`
- [ ] todas as issues filhas estao `done`
- [ ] DoD da fase foi revisado

### `pending -> hold`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R01.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Modelo Canonico do Framework3 | Consolidar o dominio canonico do FRAMEWORK3 e estabilizar a baseline tecnica do embriao ja presente no backend. | nenhuma | todo | [EPIC-F1-01-Modelo-Canonico-do-Framework3.md](./EPIC-F1-01-Modelo-Canonico-do-Framework3.md) |
| EPIC-F1-02 | Coexistencia Markdown-Banco e Rastreabilidade | Definir como o FRAMEWORK3 convive com o filesystem documental atual com bootstrap minimo e historico rastreavel. | EPIC-F1-01 | todo | [EPIC-F1-02-Coexistencia-Markdown-Banco-e-Rastreabilidade.md](./EPIC-F1-02-Coexistencia-Markdown-Banco-e-Rastreabilidade.md) |
| EPIC-F1-03 | Contrato do AgentOrchestrator e Modos de Operacao | Formalizar a maquina de estados os gates HITL os work orders e os modos de autonomia por projeto. | EPIC-F1-01 EPIC-F1-02 | todo | [EPIC-F1-03-Contrato-do-AgentOrchestrator-e-Modos-de-Operacao.md](./EPIC-F1-03-Contrato-do-AgentOrchestrator-e-Modos-de-Operacao.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: EPIC-F1-01
- `EPIC-F1-03`: EPIC-F1-01 e EPIC-F1-02

## Escopo desta Fase

### Dentro
- estabilizar a baseline tecnica do embriao FRAMEWORK3 ja acoplado ao backend
- alinhar taxonomias entidades IDs e estados do dominio a governanca canonica
- definir sincronizacao Markdown-banco rastreabilidade e modos de operacao do orquestrador

### Fora
- CRUD completo do modulo Framework
- interface admin completa no dashboard
- pipeline de execucao review pos-issue e auditoria final de fase

## Definition of Done da Fase
- [ ] baseline do backend estabilizada para o escopo framework
- [ ] intake normalizado a taxonomia canonica e AUDIT-LOG raiz criado
- [ ] contrato canonico do dominio da sincronizacao e dos modos do orquestrador aprovado
