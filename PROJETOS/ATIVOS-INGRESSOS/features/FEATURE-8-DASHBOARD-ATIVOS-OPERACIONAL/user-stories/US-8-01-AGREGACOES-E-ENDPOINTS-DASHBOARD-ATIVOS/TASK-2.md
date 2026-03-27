---
doc_id: "TASK-2.md"
user_story_id: "US-8-01-AGREGACOES-E-ENDPOINTS-DASHBOARD-ATIVOS"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# T2 - Estrategia read-only no banco (views ou queries documentadas)

## objetivo

Decidir e implementar a **camada de persistencia read-only** para agregacoes: **views SQL** (materializadas ou nao) **ou** documentacao explicita no codigo de que as agregacoes serao **queries ad-hoc** sobre tabelas existentes — sem duplicar fonte de verdade nem alterar semantica de escrita do dominio (FEATURE-2/4/6). Se novos objetos no catalogo PostgreSQL forem necessarios (view, indice de apoio), entregar **revisao Alembic** aplicavel e reversivel.

## precondicoes

- [T1](TASK-1.md) concluida: schemas `dashboard_ativos` estabilizados o suficiente para saber quais agregados precisam de suporte SQL.
- Migracoes recentes do dominio de ativos/recebimento/distribuicao lidas para join correto.
- `DATABASE_URL` / `DIRECT_URL` disponiveis para validar SQL em desenvolvimento quando aplicavel.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.
- `write_scope`: migracoes e, se imprescindivel, reflexo minimo em `models.py` para leitura ORM de views.

## arquivos_a_ler_ou_tocar

- `backend/app/models/models.py` *(entidades Cota, recebimento, distribuicao, remanejamento, ajustes, problemas conforme F2/F4/F6)*
- `backend/alembic/env.py` e revisoes existentes em `backend/alembic/versions/`
- [FEATURE-8.md](../../FEATURE-8.md) sec. 6 (estrategia de implementacao)
- **Criar**: nova revisao em `backend/alembic/versions/` **se** views/indices forem adotados
- **Opcional**: comentarios ou modulo `backend/app/db/` apenas se o repo ja usar padrao para SQL bruto de leitura

## passos_atomicos

1. Mapear tabelas/colunas canonicas para cada dimensao (planejado, recebido, bloqueado, distribuido, remanejado, aumentado, reduzido, problemas) com base no codigo existente — citar ficheiros de modelo ou servicos de dominio na descricao da revisao ou em docstring.
2. Escolher entre: (A) `CREATE VIEW` / materialized view + `REFRESH` documentado para operacao, ou (B) queries parametrizadas no servico (T3) sem novo objeto DDL — **justificar** a escolha no corpo da task implementada (comentario na migracao ou README tecnico curto no servico).
3. Se (A): escrever migracao Alembic idempotente no padrao do repo (`upgrade`/`downgrade`); evitar dados mutaveis na migracao.
4. Se (B): registrar em comentario no codigo da T3 (referencia cruzada) que **nao** ha revisao DDL desta task e listar riscos de performance (FEATURE-8 sec. 7).
5. Validar `alembic upgrade head` em ambiente local quando houver revisao nova.

## comandos_permitidos

- `cd backend && DATABASE_URL=... DIRECT_URL=... PYTHONPATH=$(pwd)/..:$(pwd) .venv/bin/alembic upgrade head`
- `cd backend && DATABASE_URL=... DIRECT_URL=... PYTHONPATH=$(pwd)/..:$(pwd) .venv/bin/alembic downgrade -1` *(smoke de rollback em dev)*
- `cd backend && .venv/bin/ruff check` *(ficheiros tocados)*

## resultado_esperado

- Caminho de leitura no banco definido: DDL novo **ou** decisao documentada de query-only com referencia ao modelo de dados.
- Nenhuma alteracao de regras de negocio de escrita nas FEATURE-4/6.

## testes_ou_validacoes_obrigatorias

- Migracao aplica e reverte sem erro em Postgres de desenvolvimento **quando** DDL existir.
- Revisao revisada por diff: sem criacao acidental de tabelas de fatos duplicadas.

## stop_conditions

- Parar se o modelo persistido nao permitir derivar uma das oito dimensoes sem decisao de produto — reportar lacuna objetiva em vez de estimar numeros.
- Parar se for necessario ETL batch fora do padrao Alembic — escopo de infra fora desta US.
