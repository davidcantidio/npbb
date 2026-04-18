# Task 3 — Dedupe e idempotência no Postgres (NULL e concorrência)

**Prioridade:** P1

## Problema

A unicidade no modelo `Lead` usa `uq_lead_ticketing_dedupe(email, cpf, evento_nome, sessao)` com campos opcionais. Em PostgreSQL, **NULL não entra na unicidade** da mesma forma que valores concretos: duas linhas com a mesma combinação “efetiva” de negócio podem coexistir se partes da chave forem NULL. A aplicação tenta deduplicar com `find_existing_lead` / `build_dedupe_key` antes do insert, mas **sem lock transacional nem `ON CONFLICT`**, duas transações concorrentes podem ambas “não encontrar” e inserir duplicados.

## Escopo

- `backend/app/models/lead_public_models.py` — modelo `Lead`, constraints
- `backend/app/modules/leads_publicidade/application/etl_import/persistence.py` — `find_existing_lead`, `build_dedupe_key`, fluxo de insert
- `backend/app/services/lead_pipeline_service.py` — `_find_existing_lead` no caminho Gold
- Migrações Alembic para índices únicos funcionais ou estratégia de chave canónica alinhada à regra atual de **CPF obrigatório** (com tratamento consistente para email opcional)

## Critérios de aceite

1. Semântica de unicidade **documentada** e coerente com a regra de negócio (incluindo tratamento de NULL e sessão vazia).
2. Estratégia no banco (unique index funcional, partial indexes, ou upsert atómico) que **impede** duplicados nos cenários críticos identificados no relatório.
3. Teste de **concorrência em PostgreSQL real** (não apenas SQLite): dois imports paralelos com mesmo payload e `sessao` nula não criam dois `lead` equivalentes.
4. Query de verificação pós-teste documentada (ex.: agrupamento por chave de negócio) sem violações.

## Plano de verificação

- Teste de integração com Postgres (CI ou marcador `postgres`) disparando duas coroutines/threads com o mesmo import.
- Revisar impacto em `lead_evento` e vínculos canónicos.

## Skills recomendadas (acionar na execução)

Antes de implementar, **ler** cada skill indicada (`SKILL.md` na pasta listada) e seguir as práticas descritas.

- [.claude/skills/postgres-pro/SKILL.md](.claude/skills/postgres-pro/SKILL.md) — constraints, índices únicos, NULL em unicidade, `ON CONFLICT`.
- [.claude/skills/sql-pro/SKILL.md](.claude/skills/sql-pro/SKILL.md) — desenho de queries de verificação e migrações SQL.
- [.claude/skills/database-optimizer/SKILL.md](.claude/skills/database-optimizer/SKILL.md) — impacto de índices e padrões de escrita concorrente.
- [.claude/skills/python-pro/SKILL.md](.claude/skills/python-pro/SKILL.md) — SQLAlchemy, Alembic e camada de persistência.
- [.claude/skills/test-master/SKILL.md](.claude/skills/test-master/SKILL.md) — testes de corrida com Postgres real (marcadores CI).

## Subtarefa obrigatória: handoff ao concluir

Ao **terminar** esta tarefa (código, testes e revisão), criar o ficheiro **`auditoria/handoff-task3.md`** com:

1. **Resumo** do que foi implementado, semântica de dedupe e decisões de schema.
2. **Lista de ficheiros** tocados (criados, alterados ou removidos), com caminhos relativos à raiz do repositório; **destacar** ficheiros em `backend/alembic/versions/`.
3. **Diffs / revisão**: comandos sugeridos (ex.: `git diff main...HEAD -- backend/alembic/ backend/app/models/`), notas sobre backward compatibility e plano de deploy (locks, tempo de criação de índice).

O handoff deve permitir continuidade sem reler toda a conversa.

## Referência

Relatório completo: [auditoria/deep-research-report.md](deep-research-report.md) — secção **Achados detalhados** → **A deduplicação real depende demais do código e não fica robustamente protegida no banco**; também **Lacunas de teste e observabilidade** (corrida em Postgres).
