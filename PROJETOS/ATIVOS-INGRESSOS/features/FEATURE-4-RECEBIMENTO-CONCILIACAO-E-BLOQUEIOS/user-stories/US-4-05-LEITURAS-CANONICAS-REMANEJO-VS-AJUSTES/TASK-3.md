---
doc_id: "TASK-3.md"
user_story_id: "US-4-05-LEITURAS-CANONICAS-REMANEJO-VS-AJUSTES"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/schemas/ativos.py"
  - "backend/app/routers/ativos.py"
tdd_aplicavel: false
---

# TASK-3 - Contrato estavel de API para leituras canonicas

## objetivo

Expor **schemas Pydantic e endpoint(s) HTTP** (ou extensao coerente do router `/ativos`) que entreguem ao cliente interno as **leituras canonicas** implementadas na TASK-2, com **contrato JSON estavel** alinhado ao ADR da TASK-1 e preparado para consumo futuro pelo dashboard FEATURE-8 (sem implementar FEATURE-8).

## precondicoes

- [TASK-2.md](./TASK-2.md) concluida (`done`): servico de leituras canonicas utilizavel a partir da camada de aplicacao.
- Padroes de autenticacao e erros HTTP em `backend/app/routers/ativos.py` compreendidos.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `docs/adr/ADR-ATIVOS-INGRESSOS-leituras-canonicas-remanejo-vs-ajustes.md`
- `backend/app/services/ativos_leituras_canonicas.py`
- `backend/app/schemas/ativos.py`
- `backend/app/routers/ativos.py`
- `backend/app/main.py` *(apenas se registro de router exigir alteracao — normalmente nao)*

## passos_atomicos

1. Definir em `ativos.py` (schemas) modelos de resposta com campos explicitos para cada dimensao canonicas (ex.: `remanejado`, `aumentado`, `reduzido` ou nomes fixados no ADR), evitando campos genericos que misturem semantica.
2. Implementar rota GET sob prefixo `/ativos` (ou sub-recurso acordado no ADR) que aceite identificadores minimos (`evento_id`, e filtros adicionais exigidos pelo ADR: categoria, diretoria, etc.).
3. Delegar calculo ao servico da TASK-2; mapear erros de dominio para 4xx/5xx alinhados ao restante do router.
4. Documentar no docstring da rota referencia ao ADR e versao logica do contrato (data ou versao do ADR).
5. Garantir que resposta nao agrega remanejado em campos de aumento/reducao sem subcampos separados.

## comandos_permitidos

- `cd backend && ruff check app/schemas/ativos.py app/routers/ativos.py`
- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q` *(ajustar ou adicionar testes na TASK-4 se preferir separacao)*

## resultado_esperado

- Cliente autenticado (frontend ou servico interno) obtem JSON com leituras separadas conforme US (Given/When/Then 1).
- Contrato documentado e estavel o suficiente para FEATURE-8 consumir na mesma forma sem reinterpretacao.

## testes_ou_validacoes_obrigatorias

- Chamada GET feliz com escopo valido retorna HTTP 200 e corpo contendo campos distintos para remanejado e para ajustes (aumento/reducao), conforme ADR.
- Evento inexistente ou fora de visibilidade retorna 4xx consistente com `listar_ativos`.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o ADR e a TASK-2 nao fixarem parametros de rota ou granularidade (evento vs categoria) necessarios para um contrato fechado.
- Parar se o PRD exigir prefixo ou autenticacao diferente sem decisao documentada.
