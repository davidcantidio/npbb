---
doc_id: "TASK-1.md"
user_story_id: "US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO"
task_id: "T1"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# T1 - Migration: recebimento e divergencia (conciliacao) com indices

## objetivo

Introduzir revisao Alembic que cria a base persistida para **registros de recebimento** e para **divergencia / conciliacao** (planejado vs recebido), com vinculo obrigatorio a `evento` e `diretoria` e vinculo as entidades de **categoria por evento** e **modo canonico de fornecimento** entregues por FEATURE-3 (US-3-01), mais **indices** que suportem consultas por evento e por categoria conforme manifesto FEATURE-4 sec. 6–7.

## precondicoes

- `cd backend && alembic heads` executado; existe um unico head (referencia ao executar: `17e2fd99b4fe` — revalidar no branch).
- Migrations da **US-3-01** (catalogo / configuracao de categorias e modos) estao **mergeadas neste branch** com nomes finais de tabelas e PKs; o executor copiou os nomes exatos das FKs a partir do ficheiro de revisao correspondente em `backend/alembic/versions/`.
- Se US-3-01 ainda nao existir no branch: **parar** (nao inventar nomes de tabela de FEATURE-3).

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: false (fila de revisoes Alembic).
- `write_scope`: apenas novos ficheiros sob `backend/alembic/versions/` nesta task.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md` (sec. 6–7)
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/user-stories/US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md`
- Revisao Alembic da US-3-01 (FEATURE-3) para FKs de categoria/modo
- `backend/alembic/env.py` *(apenas se convencao do repo exigir ajuste; evitar mudancas desnecessarias)*
- `backend/app/models/models.py` e `backend/app/models/event_support_models.py` *(contexto: `evento`, `diretoria`, `cota_cortesia` — sem alterar modelos nesta task)*

## passos_atomicos

1. Confirmar `alembic heads` e definir `down_revision` para o head atual.
2. Esboçar duas tabelas minimas (nomes em `snake_case` alinhados ao dominio): (a) cabecalho ou linha de **recebimento** por evento+diretoria+categoria+modo; (b) registro de **divergencia** ou snapshot de conciliacao referenciando a linha de recebimento ou entidade operacional acordada no PRD — sem implementar regras de negocio de US-4-02+.
3. Declarar FKs para `evento.id`, `diretoria.id` e para as PKs expostas pela migration de FEATURE-3 (categoria por evento / modo).
4. Criar indices compostos ou simples que cubram consultas por **evento** e por **categoria** (ex.: indice com prefixo `evento_id` + coluna de categoria ou FK de categoria, conforme modelo mergeado).
5. Implementar `upgrade()` e `downgrade()` **simetricos**: o `downgrade()` remove apenas objetos criados nesta revisao.
6. Rodar `alembic upgrade head` e `alembic downgrade -1` em ambiente de desenvolvimento com `DATABASE_URL` valido.

## comandos_permitidos

- `cd backend && .venv/bin/alembic heads`
- `cd backend && .venv/bin/alembic upgrade head`
- `cd backend && .venv/bin/alembic downgrade -1`
- `cd backend && .venv/bin/alembic history -v` *(leitura)*

## resultado_esperado

Nova revisao Alembic aplicavel e reversivel que materializa estruturas de recebimento e de divergencia/conciliacao alinhadas ao primeiro criterio Given/When/Then da US (migrations + vinculos + indices).

## testes_ou_validacoes_obrigatorias

- `alembic upgrade head` sem erro apos criar a revisao.
- `alembic downgrade -1` sem erro e sem deixar lixo de schema.
- Verificacao manual (ou query) de existencia dos indices declarados no `upgrade()`.

## stop_conditions

- Parar se nao houver migration de US-3-01 no branch para referenciar FKs.
- Parar se `alembic heads` reportar multiplos heads nao resolvidos (resolver merges antes).
- Parar se for necessario alterar tabelas legadas fora do escopo desta US para satisfazer FKs — escalar para revisao de escopo/ADR.
