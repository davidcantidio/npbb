---
doc_id: "TASK-1.md"
user_story_id: "US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/routers/ativos.py"
  - "backend/app/schemas/ativos.py"
tdd_aplicavel: false
---

# TASK-1 - Leitura de configuracao por evento e contrato dos modos canonicos

## objetivo

Expor via API (ou extensao coerente do router de ativos) a leitura da configuracao de categorias por evento e garantir que o contrato de resposta inclua, de forma estavel, os **dois modos canonicos de fornecimento** definidos no manifesto da FEATURE-3 e na US: **interno emitido com QR** e **externo recebido**, para consumo por frontend e preparacao das FEATURE-4/FEATURE-5.

## precondicoes

- [US-3-01](../US-3-01-MODELAGEM-PERSISTENCIA-E-DEFAULTS-LEGADO/README.md) concluida (`done`): modelo persistido, migracoes e seeds/defaults de legado alinhados ao PRD e ao manifesto FEATURE-3.
- Rotas existentes em `backend/app/routers/ativos.py` e padroes de schema em `backend/app/schemas/ativos.py` lidos para manter consistencia com visibilidade por agencia e convencoes do projeto.

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false` (mesmo router e schemas compartilhados).
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ativos.py`
- `backend/app/schemas/ativos.py`
- `backend/app/models/models.py` *(ou modulos entregues pela US-3-01)*
- `backend/app/main.py` *(apenas se novas rotas precisarem de registro explicito)*
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-3-CATEGORIAS-E-MODOS-FORNECIMENTO/FEATURE-3.md` *(sec. 2, 4, 7)*

## passos_atomicos

1. Definir enums ou literais de API alinhados aos dois modos canonicos (nomes estaveis em JSON; documentar mapeamento para o dominio persistido da US-3-01).
2. Definir schemas Pydantic de resposta para a configuracao por evento (categorias habilitadas, modos ou referencias acordadas) sem implementar ainda a alteracao por esta task.
3. Implementar endpoint(s) GET (ou sub-recurso sob `/ativos` ou prefixo acordado no PRD) que retornem a configuracao leida do banco para um `evento_id` valido e autenticado.
4. Garantir que a resposta expõe explicitamente os dois valores canonicos de modo (lista fixa, discriminador ou campo dedicado) de forma que consumidores internos nao dependam de strings magicas espalhadas.
5. Tratar evento inexistente ou fora de escopo de visibilidade com 4xx alinhado ao padrao existente (`raise_http_error` ou equivalente).

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_endpoints.py -q` *(apos ajustes minimos de teste se existirem)*
- `cd backend && ruff check app/routers/ativos.py app/schemas/ativos.py`

## resultado_esperado

- Cliente autenticado obtem, para um evento elegivel, payload JSON estavel com configuracao de categorias e representacao clara dos dois modos canonicos.
- Nenhuma operacao de escrita de configuracao e introduzida nesta task.

## testes_ou_validacoes_obrigatorias

- Chamada GET feliz retorna HTTP 200 e corpo contendo ambos os identificadores de modo canonicos acordados.
- Caso de evento invalido ou nao visivel retorna 4xx consistente com o restante do router de ativos.

## stop_conditions

- Parar e reportar `BLOQUEADO` se o modelo ou tabelas da US-3-01 nao estiverem disponiveis no codigo.
- Parar se o PRD ou a FEATURE-3 exigirem um prefixo ou recurso de URL diferente do padrao atual sem decisao documentada (escopo fora desta US).
