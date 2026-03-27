---
doc_id: "TASK-2.md"
user_story_id: "US-6-04-PROBLEMAS-OPERACIONAIS"
task_id: "T2"
version: "2.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/schemas/ingressos.py"
  - "backend/app/routers/ingressos.py"
  - "backend/app/main.py"
tdd_aplicavel: false
---

# T2 - API: criar e listar problemas operacionais por evento

## objetivo

Expor endpoints autenticados para **criar** uma ocorrencia e **listar** ocorrencias filtradas por `evento_id`, com **paginacao ou limite** explicito no contrato OpenAPI (query params documentados: ex. `limit`/`offset` ou `page`/`page_size`). Respostas devem incluir os campos necessarios para consumo futuro pelo dashboard (FEATURE-8) sem inventar campos fora da US.

## precondicoes

- T1 `done`: tabela e modelo SQLModel disponiveis.
- Padrao de autenticacao e RBAC para operadores NPBB/admin alinhado a rotas existentes em `ingressos.py` ou `ativos.py` — reutilizar `get_current_user` / helpers do projeto.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: false.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py`
- `backend/app/core/auth.py` *(ou modulo efetivo de dependencias de usuario)*
- `backend/app/utils/http_errors.py`
- `backend/app/main.py` *(registo de router apenas se criar router novo; caso contrario omitir)*
- `backend/app/models/models.py` *(modelo da T1)*

## passos_atomicos

1. Definir schemas Pydantic: corpo de criacao (tipo, descricao, evento_id; opcional correlation_id se coluna existir), item de leitura, resposta de listagem paginada (lista + metadados minimos de paginacao se o projeto padronizar assim).
2. Implementar POST que persiste registro com estado `problema_registrado` coerente com a T1; validar que `evento_id` referencia evento existente; erros 4xx claros.
3. Implementar GET (ou GET com path `evento_id`) que retorna apenas linhas daquele evento; aplicar limite maximo defensivo (ex. cap de `limit`) documentado.
4. Garantir transacao com commit/rollback coerente com o restante do backend.
5. Registrar rotas no router escolhido; preferir prefixo sob `/ingressos` ou `/ativos` consistente com operadores de evento (decisao documentada no PR do commit).

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true .venv/bin/python -m pytest tests/test_ingressos_endpoints.py -q` *(regressao rapida se tocar router compartilhado)*
- `cd backend && ruff check app/routers/ingressos.py app/schemas/ingressos.py`

## resultado_esperado

Contrato HTTP estavel para criar e listar por evento, alinhado aos criterios Given/When/Then da US.

## testes_ou_validacoes_obrigatorias

- Smoke manual ou documentado: POST + GET com filtro retorna o registro criado.
- Evento inexistente ou sem permissao retorna 4xx adequado (alinhado a convencoes do repo).

## stop_conditions

- Parar se RBAC nao cobrir operador de evento sem refatoracao ampla — coordenar com PM e possivel divisao de sub-rota protegida.
- Parar se o modelo da T1 nao expuser colunas necessarias ao contrato; retornar a T1.
