---
doc_id: "TASK-2.md"
user_story_id: "US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# T2 - Migration: referencias externas (ticketeira) sem binarios

## objetivo

Adicionar revisao Alembic com tabela(s) para **IDs e metadados** fornecidos por ticketeiras ou sistemas externos, em formato texto/JSON, **sem** colunas de binarios nem anexos obrigatorios, alinhado ao terceiro criterio Given/When/Then da US e aos placeholders LGPD citados no README da US (referencia + metadados ate fecho PRD sec. 7).

## precondicoes

- TASK **T1** concluida: existe revisao com tabela de idempotencia e head Alembic atualizado.
- Nomes finais da tabela e PK de idempotencia da T1 conhecidos para eventual `ForeignKey` opcional.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: false.
- `write_scope`: apenas novos ficheiros em `backend/alembic/versions/` nesta task.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/TASK-1.md`
- Ficheiro de revisao Alembic criado na T1
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 7 — contexto LGPD; sem alargar escopo)*

## passos_atomicos

1. Definir `down_revision` como o head deixado pela T1.
2. Criar tabela (nome em `snake_case`, ex.: `external_supply_reference`) com: `id` PK; `provider_code` ou `external_system` `VARCHAR` (identificacao da fonte); `entity_kind` `VARCHAR` (tipo logico: ex. lote, comprovativo, referencia comercial); `external_id` `VARCHAR` (id na origem); `metadata_json` `TEXT` nullable (JSON serializado — sem BLOB).
3. Opcional: `external_ingest_idempotency_id` nullable FK para a tabela da T1, quando uma referencia externa nascer de uma tentativa de ingestao concreta.
4. Opcional: `UniqueConstraint` em (`provider_code`, `entity_kind`, `external_id`) se o desenho exigir deduplicacao de referencias estaveis (documentar escolha no corpo da migration).
5. Indices simples sobre `provider_code` e/ou `external_id` se consultas por US-7-03 forem antecipadas.
6. `upgrade()` / `downgrade()` simetricos.
7. `alembic upgrade head` e `alembic downgrade -1` em desenvolvimento.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Schema persistente para chaves externas e metadados nao-binarios, pronto para ligacao na camada de aplicacao (US-7-03) e documentacao OpenAPI (US-7-04).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` e `downgrade -1` sem erro.
- Confirmar ausencia de tipo BLOB/bytea para payload de artefato; apenas `TEXT`/JSON em string.

## stop_conditions

- Parar se a T1 ainda nao estiver mergeada no branch (head incorreto).
- Parar se stakeholders exigirem storage de ficheiro nesta US — fora de escopo; retornar a revisao de PRD/US.
