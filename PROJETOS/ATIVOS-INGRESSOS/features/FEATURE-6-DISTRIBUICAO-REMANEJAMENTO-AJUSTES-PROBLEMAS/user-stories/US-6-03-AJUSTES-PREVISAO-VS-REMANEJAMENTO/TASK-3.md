---
doc_id: "TASK-3.md"
user_story_id: "US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/schemas/ingressos.py"
  - "backend/app/routers/ingressos.py"
tdd_aplicavel: false
---

# TASK-3 - Exposicao HTTP e schema Pydantic (OpenAPI via FastAPI)

## objetivo

Expor **schemas Pydantic e endpoint(s) HTTP** alinhados ao contrato [TASK-1](./TASK-1.md), delegando calculo ao servico da [TASK-2](./TASK-2.md). O **OpenAPI** e gerado pelo FastAPI a partir dos models de resposta; nenhum ficheiro OpenAPI estatico e obrigatorio salvo convencao futura do repo.

## precondicoes

- [TASK-2.md](./TASK-2.md) concluida (`done`): servico utilizavel a partir da camada de aplicacao.
- Caminho e metodo HTTP fixados no doc `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md`.
- Padroes de autenticacao e erros em `backend/app/routers/ingressos.py` compreendidos.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; se o contrato TASK-1 mandar usar `ativos.py` em vez de `ingressos.py`, atualizar frontmatter e esta task na revisao.

## arquivos_a_ler_ou_tocar

- `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md`
- `backend/app/services/ativos_distribuicao_leituras.py`
- `backend/app/schemas/ingressos.py`
- `backend/app/routers/ingressos.py`
- `backend/app/main.py` *(apenas se registro de router faltar — normalmente ja inclui `ingressos_router`)*

## passos_atomicos

1. Adicionar em `schemas/ingressos.py` modelos de resposta com **campos explicitos** para `aumentado`, `reduzido` e `remanejado` (ou nomes fixados no contrato TASK-1), evitando campos genericos que misturem semantica.
2. Implementar rota(s) GET conforme contrato TASK-1 (parametros: pelo menos `evento_id` e filtros adicionais exigidos).
3. Delegar ao servico TASK-2; mapear erros de dominio para 4xx/5xx alinhados ao router.
4. Docstring da rota: referencia ao ficheiro de contrato TASK-1 e versao/data logica do documento.
5. Verificar em `/docs` (OpenAPI) que cada campo documentado aparece com tipo e descricao suficiente para integrador (summary/description nos schemas ou na rota).

## comandos_permitidos

- `cd backend && ruff check app/schemas/ingressos.py app/routers/ingressos.py`
- `cd backend && PYTHONPATH=<repo-raiz>:<repo-raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py -q` *(regressao rapida)*

## resultado_esperado

- Cliente autenticado obtem JSON com as tres leituras separadas conforme US (Given/When/Then 1).
- Contrato OpenAPI reflete os mesmos nomes que o documento TASK-1 (Given/When/Then 2).

## testes_ou_validacoes_obrigatorias

- Chamada GET feliz com escopo valido retorna HTTP 200 e corpo com tres dimensoes distinguiveis.
- Recurso inexistente ou fora de visibilidade retorna 4xx consistente com o restante de `ingressos.py`.

## stop_conditions

- Parar e reportar `BLOQUEADO` se TASK-1 e TASK-2 nao fixarem parametros de rota ou granularidade necessarios para contrato fechado.
- Parar se houver conflito com rotas planejadas na US-4-05 para o mesmo path — exigir decisao de consolidacao no gate.
