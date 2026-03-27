---
doc_id: "TASK-2.md"
user_story_id: "US-5-02-SERVICO-E-API-EMISSAO"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingressos.py"
  - "backend/app/schemas/ingressos.py"
  - "backend/tests/test_ingressos_endpoints.py"
tdd_aplicavel: true
---

# TASK-2 - Endpoints HTTP, schemas e OpenAPI para emissao

## objetivo

Expor operacoes de emissao **individual** e, se ja previstas no PRD/US sem alargar escopo, **em lote** via FastAPI, com schemas Pydantic, documentacao OpenAPI gerada e integracao ao servico da TASK-1. Propagar `correlation_id` no padrao ja usado em APIs internas (ex. erros em `app/platform/security/rbac.py` ou middleware existente).

## precondicoes

- TASK-1 (`T1`) `done`.
- [US-5-01](../US-5-01-MODELO-E-MIGRACAO-EMISSAO-UNITARIA/README.md) `done`.
- Ler `backend/app/routers/ingressos.py` e `backend/app/schemas/ingressos.py` para alinhar prefixo `/ingressos`, convencoes de erro (`raise_http_error`) e testes existentes.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; preferir evoluir `ingressos.py` antes de criar router paralelo, salvo decisao de modularizacao ja existente no repo.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingressos.py`
- `backend/app/schemas/ingressos.py`
- `backend/app/main.py` *(apenas se registro de router adicional for necessario)*
- Servico implementado em TASK-1 sob `backend/app/services/`
- `backend/tests/test_ingressos_endpoints.py`
- `backend/app/utils/http_errors.py`

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API (TestClient) com usuario autenticado stub: POST de emissao individual retorna **201** (ou codigo acordado) e corpo com **identificador unico** coerente com o modelo (mesma forma que o servico TASK-1).
  - Se lote estiver no escopo: teste minimo de POST em lote com N=2 e verificacao de duas emissoes persistidas ou resposta agregada conforme contrato definido nesta task (documentar no schema OpenAPI).
- comando_para_rodar:
  - `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py -q`
- criterio_red:
  - Os testes novos devem falhar ate rotas e wiring estarem implementados; se passarem antes, parar e revisar.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar pytest e confirmar falha inicial (red).
3. Definir schemas Pydantic de request/response para emissao; adicionar rotas POST (e sub-recursos se necessario) em `ingressos.py` chamando o servico da TASK-1.
4. Garantir que respostas de erro HTTP incluam `correlation_id` quando o projeto padronizar esse campo no JSON de erro.
5. Rodar pytest e confirmar green; refatorar mantendo green.

## comandos_permitidos

- `cd backend && PYTHONPATH="${PWD}/..:${PWD}" SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ingressos_endpoints.py -q`
- `cd backend && ruff check app/routers/ingressos.py app/schemas/ingressos.py`

## resultado_esperado

- OpenAPI (Swagger) lista operacoes de emissao com request/response documentados.
- Fluxo feliz de emissao via API verificado por testes.

## testes_ou_validacoes_obrigatorias

- `tests/test_ingressos_endpoints.py` verde para os novos cenarios.
- Verificacao manual rapida do schema em `/docs` (ou equivalente) para as novas operacoes.

## stop_conditions

- Parar se TASK-1 nao expuser contrato utilizavel sem acoplamento excessivo ao router.
- Parar e **deferir** envio por email (PRD 2.7): apenas documentar em `resultado_esperado` ou comentario de router que integracao com `backend/app/services/email.py` fica para quando houver criterio explicito na US/feature; nao implementar envio automatico nesta task sem decisao.
