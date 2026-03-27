---
doc_id: "TASK-1.md"
user_story_id: "US-7-04-OPENAPI-CONTRATO-E-QUALIDADE"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/main.py"
  - "backend/app/routers/ativos_ingressos_externo.py"
  - "backend/app/schemas/ativos_ingressos_externo.py"
tdd_aplicavel: false
---

# TASK-1 - OpenAPI e documentacao de idempotencia para ingestao externa

## objetivo

Garantir que o artefato OpenAPI (gerado pelo FastAPI ou publicado em endpoint estavel, ex. `/openapi.json`) descreva integralmente as operacoes de ingestao entregues pela US-7-03: paths, request/response bodies, codigos HTTP, esquemas de erro reutilizaveis e **documentacao explicita** da politica de idempotencia (cabecalhos ou campos chave, semantica de reenvio com a mesma chave).

## precondicoes

- [US-7-03](../US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL/README.md) concluida (`done`): rotas, modelos Pydantic e respostas de erro estaveis.
- Politica de idempotencia acordada em produto/US-7-01 disponivel para transcrever na descricao OpenAPI (sem inventar comportamento).
- Se o modulo do router na US-7-03 tiver nome diferente de `ativos_ingressos_externo.py`, atualizar `write_scope` e esta task antes de implementar.

## orquestracao

- `depends_on`: `[]` (primeira task da US; dependencia externa e US-7-03).
- `parallel_safe`: `false` (base do contrato para T2/T3/T4).
- `write_scope`: routers e schemas da API externa + registo em `main.py`; nao incluir suites de teste (T2).

## arquivos_a_ler_ou_tocar

- `backend/app/main.py`
- Router e schemas entregues pela US-7-03 (caminhos alvo: `backend/app/routers/ativos_ingressos_externo.py`, `backend/app/schemas/ativos_ingressos_externo.py` ou equivalente confirmado no handoff da US-7-03)
- [README.md](./README.md) da US-7-04 (criterios de aceite)
- Documentacao FastAPI/OpenAPI: descricoes em rotas, `responses=`, `openapi_tags`, exemplos em modelos (sem dados sensiveis; detalhe fino em T4)

## passos_atomicos

1. Mapear todos os endpoints publicos de ingestao externa da US-7-03 e confirmar que aparecem no schema OpenAPI com metodo, path, tags e sumarios coerentes.
2. Para cada operacao, documentar corpos de request/response e codigos HTTP (incluindo 4xx/5xx) com modelos ou `JSON` schema alinhados ao codigo.
3. Extrair ou definir modelos de erro comuns (estrutura `detail`, codigos de negocio) e referencia-los nas respostas OpenAPI.
4. Adicionar descricao normativa da idempotencia: quais cabecalhos/campos sao chave de deduplicacao; o que ocorre em reenvio com a mesma chave (ex.: 200 com mesmo recurso, 409, etc.) conforme decisao de produto/US-7-01.
5. Garantir endpoint de documentacao acessivel em ambiente dev (ex.: `/docs`, `/openapi.json`) e, se o projeto exigir artefato estatico versionado, exportar ou gerar bundle conforme convencao do repo (sem alargar escopo alem desta US).
6. Revisar rapidamente que rotas internas ou administrativas nao vazam no mesmo tag que a API de integradores, salvo decisao explicita.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. uvicorn app.main:app --reload` (validacao manual do `/openapi.json` ou `/docs`)
- Ferramentas de lint/format do projeto nos ficheiros tocados, se ja existirem no Makefile ou CI

## resultado_esperado

Integrador ou engenheiro consegue abrir o OpenAPI e encontrar paths, schemas, erros, codigos HTTP e secao/clarificacao de idempotencia alinhados ao comportamento real das rotas da US-7-03.

## testes_ou_validacoes_obrigatorias

- Verificacao manual: `GET /openapi.json` (ou rota equivalente) contem os paths de ingestao externa e descricoes de idempotencia.
- Confirmar que exemplos em schema (se houver) nao contem tokens, senhas ou PII (refinar na T4 se necessario).

## stop_conditions

- Parar se US-7-03 nao estiver `done` ou se os paths do router real divergirem dos ficheiros listados em `write_scope` sem atualizacao documental da task.
- Parar se faltar decisao de produto sobre semantica de idempotencia para documentar.
