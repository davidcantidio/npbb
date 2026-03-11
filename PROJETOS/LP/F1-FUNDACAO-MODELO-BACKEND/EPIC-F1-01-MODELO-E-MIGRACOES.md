---
doc_id: "EPIC-F1-01-MODELO-E-MIGRACOES.md"
version: "1.1"
status: "active"
owner: "PM"
last_updated: "2026-03-11"
---

# EPIC-F1-01 - Modelo e Migrações

## Objetivo

Criar os modelos SQLModel e migrações Alembic para `ativacao`, `conversao_ativacao` e `lead_reconhecimento_token`, conforme especificado no PRD seção 6.

## Resultado de Negocio Mensuravel

O banco de dados suporta ativações vinculadas a eventos, conversões por ativação com bloqueio de CPF duplicado, e tokens de reconhecimento para leads entre ativações do mesmo evento.

## Contexto Arquitetural

- Modelos em `backend/app/models/models.py` (SQLModel, table=True)
- Migrations Alembic em `backend/alembic/versions/`
- Tabela `evento` já existente; FK `evento_id` em `ativacao`
- Índice composto `(ativacao_id, cpf)` em `conversao_ativacao` para lookup rápido
- Tabela `lead_reconhecimento_token`: lead_id, evento_id, token_hash, expires_at

## Definition of Done do Epico

- [x] Modelo `Ativacao` validado no contrato vigente: id, evento_id, nome, descricao, `checkin_unico`, qr_code_url, created_at, updated_at
- [ ] Modelo `ConversaoAtivacao` (ou equivalente) com: id, ativacao_id, lead_id, cpf, created_at
- [ ] Modelo `LeadReconhecimentoToken` com: lead_id, evento_id, token_hash, expires_at
- [ ] Migrations aplicáveis em banco limpo e com dados existentes
- [ ] Rollback das migrations sem efeito colateral
- [ ] Testes de criação/leitura dos modelos passam

## Issues do Epico

| Issue ID | Nome | Objetivo | SP | Status | Documento |
|---|---|---|---|---|---|
| ISSUE-F1-01-001 | Modelo Ativacao e migration | Validar o modelo `Ativacao` e a chain Alembic existente | 2 | done | [ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md](./issues/ISSUE-F1-01-001-MODELO-ATIVACAO-E-MIGRATION.md) |
| ISSUE-F1-01-002 | Modelos conversao_ativacao e lead_reconhecimento_token | Criar modelos e migrations para conversão e token de reconhecimento | 3 | todo | [ISSUE-F1-01-002-MODELOS-CONVERSAO-E-TOKEN.md](./issues/ISSUE-F1-01-002-MODELOS-CONVERSAO-E-TOKEN.md) |

## Artifact Minimo do Epico

- `backend/app/models/models.py`
- `backend/alembic/versions/`

## Dependencias

- [Intake](../INTAKE-LP-QR-ATIVACOES.md)
- [PRD](../PRD-LP-QR-ATIVACOES.md)
- [Fase](./F1_LP_EPICS.md)
