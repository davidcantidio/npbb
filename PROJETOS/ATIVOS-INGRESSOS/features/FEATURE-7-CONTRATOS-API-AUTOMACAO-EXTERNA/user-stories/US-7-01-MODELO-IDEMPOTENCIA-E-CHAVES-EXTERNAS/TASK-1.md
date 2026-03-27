---
doc_id: "TASK-1.md"
user_story_id: "US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# T1 - Migration: registos de idempotencia para ingestao externa (API ticketeira)

## objetivo

Criar revisao Alembic com tabela persistida para **chaves de idempotencia** por integrador (escopo opaco ate US-7-02 materializar identidade), permitindo trilha minimamente auditavel de tentativas (estado, instantes, resumo de desfecho) e **sem** implementar logica HTTP (US-7-03). O desenho deve **coexistir** com o modelo de recebimento FEATURE-4: usar coluna de correlacao **nullable sem FK** para futura ligacao a linhas de recebimento quando US-4-01 estiver mergeada, em vez de assumir nomes de tabela ainda ausentes no branch.

## precondicoes

- `cd backend && .venv/bin/alembic heads` reporta um unico head; usar esse revision id como `down_revision` (referencia ao planear: `17e2fd99b4fe` — revalidar no branch).
- Leitura do manifesto FEATURE-4 e US-4-01 para alinhar semantica de correlacao (recebimento / conciliacao), sem copiar FKs inexistentes no schema atual.

## orquestracao

- `depends_on`: nenhuma.
- `parallel_safe`: false (fila Alembic).
- `write_scope`: apenas novos ficheiros em `backend/alembic/versions/` nesta task.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/FEATURE-7.md` (sec. 6–7)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md` (sec. 6–7)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md` *(correlacao futura)*
- `backend/alembic/versions/e4c7b8a9d0f1_create_sources_and_ingestions_tables.py` ou revisao que define `ingestions` *(FK opcional)*
- `backend/alembic/env.py` *(sem alteracao nesta task, salvo convencao do repo)*

## passos_atomicos

1. Confirmar head atual e nomear a nova revisao (ex.: prefixo descritivo alinhado ao dominio `external_ingest` / `ticketeira_api`).
2. Definir tabela com colunas minimas sugeridas (ajustar tipos ao padrao do repo): `id` PK; `integrator_client_ref` `VARCHAR` nao nulo (escopo de deduplicacao ate entidade de integrador); `idempotency_key` `VARCHAR` nao nulo; `status` com dominio restrito (`pending`, `succeeded`, `failed` ou equivalente em maiusculas se o repo padronizar assim); `outcome_summary` `TEXT` nullable; `correlation_id` UUID ou `VARCHAR` nullable; `created_at` / `updated_at` com timezone.
3. `UniqueConstraint` composto em (`integrator_client_ref`, `idempotency_key`) para garantir uma linha canonica por reenvio da mesma chave no mesmo integrador.
4. Incluir `ingestion_id` nullable com `ForeignKey` para `ingestions.id` **somente se** a tabela existir no mesmo branch (ponte opcional com registry ETL); caso contrario omitir e deixar para extensao documentada na TASK-4.
5. Incluir `feature4_receipt_record_id` (nome alinhado ao que US-4-01 vier a expor) como **INTEGER NULL sem FK**, com comentario SQL ou docstring na migration: "Reservado para FK quando migrations de US-4-01 estiverem mergeadas".
6. Implementar `upgrade()` e `downgrade()` simetricos (apenas objetos criados nesta revisao).
7. Correr `alembic upgrade head` e `alembic downgrade -1` em ambiente com `DATABASE_URL` valido.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Revisao Alembic aplicavel e reversivel que satisfaz o primeiro e segundo criterios Given/When/Then da US (estruturas apos migrate; suporte a reenvio com unicidade e trilha minima; sem quebrar FEATURE-4 por FK prematura).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` sem erro.
- `alembic downgrade -1` sem erro.
- Verificar existencia do indice/constraint unico (`integrator_client_ref`, `idempotency_key`).

## stop_conditions

- Parar se `alembic heads` tiver multiplos heads nao resolvidos.
- Parar se for necessario fixar nome definitivo da PK de recebimento FEATURE-4 antes de existir migration no branch — manter coluna reservada sem FK e escalar em ADR se o produto exigir vinculo obrigatorio ja nesta entrega.
