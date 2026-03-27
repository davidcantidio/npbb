---
doc_id: "TASK-1.md"
user_story_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# T1 - Migration e modelo: ocorrencia operacional (problema_registrado)

## objetivo

Persistir **ocorrencias operacionais** ligadas a `evento`, com campos minimos alinhados ao PRD (`problema_registrado`): tipo, descricao, referencia ao evento, instante de registro; opcionalmente `correlation_id` ou cabecalho rastreavel para observabilidade. Incluir indices que suportem listagem por evento.

## precondicoes

- `cd backend && alembic heads` executado; head unico (revalidar `down_revision` no branch).
- Tabela `evento` existente com PK alinhada a `backend/app/models/models.py` (`evento.id`).
- Se US-6-01 ainda nao estiver `done`: esta task pode avancar **tecnicamente** (FK apenas a `evento`), mas a US permanece inelegivel para fecho ate dependencia de governanca resolvida (ver README da US).

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false (fila Alembic + mesmo modulo de modelos).
- `write_scope`: nova revisao Alembic + classe SQLModel na localizacao canonica de dominio em `models.py` (ou modulo dedicado se o repo ja separar entidades de ingressos/ativos — seguir convencao existente).

## arquivos_a_ler_ou_tocar

- [README.md](README.md) desta US (criterios Given/When/Then)
- [FEATURE-6.md](../../FEATURE-6.md) (sec. 2, 4, 7)
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) (estado `problema_registrado`)
- `backend/app/models/models.py` — padrao de `Evento`, tipos, relacionamentos
- `backend/alembic/env.py` *(apenas se convencao exigir; evitar mudancas desnecessarias)*

## passos_atomicos

1. Confirmar `alembic heads` e definir `down_revision` para o head atual.
2. Escolher nome de tabela em `snake_case` (ex.: `problema_operacional` ou `ocorrencia_operacional`) e documentar no corpo da migration.
3. Colunas minimas: `id` (PK), `evento_id` (FK `evento.id`, `ondelete` alinhado a politica do repo — RESTRICT ou CASCADE conforme decisao consistente com outras entidades por evento), `tipo` (string ou enum persistido conforme padrao do projeto), `descricao` (texto), `registrado_em` (timezone-aware), coluna ou convencao que materialize o estado **`problema_registrado`** (valor fixo, enum operacional, ou coluna `status` com valor canonico — documentar escolha na revisao).
4. Opcional: `correlation_id` (string indexavel), `created_by_usuario_id` (FK) se RBAC/auditoria exigir na mesma entrega; nao alargar a US sem criterio testavel.
5. Indice composto ou simples em `evento_id` (+ ordenacao por `registrado_em` desc se util para listagens).
6. Adicionar classe SQLModel em `models.py` (ou modulo acordado) espelhando a migration; relacionamento opcional `Evento` <-> ocorrencias.
7. Implementar `upgrade()` / `downgrade()` simetricos na revisao Alembic.
8. Rodar `alembic upgrade head` e `alembic downgrade -1` em ambiente de desenvolvimento com `DATABASE_URL` valido.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Schema e modelo alinhados ao primeiro criterio de aceitacao da US (persistencia listavel com referencia ao evento e estado `problema_registrado` ou equivalente documentado).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` sem erro apos criar a revisao.
- `alembic downgrade -1` sem erro e sem objetos orphan.
- Verificacao manual ou query de existencia do indice por `evento_id`.

## stop_conditions

- Parar se `alembic heads` reportar multiplos heads nao resolvidos.
- Parar se for necessario criar tabelas de FEATURE-6 distintas (distribuicao) para satisfazer FK — fora do escopo desta US; escalar PM.
