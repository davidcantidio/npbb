---
doc_id: "TASK-3.md"
user_story_id: "US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS"
task_id: "T3"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/models/"
  - "backend/alembic/env.py"
tdd_aplicavel: false
---

# T3 - Modelos SQLModel para idempotencia e referencias externas

## objetivo

Materializar o schema das tasks **T1** e **T2** em **classes SQLModel** (enums de dominio, relacoes opcionais, `__table_args__` para constraints), e garantir que a metadata e carregada por Alembic autogenerate conforme convencao do repo.

## precondicoes

- T1 e T2 concluidas: tabelas existem nas migrations e `alembic upgrade head` passa.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: false.
- `write_scope`: novo modulo sob `backend/app/models/` e linha de import em `backend/alembic/env.py` (e em `app.models` apenas se o projeto exigir reexport — seguir padrao existente para `etl_registry`).

## arquivos_a_ler_ou_tocar

- Revisoes Alembic das T1 e T2
- `backend/app/models/etl_registry.py` *(estilo Field, Relationship, enums)*
- `backend/app/db/metadata.py`
- `backend/alembic/env.py`
- `backend/app/models/models.py` *(apenas leitura — evitar misturar dominio de leads)*

## passos_atomicos

1. Criar modulo dedicado (ex.: `backend/app/models/external_ingest_api.py`) com duas classes `table=True` espelhando nomes de tabela e colunas das migrations.
2. Declarar enums Python alinhados aos `CheckConstraint` de status (respeitar maiusculas/minusculas do banco).
3. Se a T1 incluir FK opcional para `ingestions`, declarar `Relationship` apenas se o padrao do repo para `IngestionRun` for estavel e desejado; caso contrario manter apenas FK sem back_populates.
4. Adicionar em `backend/alembic/env.py` o import do novo modulo apos os imports existentes de modelos (`# noqa: F401`), para manter `target_metadata` completo.
5. Correr verificacao rapida: `python -c` import do modulo ou `ruff check` no ficheiro novo se aplicavel.

## comandos_permitidos

- `cd backend && .venv/bin/python -c "from app.models.external_ingest_api import *"` *(ajustar nome do modulo ao escolhido)*
- `cd backend && .venv/bin/ruff check app/models/<modulo_novo>.py`
- `cd backend && .venv/bin/alembic check` *(se disponivel no projeto)*

## resultado_esperado

Modelos ORM utilizaveis por servicos e routers futuros (US-7-02, US-7-03) sem alterar manifestos FEATURE-7/PRD.

## testes_ou_validacoes_obrigatorias

- Import do novo modulo sem erro com `PYTHONPATH` do repo (ver `docs/SETUP.md` / `AGENTS.md`).
- Nenhuma divergencia obvia de nome de tabela/coluna entre migration e modelo (revisao manual).

## stop_conditions

- Parar se autogenerate Alembic gerar diff inesperado por drift de tipos — alinhar tipo SQLAlchemy ao migration antes de prosseguir.
- Parar se for necessario editar dezenas de ficheiros legados — reduzir escopo ao import em `env.py` + modulo novo, salvo exigencia explicita do repositorio.
