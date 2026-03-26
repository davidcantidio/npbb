# Índice derivado de `PROJETOS/` (OpenClaw)

A **fonte de verdade** são os ficheiros Markdown e a árvore em `PROJETOS/` no Git.

Este módulo suporta:

- **SQLite** (default): rebuild completo via `sync.py` (schema v4, `sync_meta` + FTS5).
- **Postgres** (read model alvo): ingestão direta com `sync.py --backend postgres`, DDL `schema_postgres.sql` (bundle `pg-1`), `pgvector`, `sync_runs`, `execution_commits`. Contrato normativo: [`PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md`](../../PROJETOS/COMUM/SPEC-INDICE-PROJETOS-POSTGRES.md).

**Coexistência:** pode manter só SQLite, só Postgres ou ambos (parse único em `domain.py` + `sync.py`; um destino por invocação).

O layout canônico de entrega continua `Feature -> User Story -> Task` sob `features/`.

## Ficheiros

| Ficheiro | Função |
|----------|--------|
| [`domain.py`](domain.py) | Classificação de paths, parsing YAML, utilitários partilhados (sem driver SQL) |
| [`build_local_pyyaml_wheel.py`](build_local_pyyaml_wheel.py) | Exporta um wheel local puro de `PyYAML` para deploys e smokes remotos |
| [`requirements.txt`](requirements.txt) | `PyYAML` + `psycopg[binary]` (Postgres opcional até usar `--backend postgres`) |
| [`requirements-postgres.txt`](requirements-postgres.txt) | Legado: apenas `psycopg`; preferir `requirements.txt` |
| [`schema.sql`](schema.sql) | DDL SQLite v4 |
| [`schema_postgres.sql`](schema_postgres.sql) | DDL Postgres `pg-1` + `vector`, `sync_runs`, `execution_commits`, GIN/tsvector em `documents` |
| [`sync.py`](sync.py) | Varredura `PROJETOS/**/*.md`, rebuild para SQLite **ou** Postgres |
| [`mirror_sqlite_to_postgres.py`](mirror_sqlite_to_postgres.py) | Opcional: copia dados já materializados em SQLite v4 para Postgres (fluxo legado) |
| [`migrate_sqlite_embeddings_to_postgres.py`](migrate_sqlite_embeddings_to_postgres.py) | BLOB float32 (SQLite) → `vector` (Postgres), alinhando por `path_relative` + `chunk_index` + `model` |
| [`chunk_documents.py`](chunk_documents.py) | Preenche `document_chunks` a partir de `documents.body_markdown` (SQLite ou Postgres) |

## Sincronizar

Na raiz do repositório:

```bash
./bin/ensure-openclaw-projects-index-runtime.sh
./bin/sync-openclaw-projects-db.sh
```

Postgres (após criar BD e extensões `vector` + `pg_trgm`):

```bash
export OPENCLAW_PROJECTS_DATABASE_URL='postgresql://user:pass@localhost:5432/openclaw_projects'
./bin/apply-openclaw-projects-pg-schema.sh   # opcional: sync.py também aplica o DDL
./bin/sync-openclaw-projects-db.sh -- --backend postgres
```

Ou diretamente:

```bash
python3 scripts/openclaw_projects_index/sync.py [--repo-root PATH] [--db PATH] \
  [--backend sqlite|postgres] [--dry-run] [--sync-trigger cli]
```

### Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `OPENCLAW_REPO_ROOT` | Raiz do clone (deve conter `PROJETOS/`). |
| `OPENCLAW_PROJECTS_DB` | Caminho do `.sqlite` (só backend `sqlite`). Default: `<repo>/.openclaw/openclaw-projects.sqlite` |
| `OPENCLAW_PROJECTS_DATABASE_URL` | URL Postgres (obrigatório para `--backend postgres`). |
| `OPENCLAW_PGSSLMODE` | Opcional; anexado à URL se não houver `sslmode=`. |
| `OPENCLAW_PROJECTS_INDEX_BACKEND` | Default do CLI se não passar `--backend` (`sqlite` ou `postgres`). |

### Matriz de backends

| Destino | Comando típico | Validação smoke / host |
|---------|----------------|-------------------------|
| SQLite | `sync.py` (default) | `sync_meta.last_sync_at` + `repo_root` |
| Postgres | `sync.py --backend postgres` | Última linha em `sync_runs` com `status=success` e `repo_root` alinhado ao clone |

## Postgres: schema e espelho

1. Instalar extensões **vector** e **pg_trgm** no servidor.
2. Definir `OPENCLAW_PROJECTS_DATABASE_URL`.
3. Aplicar DDL (idempotente):

```bash
./bin/apply-openclaw-projects-pg-schema.sh
```

4. Sync direto para Postgres (recomendado):

```bash
./bin/sync-openclaw-projects-db.sh -- --backend postgres
```

5. **Alternativa legada:** manter SQLite e usar `mirror_sqlite_to_postgres.py` / `bin/mirror-openclaw-projects-sqlite-to-pg.sh`.

6. **Embeddings:** o mirror não converte BLOB → `vector`; usar `migrate_sqlite_embeddings_to_postgres.py` após `chunk_documents` alinhado nos dois lados, ou regerar embeddings no Postgres.

### Busca full-text no Postgres

Coluna gerada `documents.search_vector` (GIN). Exemplo:

```sql
SELECT path_relative, title
FROM documents
WHERE search_vector @@ plainto_tsquery('simple', 'openrouter')
LIMIT 20;
```

## Contrato do schema v4 (SQLite)

Tabelas estruturadas:

- `projects`, `features`, `user_stories`, `tasks`, `feature_audits`
- `governance_documents`, `project_documents`, `documents`, `documents_fts`
- `document_chunks`, `embeddings`, `sync_meta`

Postgres acrescenta `sync_runs`, `execution_commits` e não usa `sync_meta` (estado de corrida em `sync_runs`).

Layout estrutural suportado:

- `PROJETOS/<PROJETO>/features/FEATURE-*/FEATURE-*.md`
- `PROJETOS/<PROJETO>/features/FEATURE-*/user-stories/US-*/README.md`
- `PROJETOS/<PROJETO>/features/FEATURE-*/user-stories/US-*/TASK-N.md`
- `PROJETOS/<PROJETO>/features/FEATURE-*/auditorias/RELATORIO-AUDITORIA-F<N>-R<NN>.md`
- `PROJETOS/<PROJETO>/encerramento/RELATORIO-ENCERRAMENTO.md`

### Corte seco do layout legado

Artefatos legados `F*/issues/`, `EPIC-*`, `SPRINT-*` e auditorias de fase:

- continuam indexados em `documents`
- entram em `documents_fts` (SQLite) ou tsvector (Postgres)
- **não** populam `features`, `user_stories`, `tasks` ou `feature_audits`

## Contrato para skills e backends

1. **Escrita:** persistir em `.md` e pastas conforme governança; em seguida invocar o sync.
2. **Leitura operacional:** SQL sobre `projects`, `features`, `user_stories`, `tasks`, `feature_audits`.
3. **Leitura documental:** `documents` (+ FTS conforme backend).
4. **Descoberta de projeto:** apenas diretórios canónicos em `projects` (`INTAKE-*`, `PRD-*`, `AUDIT-LOG.md`).

### Metadados de sync

**SQLite:**

```sql
SELECT key, value FROM sync_meta;
-- last_sync_at, repo_root, schema_bundle_version
```

**Postgres:**

```sql
SELECT id, started_at, finished_at, status, repo_root, git_head, schema_version
FROM sync_runs
ORDER BY id DESC
LIMIT 5;
```

### Consultas úteis

Feature por projeto:

```sql
SELECT f.feature_key, f.status, f.audit_gate, f.path_relative
FROM features f
JOIN projects p ON p.id = f.project_id
WHERE p.slug = 'DEMO';
```

User Stories por feature:

```sql
SELECT us.user_story_key, us.status, us.task_instruction_mode, us.path_relative
FROM user_stories us
JOIN features f ON f.id = us.feature_id
WHERE f.feature_key = 'FEATURE-1-FUNDACAO';
```

Busca full-text (SQLite):

```sql
SELECT d.path_relative, d.title
FROM documents_fts
JOIN documents d ON d.id = documents_fts.rowid
WHERE documents_fts MATCH 'openrouter'
LIMIT 20;
```

## Chunks e embeddings (RAG)

1. Correr `sync.py` (SQLite ou Postgres).
2. Correr `chunk_documents.py` com o mesmo backend:

```bash
python3 scripts/openclaw_projects_index/chunk_documents.py --db "$OPENCLAW_PROJECTS_DB"
python3 scripts/openclaw_projects_index/chunk_documents.py --backend postgres
```

3. Preencher `embeddings` noutro pipeline; migração BLOB (SQLite) → `vector`:

```bash
python3 scripts/openclaw_projects_index/migrate_sqlite_embeddings_to_postgres.py \
  --sqlite-db "$OPENCLAW_PROJECTS_DB"
```

**Nota:** a coluna `embeddings.embedding` no Postgres é `vector(1536)` por omissão; o vetor migrado deve ter a mesma dimensão.
