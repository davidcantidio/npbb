-- OpenClaw: índice SQLite derivado de PROJETOS/**/*.md (fonte de verdade = Git + Markdown).
-- Aplicar com: sqlite3 DB < schema.sql ou via sync (executescript).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sync_meta (
  key TEXT PRIMARY KEY NOT NULL,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE,
  name_display TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS features (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  feature_key TEXT NOT NULL,
  feature_number INTEGER,
  name_display TEXT,
  status TEXT,
  audit_gate TEXT,
  path_relative TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (project_id, feature_key)
);

CREATE TABLE IF NOT EXISTS user_stories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  feature_id INTEGER NOT NULL REFERENCES features (id) ON DELETE CASCADE,
  user_story_key TEXT NOT NULL,
  layout TEXT NOT NULL DEFAULT 'folder',
  status TEXT,
  task_instruction_mode TEXT,
  decision_refs_json TEXT,
  path_relative TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (project_id, user_story_key)
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_story_id INTEGER NOT NULL REFERENCES user_stories (id) ON DELETE CASCADE,
  task_number INTEGER NOT NULL,
  task_id TEXT,
  status TEXT,
  tdd_aplicavel INTEGER NOT NULL DEFAULT 0,
  path_relative TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (user_story_id, task_number)
);

CREATE TABLE IF NOT EXISTS feature_audits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_id INTEGER NOT NULL REFERENCES features (id) ON DELETE CASCADE,
  report_key TEXT NOT NULL,
  status TEXT,
  verdict TEXT,
  scope_type TEXT,
  scope_ref TEXT,
  feature_code TEXT,
  base_commit TEXT,
  compares_to TEXT,
  round_number INTEGER,
  supersedes TEXT,
  followup_destination TEXT,
  decision_refs_json TEXT,
  path_relative TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (feature_id, report_key)
);

CREATE TABLE IF NOT EXISTS governance_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  doc_id TEXT,
  filename TEXT NOT NULL,
  path_relative TEXT NOT NULL UNIQUE,
  version TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS project_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects (id) ON DELETE CASCADE,
  doc_type TEXT NOT NULL,
  status TEXT,
  intake_kind TEXT,
  source_mode TEXT,
  intake_slug TEXT,
  path_relative TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path_relative TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL,
  project_id INTEGER REFERENCES projects (id) ON DELETE CASCADE,
  feature_id INTEGER REFERENCES features (id) ON DELETE CASCADE,
  user_story_id INTEGER REFERENCES user_stories (id) ON DELETE CASCADE,
  task_id INTEGER REFERENCES tasks (id) ON DELETE CASCADE,
  feature_audit_id INTEGER REFERENCES feature_audits (id) ON DELETE CASCADE,
  governance_doc_id INTEGER REFERENCES governance_documents (id) ON DELETE CASCADE,
  title TEXT,
  body_markdown TEXT,
  front_matter_json TEXT,
  content_hash TEXT NOT NULL,
  file_mtime INTEGER,
  indexed_at TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_documents_project_kind ON documents (project_id, kind);
CREATE INDEX IF NOT EXISTS idx_documents_feature ON documents (feature_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_story ON documents (user_story_id);
CREATE INDEX IF NOT EXISTS idx_documents_task ON documents (task_id);
CREATE INDEX IF NOT EXISTS idx_documents_feature_audit ON documents (feature_audit_id);
CREATE INDEX IF NOT EXISTS idx_documents_governance ON documents (governance_doc_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_hash ON documents (content_hash);

CREATE INDEX IF NOT EXISTS idx_features_project ON features (project_id);
CREATE INDEX IF NOT EXISTS idx_features_status ON features (status);
CREATE INDEX IF NOT EXISTS idx_features_audit_gate ON features (audit_gate);

CREATE INDEX IF NOT EXISTS idx_user_stories_project ON user_stories (project_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_feature ON user_stories (feature_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_status ON user_stories (status);

CREATE INDEX IF NOT EXISTS idx_tasks_user_story ON tasks (user_story_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);

CREATE INDEX IF NOT EXISTS idx_feature_audits_feature ON feature_audits (feature_id);
CREATE INDEX IF NOT EXISTS idx_feature_audits_status ON feature_audits (status);
CREATE INDEX IF NOT EXISTS idx_feature_audits_verdict ON feature_audits (verdict);

-- FTS5: conteúdo externo em `documents`; após bulk load usar INSERT INTO documents_fts(documents_fts) VALUES('rebuild').
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5 (
  title,
  body_markdown,
  content='documents',
  content_rowid='id',
  tokenize='porter'
);

CREATE TABLE IF NOT EXISTS document_chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  text TEXT NOT NULL,
  token_count INTEGER,
  content_hash TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  chunk_id INTEGER NOT NULL REFERENCES document_chunks (id) ON DELETE CASCADE,
  model TEXT NOT NULL,
  embedding BLOB NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (chunk_id, model)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk ON embeddings (chunk_id);

PRAGMA user_version = 4;
