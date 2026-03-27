---
doc_id: "TASK-2.md"
user_story_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/schemas/ingestao_externa.py"
  - "backend/app/routers/ingestao_externa.py"
  - "backend/tests/test_ingestao_externa_validation.py"
tdd_aplicavel: true
---

# TASK-2 - Esquemas Pydantic e validacao de carga de ingestao

## objetivo

Definir modelos de request/response para a carga de ingestao externa, alinhados
ao dominio de recebimento (FEATURE-4) e aos criterios de aceite desta US:
payload valido aceite; payload invalido ou precondicao de entrada violada gera
4xx com **codigo de erro estavel** e mensagem acordada *(textos e exemplos
completos na US-7-04)*.

## precondicoes

- [TASK-1](./TASK-1.md) concluida (`done`): router e prefixo estaveis.
- [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md) concluida ou dependencia
  de auth aplicada de forma que testes HTTP possam simular integrador
  autenticado.
- Revisar tarefas/servicos FEATURE-4 relevantes (ex.: US-4-02, modelos de
  recebimento) para nao inventar campos fora do contrato de dominio.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.
- `write_scope`: ficheiros no frontmatter; nao implementar idempotencia nem
  persistencia de negocio aqui.

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-4-RECEBIMENTO-CONCILIACAO-E-BLOQUEIOS/FEATURE-4.md`
- `backend/app/schemas/ingestao_externa.py` *(criar)*
- `backend/app/routers/ingestao_externa.py`
- `backend/app/utils/http_errors.py` ou padrao de `HTTPException` do projeto
- `backend/tests/test_ingestao_externa_validation.py` *(criar)*

## testes_red

- testes_a_escrever_primeiro:
  - caso: payload obrigatorio ausente ou tipo errado -> 422 ou 400 com corpo
    contendo codigo de erro estavel (string ou enum interno) definido na task.
  - caso: identificadores de evento/diretoria/categoria inexistentes ou fora de
    escopo (se aplicavel ao contrato) -> 4xx com mesmo formato de erro.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_validation.py`
- criterio_red:
  - os testes novos devem falhar antes da implementacao dos schemas/handlers;
    se passarem sem codigo novo, parar e rever o entendimento do contrato.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar o comando red e confirmar falha inicial ligada a validacao.
3. Implementar schemas Pydantic (campos minimos para a primeira versao da carga
   acordada com FEATURE-4) e ligar ao endpoint POST (ou metodo definido) no
   router, sem ainda persistir estado final de recebimento.
4. Mapear erros de validacao e de negocio leve para respostas 4xx com estrutura
   uniforme (`code`, `message`, opcional `details`).
5. Rodar novamente a suite alvo e confirmar green; refatorar apenas nomes ou
   extracoes locais.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_validation.py`
- `cd backend && ruff check app/schemas/ingestao_externa.py app/routers/ingestao_externa.py`

## resultado_esperado

Contrato de entrada validado na camada HTTP com erros previsiveis e testados;
corpo de sucesso pode ser stub ate T4 preencher orquestracao.

## testes_ou_validacoes_obrigatorias

- Suite `test_ingestao_externa_validation.py` em green.
- Lista dos codigos de erro estaveis documentada em comentario ou docstring no
  modulo de schemas *(US-7-04 consolidara OpenAPI)*.

## stop_conditions

- Parar se o modelo FEATURE-4 nao tiver campos suficientes para um payload
  minimo — escalar para gap em FEATURE-4 ou US predecessora, sem alargar escopo
  da US-7-03.
- Parar se a US-7-02 impedir testes autenticados; concluir apenas schemas
  unitarios e abrir bloqueio explicito.
