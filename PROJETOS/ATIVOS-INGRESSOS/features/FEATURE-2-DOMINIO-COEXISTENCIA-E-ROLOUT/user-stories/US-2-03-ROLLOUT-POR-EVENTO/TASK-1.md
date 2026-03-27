---
doc_id: "TASK-1.md"
user_story_id: "US-2-03-ROLLOUT-POR-EVENTO"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/models/models.py"
  - "backend/alembic/versions/"
  - "backend/docs/auditoria_eventos/"
tdd_aplicavel: true
---

# TASK-1 - Persistencia e registro do criterio de ativacao por evento

## objetivo

Introduzir o mecanismo **persistido e versionado** que representa se um
`evento_id` esta no novo fluxo ou permanece no agregado legado, alinhado ao ADR
ou documento vivo da US-2-01 e ao que US-2-02 deixar como schema base (coluna
em entidade existente, tabela de configuracao por evento, ou variante
documentada). A escolha concreta deve ser **registada** (comentario em revisao
Alembic + uma linha no ADR ou doc operacional referenciado pela US) para
satisfazer o criterio Given/When/Then sobre coerencia do criterio de ativacao.

## precondicoes

- [US-2-02](../US-2-02-MODELO-E-MIGRACOES-INICIAIS/README.md) em `done` com
  migracoes aplicaveis ao repo; sem isso esta task fica **BLOQUEADA** para
  execucao de codigo.
- Baseline PRD 4.0 lido para nao violar contratos do fluxo agregado por
  omissao (default = legado ate marcacao explicita).

## orquestracao

- `depends_on`: nenhuma dentro desta US; dependencia externa obrigatoria: US-2-02.
- `parallel_safe`: `false` (mexe em modelo e migracao).
- `write_scope`: revisao Alembic + modelos SQLModel/SQLAlchemy tocados pelo gate.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-03-ROLLOUT-POR-EVENTO/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-2-DOMINIO-COEXISTENCIA-E-ROLOUT/user-stories/US-2-01-ADR-E-COEXISTENCIA/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/PRD-ATIVOS-INGRESSOS.md` *(sec. 4.1, 8)*
- `backend/app/models/models.py`
- `backend/alembic/env.py`
- `backend/alembic/versions/` *(nova revisao)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste que falha se a estrutura do gate nao existir apos `upgrade` (por
    exemplo: assert de existencia de coluna/tabela ou de valor default legado
    para eventos sem linha explicita), ou teste de migracao em SQLite de teste
    conforme padrao do repo.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(raiz do repo e pacote `app`; ver `docs/SETUP.md` / `AGENTS.md`)*
- criterio_red:
  - Antes da migracao/modelo, o teste novo deve falhar; se passar sem
    implementacao, revisar o teste.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Criar revisao Alembic e modelo associado (ou extensao acordada) para o
   estado persistido do gate por evento; default seguro = **legado**.
4. Rodar migracao em ambiente de teste e confirmar green nos testes novos.
5. Documentar em comentario da revisao e/ou ADR o criterio de ativacao
   (referencia cruzada US-2-01).

## comandos_permitidos

- `cd backend && alembic revision --autogenerate -m "..."` *(ou revisao manual conforme politica do time)*
- `cd backend && alembic upgrade head`
- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q`
- `ruff check` / `ruff format` nos ficheiros tocados

## resultado_esperado

Existe persistencia clara por `evento_id` (ou equivalente alinhado ao dominio)
com default legado; migracao `upgrade`/`downgrade` coerente com PRD sec. 8 e
criterios da US-2-02; teste(s) novo(s) passando.

## testes_ou_validacoes_obrigatorias

- `pytest` com os testes novos e regressao minima dos pacotes tocados.
- Revisao de que nenhum evento existente fica implicitamente no novo fluxo sem
  marcacao explicita.

## stop_conditions

- Parar se US-2-02 nao estiver concluida ou se o schema entregue por US-2-02
  nao comportar o gate sem decisao de produto adicional.
- Parar se autogenerate propor mudancas fora do `write_scope` sem revisao.
