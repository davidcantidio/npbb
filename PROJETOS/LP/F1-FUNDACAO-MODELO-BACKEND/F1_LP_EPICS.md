---
doc_id: "F1_LP_EPICS.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-12"
audit_gate: "pending"
---

# Epicos - LP / F1 - Fundação (Modelo e Backend)

## Objetivo da Fase

Estabelecer o modelo de dados (Ativacao, conversao_ativacao, lead_reconhecimento_token), CRUD de ativações para operadores, geração de QR por ativação e endpoint de landing com contexto de evento e ativação.

## Gate de Saida da Fase

O backend possui modelos e migrações aplicáveis, endpoints CRUD de ativações protegidos por autenticação, geração de QR por ativação e endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing` retornando payload da landing.

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
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `hold`
- [ ] o estado do gate foi atualizado para `hold`

### `pending -> approved`
- [ ] existe `RELATORIO-AUDITORIA-F1-R<NN>.md`
- [ ] `AUDIT-LOG.md` foi atualizado
- [ ] o veredito da auditoria e `go`
- [ ] o estado do gate foi atualizado para `approved`

## Epicos

| ID | Nome | Objetivo | Depende de | Status | Arquivo |
|---|---|---|---|---|---|
| EPIC-F1-01 | Modelo e Migrações | Tabelas ativacao, conversao_ativacao e lead_reconhecimento_token com migrations Alembic | nenhuma | done | [EPIC-F1-01-MODELO-E-MIGRACOES.md](./EPIC-F1-01-MODELO-E-MIGRACOES.md) |
| EPIC-F1-02 | CRUD de Ativações | Endpoints para criar, editar e listar ativações (operador autenticado) | EPIC-F1-01 | done | [EPIC-F1-02-CRUD-ATIVACOES.md](./EPIC-F1-02-CRUD-ATIVACOES.md) |
| EPIC-F1-03 | Geração de QR e Endpoint de Landing | Serviço de geração de QR e endpoint GET landing com contexto de ativação | EPIC-F1-01 | done | [EPIC-F1-03-QR-E-ENDPOINT-LANDING.md](./EPIC-F1-03-QR-E-ENDPOINT-LANDING.md) |

## Dependencias entre Epicos

- `EPIC-F1-01`: nenhuma
- `EPIC-F1-02`: depende de `EPIC-F1-01`
- `EPIC-F1-03`: depende de `EPIC-F1-01`

## Escopo desta Fase

### Dentro
- Modelo `Ativacao` com vínculo a evento, QR único, flag conversão única/múltipla
- Tabela `conversao_ativacao` com índice (ativacao_id, cpf)
- Tabela `lead_reconhecimento_token` para tokens de sessão
- CRUD de ativações protegido por autenticação de operador
- Geração de QR-code único por ativação
- Endpoint `GET /eventos/:evento_id/ativacoes/:ativacao_id/landing` com payload da landing

### Fora
- Fluxo CPF-first no frontend
- Validação de CPF e registro de conversão
- Mecanismo de reconhecimento (cookie/token)
- Interface de operador no frontend

## Definition of Done da Fase

- [x] Tabela `ativacao` criada com migration
- [x] Tabela `conversao_ativacao` criada com índice (ativacao_id, cpf)
- [x] Tabela `lead_reconhecimento_token` criada
- [x] Endpoints CRUD de ativações operacionais e protegidos
- [x] Cada ativação gera QR-code único
- [x] Endpoint de landing retorna payload com evento, ativação e formulário configurado
- [x] Testes backend cobrindo cenários críticos

## Navegacao Rapida

- [Intake](../INTAKE-LP-QR-ATIVACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Audit Log](../AUDIT-LOG.md)
