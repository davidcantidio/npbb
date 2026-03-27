---
doc_id: "TASK-2.md"
user_story_id: "US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# T2 - Migration: tabela de emissao interna unitaria com FKs e unicidade

## objetivo

Introduzir revisao Alembic que cria a entidade persistida de **emissao interna unitaria** (nome fisico alinhado ao ADR e ao dominio, ex. `emissao_interna_unitaria`), com FKs obrigatorias para `evento`, `diretoria`, a entidade de **categoria por evento** definida no ADR (FEATURE-3) e o **destinatario** definido no ADR, mais colunas de auditoria minima (`created_at` / `updated_at`) e campos opcionais para **referencia externa** a artefato (texto/URL) **sem** exigir blob, conforme contexto da US e PRD sec. 7.

## precondicoes

- T1 concluida: [ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md](./ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md) existente e com escopo de `UNIQUE`, `public_id` e nomes de FK fechados.
- `cd backend && .venv/bin/alembic heads` reporta **um unico head**; anotar o revision id atual (referencia ao executar: `17e2fd99b4fe` — revalidar no branch).
- Existe ficheiro de migration da **US-3-01** (FEATURE-3) no branch com as tabelas/PKs referenciadas no ADR; **copiar strings exatas** de `foreign_key` a partir desse ficheiro.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: false (fila de revisoes Alembic).
- `write_scope`: apenas **um** novo ficheiro sob `backend/alembic/versions/` nesta task.

## arquivos_a_ler_ou_tocar

- [ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md](./ADR-US-5-01-DOMINIO-EMISSAO-UNITARIA.md)
- [README.md](./README.md) desta US
- Revisao Alembic da US-3-01 em `backend/alembic/versions/`
- `backend/alembic/env.py` *(apenas se convencao do repo exigir; evitar mudancas desnecessarias)*
- `backend/app/models/models.py` e `backend/app/models/event_support_models.py` *(contexto de nomes de tabela `evento`, `diretoria`, `convidado`; sem alterar modelos nesta task)*

## passos_atomicos

1. Confirmar `alembic heads` e definir `down_revision` para o head atual.
2. Criar tabela com colunas: PK surrogate; `public_id` UUID **NOT NULL** **UNIQUE** (default gerado no servidor preferivel — `gen_random_uuid()` em Postgres; se o repo padronizar outro mecanismo, alinhar as migrations existentes); FKs conforme ADR; timestamps.
3. Implementar a **constraint de unicidade de negocio** exatamente como no ADR (nome de constraint/index explicito no `upgrade()`).
4. Adicionar **indices** que suportem consultas por `evento_id` e pela FK de categoria (prefixo `evento_id` quando fizer sentido).
5. Incluir comentario curto na migration (docstring ou `op.execute` COMMENT se usado no repo) sobre placeholder de storage LGPD — sem politica de retencao nesta US.
6. Implementar `upgrade()` e `downgrade()` **simetricos**: `downgrade()` remove apenas objetos criados nesta revisao.
7. Executar `alembic upgrade head` e `alembic downgrade -1` em ambiente de desenvolvimento com `DATABASE_URL` valido.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Nova revisao Alembic aplicavel e reversivel que materializa o primeiro criterio Given/When/Then da US (entidade coerente + FKs) e o segundo/terceiro na forma escolhida no ADR (unicidade + identidade imutavel).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` sem erro apos criar a revisao.
- `alembic downgrade -1` sem erro e sem deixar lixo de schema.
- Verificacao manual (ou query) de existencia do indice/constraint de unicidade de negocio e do UNIQUE em `public_id`.

## stop_conditions

- Parar se nao existir migration mergeada da US-3-01 com PK utilizavel — nao inventar nome de tabela.
- Parar se `alembic heads` reportar multiplos heads nao resolvidos.
- Parar se for necessario alterar tabelas legadas fora do escopo desta US para satisfazer FKs — escalar a revisao de escopo antes de prosseguir.
