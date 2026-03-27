# SPEC — Índice operacional OpenClaw em Postgres (read model)

**Estado:** especificação normativa (implementação em `scripts/` / `bin/` é objeto de trabalho separado).  
**Fonte de verdade:** Markdown versionado em `PROJETOS/**/*.md` e histórico Git — **inalterável**.  
**Postgres:** modelo derivado (**read model**) para consulta operacional, full-text, vetores (`pgvector`) e integração com memória semântica do agente.

## 1. Problema e objetivo

Historicamente o índice derivado materializava-se em SQLite (`scripts/openclaw_projects_index/schema.sql`, `PRAGMA user_version = 4`), com FTS5 embutido e `embeddings.embedding` como BLOB. Isso limitava:

- consultas concurrentes e integração com stacks que já usam Postgres;
- uso nativo de similaridade vetorial (`pgvector`) e operadores ANN;
- ligação explícita entre **execução** (commits Git) e artefatos (`user_stories`, `tasks`);
- observabilidade de **sync** além de pares chave/valor em `sync_meta`.

**Objetivo:** definir o **contrato** do read model Postgres: tabelas, tipos de vetor, estratégia de sincronização desde o filesystem/Git, tabela `execution_commits` e relação com a memória maior do agente, mantendo Markdown + Git como única autoridade para criação/edição de governança.

## 2. Princípios inegociáveis

1. **Escrita canónica:** alterações de estado de projeto/feature/US/task continuam em `.md` e pastas conforme `GOV-FRAMEWORK-MASTER.md`; o sync **não** substitui commits humanos ou PRs.
2. **Postgres é derivado:** pode ser apagado e reconstruído a partir do repositório + regras de parse (idempotência do pipeline de sync).
3. **Compatibilidade semântica com v4 SQLite:** os mesmos conceitos de `sync.py` (classificação de paths, front matter, documentos globais em `PROJETOS/COMUM/`) mapeiam para linhas Postgres; nomes de colunas podem evoluir com uma camada de migração documentada.
4. **RAG:** chunks textuais permanecem ligados a `documents`; vetores em `embeddings` usando `vector(dim)` do pgvector, não BLOB opaco.

## 3. Extensões Postgres

| Extensão | Uso |
|----------|-----|
| `pgvector` | Coluna `embeddings.embedding vector(<dim>)` + índice ANN (ex.: `hnsw` ou `ivfflat`) quando houver volume suficiente. |
| `pg_trgm` ou `tsvector` | Busca lexical complementar (paridade aproximada ao FTS5 do SQLite); a spec **não** obriga uma única escolha — ver §8. |

`uuid-ossp` ou `pgcrypto` (opcional) para `gen_random_uuid()` em chaves expostas a APIs externas.

## 4. Modelo lógico — tabelas obrigatórias

Todas as tabelas abaixo **devem** existir no schema alvo. Tipos concretos são indicativos; a implementação fixa `NUMERIC` precisões e `TEXT` vs `VARCHAR` em DDL versionado.

**Inventário explícito (requisito normativo T14):** o read model Postgres prevê **obrigatoriamente** as relações nomeadas:

`projects`, `project_documents`, `features`, `user_stories`, `tasks`, `feature_audits`, `documents`, `document_chunks`, `embeddings`, `execution_commits`, `sync_runs`.

Cada uma tem secção dedicada em §4 (§4.2–§4.8; `features` … `feature_audits` em §4.4).

### 4.1 `sync_runs`

Registo append-only de cada execução do sync (observabilidade, debugging, SLAs).

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `started_at` | `timestamptz` NOT NULL | |
| `finished_at` | `timestamptz` | NULL enquanto a correr |
| `status` | `text` NOT NULL | ex.: `running`, `success`, `failed`, `partial` |
| `repo_root` | `text` NOT NULL | path absoluto usado |
| `git_head` | `text` | SHA curto ou completo após sync |
| `schema_version` | `text` NOT NULL | alinhado a bundle Postgres (ex.: `pg-1`) |
| `rows_upserted` | `jsonb` | contagens por entidade (opcional) |
| `error_message` | `text` | se `failed` |
| `trigger_source` | `text` | ex.: `cli`, `ci`, `skill`, `cron` |

**Regra:** ao iniciar sync, inserir linha `running`; ao terminar, atualizar `finished_at`, `status`, `git_head`. Rollback transacional da corrida inteira é preferível a estado inconsistente; se usar staging tables, documentar em implementação.

### 4.2 `projects`

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | substitui `INTEGER` SQLite |
| `slug` | `text` NOT NULL UNIQUE | ex.: pasta `PROJETOS/<slug>/` |
| `name_display` | `text` | |
| `created_at` / `updated_at` | `timestamptz` | |

Critério de inclusão em `projects` mantém-se alinhado ao índice atual (presença de artefatos canónicos do projeto, cf. `README.md` do índice).

### 4.3 `project_documents`

Metadados de documentos **ao nível do projeto** (PRD, intake, audit log, encerramento, etc.), sem duplicar o corpo — corpo em `documents`.

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `project_id` | `bigint` NOT NULL FK → `projects(id)` ON DELETE CASCADE | |
| `doc_type` | `text` NOT NULL | ex.: `PRD`, `INTAKE`, `AUDIT_LOG`, … |
| `status` | `text` | |
| `intake_kind`, `source_mode`, `intake_slug` | `text` | paridade com SQLite v4 |
| `path_relative` | `text` NOT NULL UNIQUE | path POSIX relativo à raiz do repo |
| `created_at` / `updated_at` | `timestamptz` | |

### 4.4 `features` / `user_stories` / `tasks` / `feature_audits`

Estrutura análoga a `schema.sql` v4:

- `features`: `project_id`, `feature_key`, `feature_number`, `name_display`, `status`, `audit_gate`, `path_relative` UNIQUE, timestamps.
- `user_stories`: `project_id`, `feature_id`, `user_story_key`, `layout`, `status`, `task_instruction_mode`, `decision_refs_json` (JSONB em Postgres), `path_relative` UNIQUE, timestamps.
- `tasks`: `user_story_id`, `task_number`, `task_id`, `status`, `tdd_aplicavel` (`boolean`), `path_relative` UNIQUE, timestamps.
- `feature_audits`: `feature_id`, `report_key`, `status`, `verdict`, `scope_type`, `scope_ref`, `feature_code`, `base_commit`, `compares_to`, `round_number`, `supersedes`, `followup_destination`, `decision_refs_json`, `path_relative` UNIQUE, timestamps.

**Unicidade:** reproduzir as UNIQUE do SQLite para evitar duplicados no mesmo projeto/feature.

### 4.5 `documents`

Tabela unificada de conteúdo indexado (corpo + front matter serializado).

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `path_relative` | `text` NOT NULL UNIQUE | |
| `kind` | `text` NOT NULL | classificação do sync |
| `project_id` | `bigint` FK → `projects` nullable | NULL para `PROJETOS/COMUM/*` |
| `feature_id`, `user_story_id`, `task_id`, `feature_audit_id` | `bigint` FK nullable | |
| `title` | `text` | |
| `body_markdown` | `text` | |
| `front_matter_json` | `jsonb` | parse YAML → JSON canónico |
| `content_hash` | `text` NOT NULL | ex.: SHA-256 do ficheiro normalizado |
| `file_mtime` | `bigint` | epoch segundos (opcional) |
| `indexed_at` | `timestamptz` NOT NULL | |
| `created_at` / `updated_at` | `timestamptz` | |

**Governança em COMUM:** ficheiros sob `PROJETOS/COMUM/` mapeiam para `documents` com `project_id IS NULL` e `kind` adequado (paridade com `governance_kind_from_filename` no sync atual). Não é obrigatória tabela separada `governance_documents` no Postgres se o contrato de consulta usar `documents` filtrados por `kind` e path; para queries legadas, pode expor-se uma **VIEW** `governance_documents` compatível.

### 4.6 `document_chunks`

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `document_id` | `bigint` NOT NULL FK → `documents(id)` ON DELETE CASCADE | |
| `chunk_index` | `int` NOT NULL | UNIQUE com `document_id` |
| `text` | `text` NOT NULL | |
| `token_count` | `int` | opcional |
| `content_hash` | `text` | hash do chunk |
| `created_at` / `updated_at` | `timestamptz` | |

### 4.7 `embeddings`

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `chunk_id` | `bigint` NOT NULL FK → `document_chunks(id)` ON DELETE CASCADE | |
| `model` | `text` NOT NULL | ex.: `text-embedding-3-large` |
| `embedding` | `vector(<dim>)` NOT NULL | dimensão fixa por modelo |
| `created_at` | `timestamptz` | |
| UNIQUE (`chunk_id`, `model`) | | |

**Índices:** criar índice ANN em `embedding` quando o volume justificar; para poucos milhares de linhas, scan exaustivo pode ser aceitável em dev.

**Pipeline:** o sync **não** precisa gerar embeddings; um job assíncrono lê chunks novos ou com `content_hash` alterado e faz upsert em `embeddings`.

### 4.8 `execution_commits`

Liga **commits Git** (ou revisões) a trabalho de execução/review, sem substituir o Git log.

| Coluna | Tipo sugerido | Notas |
|--------|----------------|-------|
| `id` | `bigserial` PK | |
| `commit_sha` | `text` NOT NULL | SHA completo (40 hex) |
| `commit_short` | `text` | gerado para UI |
| `committed_at` | `timestamptz` | de `git show` se disponível |
| `author_email` | `text` | opcional |
| `message_subject` | `text` | primeira linha |
| `project_id` | `bigint` FK → `projects` nullable | |
| `feature_id` | `bigint` FK nullable | |
| `user_story_id` | `bigint` FK nullable | |
| `task_id` | `bigint` FK nullable | |
| `phase` | `text` NOT NULL | ex.: `execution`, `review_fix`, `audit_remediation` |
| `source` | `text` | ex.: `agent`, `human`, `ci` |
| `evidence_path_relative` | `text` | path a `.md` que cita o commit (opcional) |
| `recorded_at` | `timestamptz` NOT NULL DEFAULT `now()` | |

**Regras:**

- Pelo menos um de (`user_story_id`, `task_id`, `evidence_path_relative`) deve estar preenchido em ingestão estrita (política aplicável via CHECK ou validação no loader).
- O mesmo `commit_sha` pode aparecer em várias linhas se tocar várias US/tasks (normalização opcional: tabela N:N no futuro).
- Preenchimento típico: parser de corpo de `README.md` da US, secção de evidências, ou convenção de tag no commit; **fora de escopo** desta spec definir o parser — apenas o **contrato relacional**.

## 5. Estratégia de sync (filesystem → Postgres)

1. **Deteção de alterações:** comparar `content_hash` e/ou `file_mtime` com linhas existentes em `documents`; paths removidos no Git → DELETE em cascata nas FKs (ou marcação `tombstone` se se preferir arquivo — documentar escolha).
2. **Ordem de ingestão:** `projects` → entidades estruturadas (`features`, `user_stories`, `tasks`, `feature_audits`, `project_documents`) → `documents` (conteúdo) → (opcional) rebuild de chunks apenas para documentos alterados.
3. **Transacções:** uma transação por `sync_run` ou por projeto, conforme tamanho do repo; falhas parciais devem refletir-se em `sync_runs.status = partial` com `error_message`.
4. **Metadados globais:** substituir `sync_meta` key-value por consultas a `sync_runs` (último sucesso) + colunas em `projects` se necessário; chaves legadas como `last_sync_at` podem ser **VIEW** sobre `sync_runs`.
5. **Compatibilidade legada controlada:** SQLite só entra em migração/backfill explícitos; durante esses fluxos, o mesmo código de classificação/parsing pode alimentar ambos os destinos ou gerar Parquet/JSON intermédio. A spec recomenda **uma única biblioteca de domínio** partilhada para evitar drift.

## 6. pgvector e memória do agente

### 6.1 Papel do índice

- `document_chunks` + `embeddings` formam o **substrato recuperável** sobre a governança versionada (PRD, sessions, GOV, features, US, tasks, relatórios).
- Consultas de similaridade: `ORDER BY embedding <=> :query_vector LIMIT k` (cosine / L2 conforme métrica escolhida e normalização do modelo).

### 6.2 Integração com “memória maior”

O agente pode ter lojas adicionais (logs, SOUL, notas fora de `PROJETOS/`). O contrato Postgres deve permitir:

| Mecanismo | Descrição |
|-----------|-----------|
| `documents.path_relative` | Ancoragem determinística ao repo; qualquer ferramenta de memória pode guardar `path_relative` + `chunk_id` como referência estável. |
| `embeddings.model` | Desambiguação quando a memória externa agrega vetores de vários modelos. |
| Coluna futura opcional `external_memory_ref` em `embeddings` ou `document_chunks` | UUID ou URI lógico para linha num grafo/memória externa — **reservar** em migrações futuras se necessário, sem obrigar na v1. |

**Invariante:** embeddings derivados de `PROJETOS/` **devem** ser reproduzíveis a partir do Git + modelo + parâmetros de chunking; memória externa pode referenciar mas não substitui o SoT.

## 7. Variáveis de ambiente (contrato)

| Variável | Descrição |
|----------|-----------|
| `OPENCLAW_REPO_ROOT` | Raiz do clone (contém `PROJETOS/`). |
| `OPENCLAW_PROJECTS_DATABASE_URL` | URL Postgres (ex.: `postgresql://user:pass@localhost:5432/openclaw_projects`). Preferência sobre host/port/user/db soltos. |
| `OPENCLAW_PGSSLMODE` | Opcional; default alinhado ao cliente. |

Compatibilidade legada de migracao/backfill:

- `OPENCLAW_PROJECTS_DATABASE_URL` continua sendo a unica variavel operacional do indice.
- snapshots SQLite historicos, quando ainda precisarem ser importados, devem ser fornecidos por caminho explicito aos utilitarios em `scripts/openclaw_projects_index/legacy/`.

Documentar em `scripts/openclaw_projects_index/README.md` (ou sucessor) a separacao entre runtime operacional Postgres e compatibilidade legada de migracao.

## 8. Busca lexical (paridade FTS5)

Opções normativas equivalentes:

- **tsvector:** coluna gerada ou materializada em `documents` + índice GIN;
- **pg_trgm:** índice GIN em `title` + trecho de `body_markdown` para fuzzy match.

A spec exige **pelo menos uma** forma de busca full-text ou sub-string indexada para substituir `documents_fts` do SQLite; a escolha final fica na implementação com benchmarks em `PROJETOS/` típico.

## 9. Migração desde SQLite v4

1. Exportar dados estruturados e `documents` (CSV ou `COPY`) com mapeamento `INTEGER` → `bigint`.
2. `embeddings.embedding`: converter BLOB (float32 little-endian) para literal `vector` ou usar script de ingestão.
3. Backfill `sync_runs` com uma linha sintética `status=success` e `schema_version` indicando migração.
4. `execution_commits`: vazio na migração one-shot salvo pipeline pré-existente que parse evidências.

## 10. Critérios de aceite (esta spec)

- [ ] **T14 — tabelas nomeadas:** o DDL alvo materializa as onze relações: `sync_runs`, `projects`, `project_documents`, `features`, `user_stories`, `tasks`, `feature_audits`, `documents`, `document_chunks`, `embeddings`, `execution_commits`.
- [ ] Todas as entidades listadas em §4 existem com FKs e unicidades alinhadas ao modelo v4 onde aplicável.
- [ ] `embeddings` usa tipo `vector` (pgvector), não BLOB genérico.
- [ ] `sync_runs` permite auditar cada corrida de indexação.
- [ ] `execution_commits` modela ligação Git ↔ artefatos de execução sem contradizer SoT Markdown.
- [ ] Documento declara explicitamente Markdown + Git como fonte de verdade e Postgres como read model derivado.

## 11. Referências internas

- `scripts/openclaw_projects_index/schema.sql` — paridade semântica SQLite v4.
- `scripts/openclaw_projects_index/schema_postgres.sql` — DDL Postgres bundle `pg-1` (aplicar com `./bin/apply-openclaw-projects-pg-schema.sh`).
- `scripts/openclaw_projects_index/legacy/mirror_sqlite_to_postgres.py` — espelho opcional SQLite → Postgres em fluxos legados de migracao.
- `scripts/openclaw_projects_index/legacy/migrate_sqlite_embeddings_to_postgres.py` — migracao opcional de embeddings BLOB historicos para `pgvector`.
- `scripts/openclaw_projects_index/sync.py` — classificação de paths e campos extraídos; runtime operacional exclusivamente Postgres.
- `scripts/openclaw_projects_index/README.md` — variáveis operacionais Postgres e fluxos legados de migracao/backfill.
- `PROJETOS/COMUM/SPEC-PIPELINE-PRD-SEM-FEATURES.md` — contexto da migração normativa do pipeline.

---

*Versão do documento: 1.1 — especificação Postgres; DDL base em `schema_postgres.sql`; sync direto filesystem→Postgres permanece evolutivo.*
