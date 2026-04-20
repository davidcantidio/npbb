# Task 3 — Sessões ETL: ownership, expiração e auditoria

**Prioridade:** P1

## Problema

`lead_import_etl_preview_session` guarda `session_token`, `idempotency_key`, dados do preview e estado, mas **sem dono explícito** (`created_by` / `committed_by`) nem política visível de expiração/TTL. O reaproveitamento de snapshot por `idempotency_key` é global ao escopo actual da query, o que fragiliza governança e auditoria em cenários multi-utilizador.

## Escopo

- Modelo e migração: [backend/app/models/lead_public_models.py](backend/app/models/lead_public_models.py) (ou [backend/app/models/models.py](backend/app/models/models.py) conforme re-export) — `LeadImportEtlPreviewSession`
- [backend/app/modules/leads_publicidade/application/etl_import/preview_session_repository.py](backend/app/modules/leads_publicidade/application/etl_import/preview_session_repository.py) — lookup por idempotência com **âmbito** (utilizador / tenant / `evento_id` + política definida)
- Commit ETL: vínculo `committed_by` ao utilizador autenticado
- Job ou comando de **cleanup** de sessões expiradas + documentação operacional

## Critérios de aceite

1. Colunas (ou modelo equivalente) para `created_by`, `committed_by`, `expires_at` / `last_accessed_at` (nomes finais acordados com o produto).
2. Lookup de snapshot existente **restrito** ao escopo definido (não reutilizar preview de outro operador por engano).
3. Testes de API cobrindo criação, reutilização legítima e bloqueio de reutilização cruzada.

## Plano de verificação

- Migração Alembic + testes em [backend/tests/test_leads_import_etl_endpoint.py](backend/tests/test_leads_import_etl_endpoint.py) (ou ficheiro equivalente).
- Verificar `SELECT` de sessões antigas após TTL simulado (teste com relógio mock).

## Skills recomendadas (acionar na execução)

- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md)
- [.claude/skills/fastapi-expert/SKILL.md](.claude/skills/fastapi-expert/SKILL.md)
- [.claude/skills/secure-code-guardian/SKILL.md](.claude/skills/secure-code-guardian/SKILL.md)
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md)
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md)

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa, criar **`auditoria/handoff-task3.md`** (incluir notas de migração e backfill de `created_by` se aplicável).

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — **Principais problemas encontrados** → **Sessão ETL sem dono explícito e sem política visível de expiração**; **Priorização final** (item 3).
