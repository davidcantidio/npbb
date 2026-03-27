---
doc_id: "TASK-1.md"
user_story_id: "US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/"
tdd_aplicavel: false
---

# TASK-1 - Modelo e migracoes: persistencia de distribuicao e trilha minima

## objetivo

Introduzir (ou estender) o esquema persistido necessario para registrar
distribuicao efetiva em **origem externa**, com estado `distribuido` (ou campo
enum/tabela equivalente alinhada ao PRD sec. 2.3) e ligacao a evento, categoria,
destinatario e referencia ao saldo de origem externa derivado de FEATURE-4
(`disponivel` / recebido confirmado), de forma a suportar os criterios AC2 e
AC3 da US-6-01 sem estado inconsistente.

## precondicoes

- [FEATURE-4](../../../FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md)
  e modelos de recebimento / leitura de `disponivel` existentes ou planeados de
  forma a permitir FK ou join documentado *(caminhos concretos apos inspecao
  do codigo; se ausentes, parar em `stop_conditions`)*.
- Leitura integral do
  [README.md](./README.md)
  desta US e trechos do
  [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md)
  sobre `disponivel`, `distribuido` e restricoes de origem externa.

## orquestracao

- `depends_on`: `[]`.
- `parallel_safe`: `false`.
- `write_scope`: migrations sob `backend/alembic/versions/` e modelos SQLModel
  em `backend/app/models/` *(ficheiro novo ou extensao de modulo existente,
  nomeado na execucao)*.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) (US-6-01)
- [FEATURE-6.md](../../FEATURE-6.md) sec. 6–7
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) sec. 2.3–2.4
- Entidades FEATURE-4 / FEATURE-5 relevantes *(grep em `backend/app/models/` e
  servicos de recebimento)*
- `backend/alembic/env.py` *(convencao de revision)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Mapear no codigo onde `disponivel` para origem externa e calculado ou
   persistido; definir FKs ou chaves naturais entre registo de distribuicao e
   esse agregado.
2. Desenhar tabela(s) ou extensao de modelo: quantidade distribuida, estado,
   destinatario (email ou ID conforme contrato existente), `evento_id`,
   referencia a categoria/modo externo se aplicavel, campos de trilha (ator,
   `created_at` / instante de confirmacao).
3. Criar revisao Alembic com upgrade/downgrade idempotente e constraints que
   evitem quantidades negativas ou nulas invalidas.
4. Registar modelos SQLModel e relacoes; exportar em `app.models` se for padrao
   do repositorio.
5. Documentar no corpo da migration ou comentario curto no modelo o alinhamento
   ao PRD (sem alterar manifesto da feature nesta task).

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend alembic revision --autogenerate -m "<slug>"` *(se autogenerate for politica do projeto; senao revisao manual)*
- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend alembic upgrade head`
- `cd backend && ruff check app/models/`

## resultado_esperado

Esquema aplicavel e modelos Python que permitem persistir uma distribuicao com
estado `distribuido` e metadados de trilha, prontos para validacao de saldo na
TASK-2.

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` em base local de desenvolvimento sem erro.
- Smoke: instanciar modelo em teste ou REPL com FKs respeitadas *(opcional se
  TASK-4 cobrir integracao completa)*.

## stop_conditions

- Parar se nao existir ancoragem canonica para `disponivel` de origem externa
  no modelo FEATURE-4 — alinhar com owner de FEATURE-4 ou ADR antes de inventar
  chaves.
- Parar se o PRD exigir nomenclatura de estado distinta da escolhida em
  FEATURE-2/3; pedir decisao documental antes de migrar.
