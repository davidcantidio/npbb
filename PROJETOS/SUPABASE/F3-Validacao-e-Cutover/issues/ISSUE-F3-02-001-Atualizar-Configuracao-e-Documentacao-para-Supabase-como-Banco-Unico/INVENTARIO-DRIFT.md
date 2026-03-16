---
doc_id: "INVENTARIO-DRIFT.md"
issue_id: "ISSUE-F3-02-001"
task_id: "T1"
version: "1.0"
status: "active"
last_updated: "2026-03-16"
---

# Inventario de Drift Documental e de Configuracao

Inventario fechado das inconsistencias que ainda tratam PostgreSQL local como
caminho principal, produzido pela T1 da ISSUE-F3-02-001.

## Criterio de drift

- **Drift:** trecho que coloca PostgreSQL local como requisito padrao ou primeiro caminho
- **Preservar:** excecoes legitimas (SQLite para testes, scripts F2 de migracao, observacoes de dev local para frontend/API)

---

## 1. backend/.env.example

### Drift

| Linhas | Trecho | Problema |
|--------|--------|----------|
| 5-7 | Exemplo local (Postgres Homebrew) com `127.0.0.1:5432/npbb` | Aparece antes do exemplo Supabase; sugere que o local e o caminho principal |
| 9 | "Exemplo Supabase (substitua pelos seus valores)" | Ordem e rotulagem colocam Supabase como alternativa, nao como padrao |

### Preservar

- Comentarios de F2 (backup, recarga, validacao pos-carga) — linhas 13-21
- `LOCAL_DIRECT_URL` — necessario para export durante migracao F2
- `FRONTEND_ORIGIN=http://localhost:5173` — dev local legitimo
- `CORS_ALLOW_ORIGIN_REGEX` com localhost — dev legitimo

### Acao sugerida (T2)

- Inverter ordem: Supabase como exemplo principal; PostgreSQL local como alternativa opcional para dev local
- Deixar claro que o estado final do projeto e Supabase como banco unico

---

## 2. docs/SETUP.md

### Drift

| Linhas | Trecho | Problema |
|--------|--------|----------|
| 13-15 (TL;DR) | `brew install postgresql@16`, `createdb npbb` | TL;DR exige Postgres local antes do backend; caminho feliz nao menciona Supabase |
| 35 | Pre-requisitos: "Postgres local (Homebrew postgresql@16)" | PostgreSQL local como pre-requisito obrigatorio |
| 39-43 | Secao "0) Preparar Postgres local" | Passo obrigatorio antes de qualquer configuracao; nao ha caminho Supabase-first |
| 66-67 | Exemplo `.env`: `127.0.0.1:5432/npbb` | Unico exemplo de conexao; nao ha exemplo Supabase |

### Preservar

- `localhost:5173` e `localhost:8000` — dev local do frontend/API (nao banco)
- Secoes 6 e 7 (Migracao F2) — scripts de backup/export/validacao; `LOCAL_DIRECT_URL` e `pg_dump`/`pg_restore` necessarios para migracao
- Linha 78: fallback SQLite em testes com `TESTING=true`
- Linhas 87-98: `PUBLIC_APP_BASE_URL` e risco de localhost em producao — manter

### Acao sugerida (T2)

- TL;DR: oferecer caminho Supabase-first (configurar `.env` com Supabase, sem `createdb`)
- Pre-requisitos: remover Postgres local como obrigatorio; indicar como opcional para dev local
- Secao 0: tornar opcional ou mover para "Alternativa: PostgreSQL local"
- Exemplo `.env`: adicionar exemplo Supabase como principal; manter exemplo local como alternativa

---

## 3. docs/TROUBLESHOOTING.md

### Drift

| Linhas | Trecho | Problema |
|--------|--------|----------|
| 88-90 | Item 14: "configure `DATABASE_URL` para um banco de teste" | Nao prioriza `TESTING=true` (SQLite); poderia induzir configurar Postgres de teste |

### Preservar (ja alinhado)

- Itens 1, 13, 15, 16, 17, 18 — Supabase como contexto principal
- Item 15: "confirmar que o backend usa o Supabase (nao PostgreSQL local)"
- Item 18: fallback SQLite e scripts criticos sem PostgreSQL local como padrao
- `localhost:8000` e `127.0.0.1:8000` — endereco da API em dev (nao banco)
- Item 105: `brew install postgresql@16` — necessario para `pg_dump`/`pg_restore` em scripts F2; manter

### Acao sugerida (T3)

- Item 14: priorizar "exporte `TESTING=true`" e mencionar SQLite; "configure DATABASE_URL para banco de teste" como alternativa secundaria

---

## 4. docs/DEPLOY_RENDER_CLOUDFLARE.md

### Drift

Nenhum. Documento ja trata Supabase como banco de producao e estado operacional F3 validado.

### Preservar

- Linhas 99-100: regra de bloqueio para `localhost`/`127.0.0.1` em producao — manter

---

## 5. docs/render.yaml

### Drift

Nenhum. `DATABASE_URL` e `DIRECT_URL` com `sync: false` — valores vem do Supabase no Render.

---

## Resumo por arquivo

| Arquivo | Drift | Preservar | Prioridade |
|---------|-------|-----------|------------|
| backend/.env.example | Ordem exemplos (local primeiro) | F2, SQLite, dev local | Alta |
| docs/SETUP.md | TL;DR, pre-req, secao 0, exemplo .env | F2, SQLite, localhost dev | Alta |
| docs/TROUBLESHOOTING.md | Item 14 (Tests) | Itens 1-18 restantes | Baixa |
| docs/DEPLOY_RENDER_CLOUDFLARE.md | — | — | Nenhuma |
| docs/render.yaml | — | — | Nenhuma |

---

## Cobertura do inventario

- [x] setup (docs/SETUP.md)
- [x] troubleshooting (docs/TROUBLESHOOTING.md)
- [x] deploy (docs/DEPLOY_RENDER_CLOUDFLARE.md, docs/render.yaml)
- [x] exemplo de env (backend/.env.example)

---

## Stop conditions verificadas

- Nenhuma dependencia operacional nova nao validada em F3 foi identificada.
- Scripts F2 (backup, export, recarga, validacao) permanecem documentados; `pg_dump`/`pg_restore` e `LOCAL_DIRECT_URL` sao necessarios para migracao e rollback.
