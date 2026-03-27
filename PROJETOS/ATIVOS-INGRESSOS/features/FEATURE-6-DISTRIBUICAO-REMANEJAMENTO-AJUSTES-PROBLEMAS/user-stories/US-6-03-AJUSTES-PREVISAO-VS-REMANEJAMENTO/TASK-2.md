---
doc_id: "TASK-2.md"
user_story_id: "US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/services/ativos_distribuicao_leituras.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# TASK-2 - Servico de agregacao: leituras separadas no dominio F6

## objetivo

Implementar no backend **funcoes ou servico de consulta/agregacao** que produzam valores **separados** para `aumentado`, `reduzido` e `remanejado` conforme [TASK-1](./TASK-1.md) e o ADR referenciado ali, garantindo que **nenhum movimento** entre em dois buckets sem documentacao explicita (anti-duplicacao do primeiro criterio Given/When/Then da US).

## precondicoes

- [TASK-1.md](./TASK-1.md) concluida (`done`): ficheiro `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md` aceite.
- [US-6-02 README](../US-6-02-REMANEJAMENTO-AUDITAVEL/README.md) lido para **modelo de eventos** de remanejamento e possiveis tabelas/campos (alinhamento recomendado).
- Se `backend/app/services/ativos_leituras_canonicas.py` ja existir (entrega US-4-05), avaliar **reutilizar** funcoes comuns em vez de duplicar logica; se reutilizar, ajustar `write_scope` desta task na revisao para listar apenas os ficheiros efetivamente tocados.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; incluir `backend/alembic/versions/*.py` apenas se a task precisar de migracao — nesse caso atualizar frontmatter e justificar na revisao.

## arquivos_a_ler_ou_tocar

- `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md`
- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md` *(se existir)*
- `backend/app/services/ativos_distribuicao_leituras.py` *(criar ou fundir com modulo existente acordado no contrato TASK-1)*
- `backend/app/models/models.py` *(somente se faltarem entidades/campos para distinguir ajuste de previsao de remanejamento)*
- `backend/app/routers/ativos.py` e `backend/app/routers/ingressos.py` *(leitura de convencoes de visibilidade; sem novas rotas nesta task se o plano for TASK-3)*

## passos_atomicos

1. Ler o contrato TASK-1 e o ADR; listar identificadores de consulta (ex.: `evento_id`, categoria, diretoria) e fontes SQL/dominio.
2. Implementar servico com `Session` SQLModel que exponha estrutura interna (TypedDict, dataclass ou schema interno) com **tres medidas explicitas** mapeadas 1:1 as semanticas do contrato.
3. Garantir que totais derivados nao somem `remanejado` dentro de `aumentado` ou `reduzido` sem subcampo documentado.
4. Aplicar regras de **visibilidade** coerentes com routers existentes (`_apply_visibility` em `ativos.py` ou equivalente em fluxos admin de ingressos, conforme contrato TASK-1).
5. Docstring ou comentario minimo com referencia ao doc `CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md`.

## comandos_permitidos

- `cd backend && ruff check app/services/ativos_distribuicao_leituras.py`
- `cd backend && ruff check app/models/models.py` *(se tocado)*
- `cd backend && PYTHONPATH=<repo-raiz>:<repo-raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(se models alterados — smoke)*

## resultado_esperado

- Camada de aplicacao (TASK-3) pode obter as tres leituras para o recorte definido no contrato sem ambiguidade.
- Nenhuma rota HTTP nova obrigatoria nesta task.

## testes_ou_validacoes_obrigatorias

- Cenario manual ou REPL: para dados de teste com remanejamento e aumento/reducao no mesmo recorte, o servico retorna componentes nao fundidos num unico campo.
- `ruff check` nos ficheiros tocados sem erros novos introduzidos por esta task.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o contrato TASK-1 nao especificar fontes implementaveis com o modelo atual de codigo.
- Parar se US-6-02 nao tiver entregue distincao persistida entre remanejamento e ajuste — documentar lacuna objetiva e escalar ao gate.
