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

- `pg_dump` disponível no PATH (backup e export)
- `pg_restore` disponível no PATH (validação dos dumps custom e import)
- `psql` ou `pg_restore` disponíveis para import
- Credenciais válidas para Supabase (`DATABASE_URL`, `DIRECT_URL`)
- Acesso ao PostgreSQL local para export
- F1 concluída — schema do Supabase validado via `alembic upgrade head`

### 1.4 Riscos operacionais conhecidos (docs/TROUBLESHOOTING.md)

- Timeouts em migrations: usar `DIRECT_URL` (5432), não pooler
- `DATABASE_URL` não configurada: criar `.env` a partir de `.env.example`

### 1.5 Critérios de parada (antes de qualquer passo destrutivo)

- **Parar** se backup do Supabase não existir antes de limpeza/import
- **Parar** se `pg_dump` ou `pg_restore` não estiverem disponíveis
- **Parar** se credenciais Supabase ou local forem inválidas
- **Parar** se F1 não estiver concluída (schema não validado no Supabase)

---

## 2. Sequência canônica

A rodada de migração segue esta ordem. **Nenhum passo destrutivo** (limpeza/truncate) pode ocorrer antes do backup do Supabase e do export local estarem concluídos.

| # | Passo | Comando-base | URL usada | Critério de parada antes |
|---|-------|--------------|-----------|--------------------------|
| 1 | Backup do Supabase | `pg_dump` com `DIRECT_URL` do Supabase | `DIRECT_URL` | — |
| 2 | Export PostgreSQL local | `pg_dump --data-only` (ou `--format=custom`) | conexão local | Backup do Supabase existe? |
| 3 | Limpeza controlada do alvo | truncate em ordem reversa de FKs | `DIRECT_URL` | Backup e export existem? |
| 4 | Import no Supabase | `psql` ou `pg_restore` | `DIRECT_URL` | Limpeza concluída sem erro? |
| 5 | Validação pós-carga | backend + testes | `DATABASE_URL` (runtime) | Import concluído? |
| 6 | Rollback (se falha) | Supabase Dashboard ou `pg_restore` | — | Backup preservado até F3 |

### 2.1 Comandos-base da rodada

- **Backup Supabase**: `pg_dump` com `DIRECT_URL` (porta 5432) — pooler não deve ser usado para dump
- **Export local**: `pg_dump --data-only` ou `pg_dump --format=custom` após schema aplicado
- **Import**: `psql` (para SQL plain) ou `pg_restore` (para formato custom)
- **Ordem de limpeza**: truncate em ordem reversa de dependência de FKs antes do reload (detalhes na fase F2)

### 2.2 Automação (passos 1 e 2)

O script `backend/scripts/backup_export_migracao.py` automatiza os passos 1 e 2 (backup Supabase + export local):

```bash
cd backend && python -m scripts.backup_export_migracao
```

**Pré-requisitos:** configure no `.env`:
- `SUPABASE_DIRECT_URL` ou `DIRECT_URL` — conexão direct ao Supabase (backup)
- `LOCAL_DIRECT_URL` — conexão ao PostgreSQL local (export)

**Tooling obrigatório:** `pg_dump` e `pg_restore` no PATH (o segundo é usado para validar os dumps antes de declarar sucesso).

**Validação final:** o script só imprime a mensagem de prontidao para F2-02 após validar objetivamente os dumps gerados (existência, tamanho > 0, `pg_restore --list` sem erro). Se a validação falhar, o fluxo termina com erro e não declara os artefatos prontos.

Artefatos gerados em `artifacts_migracao/` (backup_supabase_*.dump, export_local_*.dump).

### 2.2.1 Automação (passos 3 e 4 — recarga)

O script `backend/scripts/recarga_migracao.py` automatiza os passos 3 e 4 (limpeza + import):

```bash
cd backend && python -m scripts.recarga_migracao
```

**Pré-requisitos:** execute primeiro `backup_export_migracao.py`; configure no `.env`:
- `SUPABASE_DIRECT_URL` ou `DIRECT_URL` — conexão direct ao Supabase

O script valida precondições, executa limpeza controlada (TRUNCATE CASCADE), importa via `pg_restore` e consolida o estado para a validação pós-carga.

### 2.3 Uso de DIRECT_URL vs DATABASE_URL

| Operação | URL | Motivo |
|----------|-----|--------|
| Backup do Supabase | `DIRECT_URL` | Dump exige conexão direta; pooler pode causar timeouts |
| Export local | conexão local | PostgreSQL local |
| Limpeza/truncate no Supabase | `DIRECT_URL` | Operações DDL/DML sensíveis |
| Import no Supabase | `DIRECT_URL` | Restore exige conexão direta |
| Runtime da API | `DATABASE_URL` | Pooler pode ser usado em produção |

### 2.4 Critérios de parada (antes de passo destrutivo)

- **Antes de limpeza**: confirmar que backup do Supabase existe e export local está disponível
- **Antes de import**: confirmar que limpeza foi concluída sem erro
- **Parar imediatamente** se `pg_dump`, `pg_restore` ou credenciais forem inválidos ou ausentes

---

## 3. Rollback

- **Backup do Supabase** preservado até o fim da validação da F3
- **Restore**: via Supabase Dashboard ou `pg_restore` em caso de falha
- **Dump local**: manter como cópia de segurança até validação completa (PRD)

---

## 4. Referências

- [PRD-SUPABASE.md](../PROJETOS/SUPABASE/PRD-SUPABASE.md) — fluxo principal e escopo
- [docs/SETUP.md](SETUP.md) — contrato de conexão
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md) — riscos operacionais (Supabase pooler vs direct)
- [docs/DEPLOY_RENDER_CLOUDFLARE.md](DEPLOY_RENDER_CLOUDFLARE.md) — variáveis de produção (Render + Supabase)
