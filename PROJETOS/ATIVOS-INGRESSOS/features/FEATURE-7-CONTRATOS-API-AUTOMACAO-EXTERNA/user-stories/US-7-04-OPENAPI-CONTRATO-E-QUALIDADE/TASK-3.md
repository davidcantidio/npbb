---
doc_id: "TASK-3.md"
user_story_id: "US-7-04-OPENAPI-CONTRATO-E-QUALIDADE"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/main.py"
  - "backend/app/middleware/observabilidade_integrador.py"
  - "backend/app/routers/ativos_ingressos_externo.py"
tdd_aplicavel: false
---

# TASK-3 - Observabilidade: correlation_id e identificacao do integrador em logs

## objetivo

Para pedidos autenticados a API de ingestao externa, garantir logs ou traces estruturados que permitam correlacionar por `correlation_id` (cabecalho ou campo aceito pelo servico) e identificar o **integrador** (ex.: id, slug ou escopo), **sem** registrar segredos (tokens completos, chaves privadas, PII desnecessaria).

## precondicoes

- T1 concluida: contrato pode documentar cabecalho de correlacao, se aplicavel.
- US-7-02 concluida: identidade do integrador disponivel no request context apos autenticacao.
- US-7-03 concluida: rotas de ingestao externa ativas.

## orquestracao

- `depends_on`: `["T1"]` (evita conflito simultaneo com edicao inicial do router; apos T1, estabilizar observabilidade nas mesmas rotas).
- `parallel_safe`: `false`.
- `write_scope`: middleware novo sob `backend/app/middleware/` e registo em `main.py`; ajustes pontuais no router externo apenas para propagar contexto se necessario.

## arquivos_a_ler_ou_tocar

- `backend/app/main.py`
- `backend/app/middleware/observabilidade_integrador.py` (criar, ou nome alinhado ao padrao do repo)
- Router de ingestao externa (`backend/app/routers/ativos_ingressos_externo.py` ou modulo real da US-7-03)
- Dependencias de auth do integrador (US-7-02) para extrair identificador seguro para log
- Referencia de padrao existente: `backend/app/modules/revisao_humana/s2_observability.py` (correlation_id em dominio interno; reutilizar ideias, nao acoplar imports desnecessarios)

## passos_atomicos

1. Definir contrato de entrada: aceitar `X-Correlation-ID` (ou nome acordado) e normalizar para um valor de trace; gerar UUID se ausente, conforme politica do projeto.
2. Implementar middleware ou dependency chain que anexe `correlation_id` e identificador do integrador ao contexto de logging (ex.: `structlog`, `logging` com `extra`, ou integracao OpenTelemetry se ja existir).
3. Garantir que handlers da ingestao externa emitam pelo menos uma linha estruturada por request processado (sucesso ou erro de negocio) contendo `correlation_id` e id do integrador.
4. Mascarar ou omitir cabecalhos `Authorization` e campos sensiveis em qualquer dump de debug.
5. Documentar no OpenAPI (descricao de operacao ou tag) o cabecalho de correlacao recomendado, se ainda nao estiver na T1.
6. Adicionar teste(s) leves que assertem presenca de campos no log capturado (opcional mas recomendado) ou validacao manual documentada no handoff da US.

## comandos_permitidos

- `cd backend && PYTHONPATH=..:. SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/<suite_que_cobrir_middleware_ou_router>.py`
- `cd backend && PYTHONPATH=..:. uvicorn app.main:app --reload` com inspecao de logs locais

## resultado_esperado

Suporte consegue seguir um `correlation_id` do integrador ate os eventos da API de ingestao externa; logs nao contem segredos em claro.

## testes_ou_validacoes_obrigatorias

- Teste automatizado ou checklist manual: request com cabecalho de correlacao propagado para log; request autenticado com identificador do integrador visivel no log estruturado.
- Grep ou revisao: nenhum token Bearer completo em strings de log adicionadas nesta task.

## stop_conditions

- Parar se a stack de logging do projeto nao suportar `extra`/contexto sem refatoracao ampla (escalar para spike ou US separada).
- Parar se identificador do integrador nao estiver acessivel apos auth (dependencia US-7-02).
