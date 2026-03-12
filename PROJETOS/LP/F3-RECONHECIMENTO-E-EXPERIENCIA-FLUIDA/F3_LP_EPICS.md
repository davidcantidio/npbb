---
doc_id: "F3_LP_EPICS.md"
version: "1.0"
status: "active"
owner: "PM"
last_updated: "2026-03-12"
audit_gate: "pending"
---

# Epicos - LP / F3 - Reconhecimento e Experiência Fluida

## Objetivo da Fase

Implementar mecanismo de reconhecimento (cookie + token na URL), lead reconhecido pula CPF, ativação múltipla vai direto ao formulário, ativação única oferece opção "Registrar outro CPF".

## Gate de Saida da Fase

O lead que já converteu em uma ativação do evento, ao acessar outra ativação via QR, é reconhecido (cookie ou token) e não repete CPF. Em ativação múltipla, vai direto ao formulário. Em ativação única já convertida, vê opção "Registrar outro CPF".

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
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F3-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F3-01 | Mecanismo de Reconhecimento | Cookie `lp_lead_token` emitido pelo backend + token na URL; validação e lead_reconhecido | F1, F2 | done | [EPIC-F3-01-MECANISMO-RECONHECIMENTO.md](./EPIC-F3-01-MECANISMO-RECONHECIMENTO.md) |
| EPIC-F3-02 | Experiência Fluida e "Registrar outro CPF" | Lead reconhecido pula CPF; ativação múltipla formulário direto; opção registrar outro | F2, EPIC-F3-01 | done | [EPIC-F3-02-EXPERIENCIA-FLUIDA.md](./EPIC-F3-02-EXPERIENCIA-FLUIDA.md) |

## Dependencias entre Epicos

- `EPIC-F3-01`: depende de F1 e F2
- `EPIC-F3-02`: depende de F2 e EPIC-F3-01

## Escopo desta Fase

### Dentro
- Cookie HTTP-only `lp_lead_token` com TTL 7 dias
- Token na URL `?token=` para fallback (link compartilhado)
- Tabela lead_reconhecimento_token para persistência
- Endpoint GET /leads/reconhecer?token=
- POST /leads retorna token_reconhecimento e emite `Set-Cookie` para `lp_lead_token`
- Lead reconhecido: pular etapa CPF
- Ativação múltipla: formulário direto
- Ativação única: opção "Registrar outro CPF" quando já converteu

### Fora
- Suporte a múltiplos eventos no mesmo fluxo (v1)
- Fingerprinting para mitigar burla

## Definition of Done da Fase

- [x] Cookie `lp_lead_token` emitido via `Set-Cookie` no submit
- [x] Token na URL validado
- [x] Lead reconhecido não repete CPF
- [x] Ativação múltipla: formulário direto
- [x] Ativação única: opção "Registrar outro CPF" quando já converteu
- [x] Testes cobrindo cenários

## Navegacao Rapida

- [Intake](../INTAKE-LP-QR-ATIVACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Audit Log](../AUDIT-LOG.md)
