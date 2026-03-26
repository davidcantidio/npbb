-- OpenClaw: read model Postgres derivado de PROJETOS/**/*.md (fonte de verdade = Git + Markdown).
-- Bundle: pg-1 — aplicar com psql ou apply-openclaw-projects-pg-schema.sh após instalar pgvector.
--
-- Extensões: vector (pgvector). Dimensão default do embedding: 1536 (ajustar por modelo).

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------------
-- sync_runs: observabilidade de cada corrida de indexação
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sync_runs (
  id                bigserial PRIMARY KEY,
  started_at        timestamptz NOT NULL DEFAULT now(),
  finished_at       timestamptz,
  status            text NOT NULL,
  repo_root         text NOT NULL,
  git_head          text,
  schema_version    text NOT NULL DEFAULT 'pg-1',
  rows_upserted     jsonb,
  error_message     text,
  trigger_source    text
);

CREATE INDEX IF NOT EXISTS idx_sync_runs_started ON sync_runs (started_at DESC);

-- ---------------------------------------------------------------------------
-- projects
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
  id            bigserial PRIMARY KEY,
  slug          text NOT NULL UNIQUE,
  name_display  text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- project_documents
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS project_documents (
  id              bigserial PRIMARY KEY,
  project_id      bigint NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  doc_type        text NOT NULL,
  status          text,
  intake_kind     text,
  source_mode     text,
  intake_slug     text,
  path_relative   text NOT NULL UNIQUE,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_project_documents_project ON project_documents (project_id);

-- ---------------------------------------------------------------------------
-- governance_documents (paridade SQLite v4; referenciado por documents)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS governance_documents (
  id              bigserial PRIMARY KEY,
  kind            text NOT NULL,
  doc_id          text,
  filename        text NOT NULL,
  path_relative   text NOT NULL UNIQUE,
  version         text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- features
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS features (
  id              bigserial PRIMARY KEY,
  project_id      bigint NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  feature_key     text NOT NULL,
  feature_number  integer,
  name_display    text,
  status          text,
  audit_gate      text,
  path_relative   text NOT NULL UNIQUE,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (project_id, feature_key)
);

CREATE INDEX IF NOT EXISTS idx_features_project ON features (project_id);
CREATE INDEX IF NOT EXISTS idx_features_status ON features (status);
CREATE INDEX IF NOT EXISTS idx_features_audit_gate ON features (audit_gate);

-- ---------------------------------------------------------------------------
-- user_stories
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_stories (
  id                      bigserial PRIMARY KEY,
  project_id              bigint NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  feature_id              bigint NOT NULL REFERENCES features (id) ON DELETE CASCADE,
  user_story_key          text NOT NULL,
  layout                  text NOT NULL DEFAULT 'folder',
  status                  text,
  task_instruction_mode   text,
  decision_refs_json      jsonb,
  path_relative           text NOT NULL UNIQUE,
  created_at              timestamptz NOT NULL DEFAULT now(),
  updated_at              timestamptz NOT NULL DEFAULT now(),
  UNIQUE (project_id, user_story_key)
);

CREATE INDEX IF NOT EXISTS idx_user_stories_project ON user_stories (project_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_feature ON user_stories (feature_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_status ON user_stories (status);

-- ---------------------------------------------------------------------------
-- tasks
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
  id              bigserial PRIMARY KEY,
  user_story_id   bigint NOT NULL REFERENCES user_stories (id) ON DELETE CASCADE,
  task_number     integer NOT NULL,
  task_id         text,
  status          text,
  tdd_aplicavel   boolean NOT NULL DEFAULT false,
  path_relative   text NOT NULL UNIQUE,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_story_id, task_number)
);

CREATE INDEX IF NOT EXISTS idx_tasks_user_story ON tasks (user_story_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

-- ---------------------------------------------------------------------------
-- feature_audits
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feature_audits (
  id                      bigserial PRIMARY KEY,
  feature_id              bigint NOT NULL REFERENCES features (id) ON DELETE CASCADE,
  report_key              text NOT NULL,
  status                  text,
  verdict                 text,
  scope_type              text,
  scope_ref               text,
  feature_code            text,
  base_commit             text,
  compares_to             text,
  round_number            integer,
  supersedes              text,
  followup_destination    text,
  decision_refs_json      jsonb,
  path_relative           text NOT NULL UNIQUE,
  created_at              timestamptz NOT NULL DEFAULT now(),
  updated_at              timestamptz NOT NULL DEFAULT now(),
  UNIQUE (feature_id, report_key)
);

CREATE INDEX IF NOT EXISTS idx_feature_audits_feature ON feature_audits (feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_audits_status ON feature_audits (status);
CREATE INDEX IF NOT EXISTS idx_feature_audits_verdict ON feature_audits (verdict);

-- ---------------------------------------------------------------------------
-- documents (conteúdo unificado + governança COMUM via kind / path)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
  id                    bigserial PRIMARY KEY,
  path_relative         text NOT NULL UNIQUE,
  kind                  text NOT NULL,
  project_id            bigint REFERENCES projects (id) ON DELETE CASCADE,
  feature_id            bigint REFERENCES features (id) ON DELETE CASCADE,
  user_story_id         bigint REFERENCES user_stories (id) ON DELETE CASCADE,
  task_id               bigint REFERENCES tasks (id) ON DELETE CASCADE,
  feature_audit_id      bigint REFERENCES feature_audits (id) ON DELETE CASCADE,
  governance_doc_id     bigint REFERENCES governance_documents (id) ON DELETE CASCADE,
  title                 text,
  body_markdown         text,
  front_matter_json     jsonb,
  content_hash          text NOT NULL,
  file_mtime            bigint,
  indexed_at            timestamptz NOT NULL DEFAULT now(),
  created_at            timestamptz NOT NULL DEFAULT now(),
  updated_at            timestamptz NOT NULL DEFAULT now(),
  search_vector         tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(title, '')), 'A')
    || setweight(to_tsvector('simple', coalesce(body_markdown, '')), 'B')
  ) STORED
);

CREATE INDEX IF NOT EXISTS idx_documents_project_kind ON documents (project_id, kind);
CREATE INDEX IF NOT EXISTS idx_documents_feature ON documents (feature_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_story ON documents (user_story_id);
CREATE INDEX IF NOT EXISTS idx_documents_task ON documents (task_id);
CREATE INDEX IF NOT EXISTS idx_documents_feature_audit ON documents (feature_audit_id);
CREATE INDEX IF NOT EXISTS idx_documents_governance ON documents (governance_doc_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents (content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_search_vector ON documents USING GIN (search_vector);

-- ---------------------------------------------------------------------------
-- document_chunks
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_chunks (
  id              bigserial PRIMARY KEY,
  document_id     bigint NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
  chunk_index     integer NOT NULL,
  text            text NOT NULL,
  token_count     integer,
  content_hash    text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks (document_id);

-- ---------------------------------------------------------------------------
-- embeddings (pgvector) — dimensão default 1536; migrar coluna se o modelo exigir
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS embeddings (
  id              bigserial PRIMARY KEY,
  chunk_id        bigint NOT NULL REFERENCES document_chunks (id) ON DELETE CASCADE,
  model           text NOT NULL,
  embedding       vector(1536) NOT NULL,
  created_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (chunk_id, model)
);

CREATE INDEX IF NOT EXISTS idx_embeddings_chunk ON embeddings (chunk_id);

-- ---------------------------------------------------------------------------
-- execution_commits — ligação Git ↔ artefactos de execução (ingestão por pipeline)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS execution_commits (
  id                        bigserial PRIMARY KEY,
  commit_sha                text NOT NULL,
  commit_short              text,
  committed_at              timestamptz,
  author_email              text,
  message_subject           text,
  project_id                bigint REFERENCES projects (id) ON DELETE SET NULL,
  feature_id                bigint REFERENCES features (id) ON DELETE SET NULL,
  user_story_id             bigint REFERENCES user_stories (id) ON DELETE SET NULL,
  task_id                   bigint REFERENCES tasks (id) ON DELETE SET NULL,
  phase                     text NOT NULL,
  source                    text,
  evidence_path_relative    text,
  recorded_at               timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_execution_commits_sha ON execution_commits (commit_sha);
CREATE INDEX IF NOT EXISTS idx_execution_commits_us ON execution_commits (user_story_id);
CREATE INDEX IF NOT EXISTS idx_execution_commits_task ON execution_commits (task_id);

COMMENT ON TABLE execution_commits IS
  'Liga commits Git a trabalho de execução/review; preenchimento via parser de evidências ou convenções de commit — ver SPEC-INDICE-PROJETOS-POSTGRES.md §4.8.';
