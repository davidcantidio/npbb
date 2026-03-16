# Runbook — Migração PostgreSQL Local → Supabase

> **Origem:** [PRD-SUPABASE.md](../PROJETOS/SUPABASE/PRD-SUPABASE.md), [INTAKE-SUPABASE.md](../PROJETOS/SUPABASE/INTAKE-SUPABASE.md)

Este runbook define a sequência operacional para migrar dados do PostgreSQL local para o Supabase, conforme a fase F2 do projeto SUPABASE.

---

## 1. Precondições e Restrições

### 1.1 Ordem obrigatória (PRD)

1. **Schema primeiro**: `alembic upgrade head` no Supabase com `DIRECT_URL` — schema validado em F1
2. **Backup do Supabase** — antes de qualquer ação destrutiva
3. **Export do PostgreSQL local** — `pg_dump` ou equivalente
4. **Recarga** — limpeza controlada e import no Supabase
5. **Validação** — backend conectando ao Supabase; testes passando
6. **Rollback** — caminho de retorno ao backup do Supabase até validação completa da F3

### 1.2 Contrato de conexão (backend/.env.example, docs/SETUP.md)

| Variável     | Uso                          | Supabase (porta) | Local (porta) |
|--------------|------------------------------|------------------|---------------|
| `DATABASE_URL` | API / runtime                | pooler :6543     | 5432          |
| `DIRECT_URL`   | migrations, seed, dump/restore | direct :5432   | 5432          |

- **Migrations e seed**: usar `DIRECT_URL` (porta 5432) — pooler pode causar timeouts (docs/TROUBLESHOOTING.md §13)
- **Operações sensíveis** (backup, export, import): `DIRECT_URL` obrigatória (backend/scripts/seed_common.py)

### 1.3 Ferramentas e acesso

- `pg_dump` disponível no PATH
- `psql` ou `pg_restore` disponíveis para import
- Credenciais válidas para Supabase (`DATABASE_URL`, `DIRECT_URL`)
- Acesso ao PostgreSQL local para export
- F1 concluída — schema do Supabase validado via `alembic upgrade head`

### 1.4 Riscos operacionais conhecidos (docs/TROUBLESHOOTING.md)

- Timeouts em migrations: usar `DIRECT_URL` (5432), não pooler
- `DATABASE_URL` não configurada: criar `.env` a partir de `.env.example`

### 1.5 Critérios de parada (antes de qualquer passo destrutivo)

- **Parar** se backup do Supabase não existir antes de limpeza/import
- **Parar** se `pg_dump` não estiver disponível
- **Parar** se credenciais Supabase ou local forem inválidas
- **Parar** se F1 não estiver concluída (schema não validado no Supabase)

---

## 2. Sequência canônica (em elaboração)

_(Seção a ser preenchida na T2)_

---

## 3. Rollback

_(Detalhes a serem consolidados na T2/T3)_

- Backup do Supabase preservado até o fim da validação da F3
- Restore via Supabase Dashboard ou `pg_restore`
