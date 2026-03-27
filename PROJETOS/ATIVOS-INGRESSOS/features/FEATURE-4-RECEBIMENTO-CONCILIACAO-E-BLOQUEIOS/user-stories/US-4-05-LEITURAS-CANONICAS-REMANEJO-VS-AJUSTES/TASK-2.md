---
doc_id: "TASK-2.md"
user_story_id: "US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/services/ativos_leituras_canonicas.py"
  - "backend/app/models/models.py"
tdd_aplicavel: false
---

# TASK-2 - Leituras canonicas no dominio (remanejado isolado)

## objetivo

Implementar no backend **funcoes ou servicos de consulta/agregacao** que produzam as **leituras canonicas** definidas no ADR da TASK-1, garantindo que **remanejado** nao seja misturado indevidamente com **aumento** ou **reducao** nas mesmas medidas (PRD 2.6; criterio 1 da US).

## precondicoes

- [TASK-1.md](./TASK-1.md) concluida (`done`): ADR publicado e mapeamento entidade→leitura aceite.
- Baseline de persistencia da [US-4-01](../US-4-01-MODELO-PERSISTENCIA-RECEBIMENTO/README.md) disponivel no codigo (tabelas/eventos de recebimento, movimentos ou equivalentes) — se incompleto, implementar apenas ramos cobertos pelo modelo existente e documentar lacuna no `resultado_esperado`.
- Regras de **prevalencia do recebido** e teto distribuivel da [US-4-03](../US-4-03-PREVALENCIA-RECEBIDO-TETO-DISTRIBUIVEL/README.md) e bloqueios da [US-4-04](../US-4-04-BLOQUEIO-POR-RECEBIMENTO/README.md) lidas para **nao contradizer** consultas de saldo quando integradas (detalhe de consistencia formal na TASK-4).

## orquestracao

- `depends_on`: `T1` (ADR aprovado).
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; ajustar lista se o executor consolidar logica em modulo existente em vez de ficheiro novo, **desde que** atualize este documento na revisao.

## arquivos_a_ler_ou_tocar

- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md`
- `backend/app/services/ativos_leituras_canonicas.py` *(criar ou substituir por modulo acordado no ADR)*
- `backend/app/models/models.py` *(entidades de recebimento / movimento / cota conforme US-4-01)*
- `backend/app/routers/ativos.py` *(apenas leitura para alinhar convencoes de visibilidade; sem alterar rotas nesta task se o contrato for TASK-3)*

## passos_atomicos

1. Ler o ADR e listar as leituras obrigatorias e suas fontes SQL/dominio.
2. Implementar funcoes puras ou servico com sessao SQLModel que retornem estruturas internas (dataclasses/TypedDict ou modelos Pydantic internos) por **dimensao**: pelo menos `remanejado`, `aumentado`, `reduzido` (ou nomes do ADR) para o recorte evento/categoria/diretoria definido no ADR.
3. Garantir que agregacoes que alimentam "totais" operacionais nao somem remanejado dentro de aumento/reducao sem campo separado documentado.
4. Aplicar mesma regra de **visibilidade por agencia** usada em `ativos.py` (`_apply_visibility` ou equivalente) nas consultas novas.
5. Registrar no codigo ou docstring curta referencia ao ID do ADR para rastreabilidade.

## comandos_permitidos

- `cd backend && ruff check app/services/ativos_leituras_canonicas.py app/models/models.py`
- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q` *(suite rapida apos alteracoes em models — apenas se TASK-2 tocar em models)*

## resultado_esperado

- Cliente interno (camada de aplicacao ou TASK-3) pode obter valores separados para remanejado versus ajustes para um mesmo evento/categoria conforme ADR.
- Nenhuma rota HTTP nova obrigatoria nesta task se o plano for delegar exposicao a TASK-3.

## testes_ou_validacoes_obrigatorias

- Cenario manual ou script: para dados de teste com evento de remanejamento e aumento/reducao no mesmo recorte, as funcoes retornam componentes nao ambiguos (valores nao "fundidos" em um unico campo sem documentacao).
- `ruff check` nos ficheiros tocados sem erros novos introduzidos por esta task.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o ADR nao especificar fontes de dados implementaveis com o modelo atual.
- Parar se US-4-01 nao tiver entregue persistencia minima para distinguir remanejamento de ajustes — escalar para gate com lacuna objetiva.
