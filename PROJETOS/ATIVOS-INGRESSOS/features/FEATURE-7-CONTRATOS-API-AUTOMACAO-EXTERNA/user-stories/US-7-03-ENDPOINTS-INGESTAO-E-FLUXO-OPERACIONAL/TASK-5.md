---
doc_id: "TASK-5.md"
user_story_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
task_id: "T5"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T4"
parallel_safe: false
write_scope:
  - "backend/app/routers/ingestao_externa.py"
  - "backend/app/middleware/ingestao_externa_limits.py"
  - "backend/tests/test_ingestao_externa_limits.py"
tdd_aplicavel: false
---

# TASK-5 - Quotas, rate limit e observabilidade minima do integrador

## objetivo

Proteger o namespace de ingestao externa com limites de taxa ou quotas **se
estes nao estiverem ja cobertos pela [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md)**,
e garantir logging estruturado com `correlation_id` e identificacao do
integrador nas requisicoes de ingestao, alinhado ao manifesto FEATURE-7 impacts
de observabilidade *(refinamento de OpenAPI e suites de carga negativa na
US-7-04)*.

## precondicoes

- [TASK-4](./TASK-4.md) concluida: fluxo operacional funcional.
- Ler o `README.md` e as tasks da [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md)
  e decidir, no inicio desta task, se rate limit/quotas ja foram implementados
  la.
- Revisar padroes de logging em `ingestao_inteligente.py` para consistencia.

## orquestracao

- `depends_on`: `T4`.
- `parallel_safe`: `false`.
- `write_scope`: limiter/middleware opcional + ajustes no router + testes;
  cancelar implementacao de limites com justificativa se US-7-02 absorver 100%
  do requisito.

## arquivos_a_ler_ou_tocar

- `backend/app/routers/ingestao_externa.py`
- `backend/app/middleware/ingestao_externa_limits.py` *(criar apenas se
  necessario; ou usar dependencia FastAPI / slowapi / util existente no repo)*
- `backend/app/main.py` *(apenas se registo de middleware for necessario)*
- `backend/tests/test_ingestao_externa_limits.py` *(criar se limites forem
  implementados; senao marcar N/A na execucao e referenciar testes da US-7-02)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`). Se optar por TDD para limites,
  alinhar com PM e definir `tdd_aplicavel: true` em revisao documental.

## passos_atomicos

1. Documentar decisao: limites na US-7-02 vs nesta task *(comentario no PR ou no
   corpo da task ao concluir)*.
2. Se necessario, aplicar rate limit por integrador ou por IP+token no router
   `ingestao_externa` ou via middleware dedicado; retornar 429 com corpo
   minimamente alinhado aos erros da TASK-2.
3. Garantir que cada request de ingestao loga `correlation_id` *(header ou
   gerado)* e identificador do integrador *(apos US-7-02)* sem dados sensiveis
   em claro (segredos mascarados).
4. Adicionar testes de limite *(ex.: N requests seguidas excedem limiar em
   ambiente de teste)* ou, se cancelado, atualizar esta task com status
   `cancelled` e justificativa no handoff da US.
5. Validar que o comportamento nao quebra fluxos green da TASK-4.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_limits.py` *(se existir)*
- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_fluxo_operacional.py`
- `cd backend && ruff check app/routers/ingestao_externa.py app/middleware/ingestao_externa_limits.py`

## resultado_esperado

Ou limites ativos e testados no namespace externo, ou decisao explicita de
cancelamento com cobertura equivalente na US-7-02; logging minimo de observabilidade
presente nas rotas de ingestao externa.

## testes_ou_validacoes_obrigatorias

- Se limites implementados: teste que demonstra 429 apos limiar.
- Inspecao de uma linha de log (teste com caplog ou documentacao de verificacao
  manual) com `correlation_id` e id de integrador.

## stop_conditions

- Parar se a stack nao tiver biblioteca de rate limit acordada — propor ADR ou
  reutilizar padrao ja usado noutro router antes de adicionar dependencia nova.
- Parar se logging PII violar politica do PRD — ajustar campos com juridico/PM.
