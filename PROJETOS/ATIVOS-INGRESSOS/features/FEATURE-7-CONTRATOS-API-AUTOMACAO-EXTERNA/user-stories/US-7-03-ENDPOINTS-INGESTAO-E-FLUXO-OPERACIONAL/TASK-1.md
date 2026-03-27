---
doc_id: "TASK-1.md"
user_story_id: "US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/app/routers/ingestao_externa.py"
  - "backend/app/main.py"
  - "backend/tests/test_ingestao_externa_router.py"
tdd_aplicavel: false
---

# TASK-1 - Router FastAPI, prefixo externo e registo na aplicacao

## objetivo

Criar o router dedicado a ingestao por integradores externos (FEATURE-7), com
prefixo e tags acordados, registado em `main.py`, servindo de superficie para
dependencias de autenticacao entregues pela [US-7-02](../US-7-02-AUTENTICACAO-INTEGRADOR/README.md) e para os endpoints de carga
definidos nas tasks seguintes.

## precondicoes

- Ler o `README.md` desta US e [FEATURE-7.md](../../FEATURE-7.md) sec. 6
  (estrategia API / namespace).
- Confirmar convencao de prefixos no monolito (ex.: rotas internas vs externas)
  em `backend/app/main.py` e routers existentes.
- US-7-02 pode estar em curso: usar **stub** de dependencia FastAPI documentado
  (ex.: `Depends(...)` placeholder) apenas ate o mecanismo real existir, sem
  desviar o objetivo desta task.

## orquestracao

- `depends_on`: `[]`.
- `parallel_safe`: `false`.
- `write_scope`: ficheiros listados no frontmatter; nao expandir a logica de
  negocio de ingestao (T2+).

## arquivos_a_ler_ou_tocar

- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-03-ENDPOINTS-INGESTAO-E-FLUXO-OPERACIONAL/README.md`
- `PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/FEATURE-7.md`
- `backend/app/main.py`
- `backend/app/routers/ingestao_inteligente.py` *(referencia de padrao interno:
  `correlation_id`, validacao leve, `APIRouter`)*
- `backend/app/routers/ingestao_externa.py` *(criar)*
- `backend/tests/test_ingestao_externa_router.py` *(criar; pytest com cwd `backend/`: `tests/test_ingestao_externa_router.py`)*

## testes_red

> Nao aplicavel (`tdd_aplicavel: false`).

## passos_atomicos

1. Definir constantes de prefixo e tag OpenAPI (ex.: `/external/ativos-ingressos/v1` ou nome alinhado ao PRD/manifesto; documentar escolha num comentario curto no router).
2. Criar `APIRouter` com `prefix` e `tags`; expor rota minima de verificacao (ex.: `GET` de scaffold ou `HEAD`/health do namespace) que nao persista dados.
3. Incluir o router em `main.py` na mesma ordem/padrao dos demais routers.
4. Adicionar dependencia de autenticacao de integrador como parametro das rotas (assinatura preparada para US-7-02); se o tipo ainda nao existir, usar `Annotated` + dependencia provisoria claramente marcada `TODO(US-7-02)`.
5. Escrever teste smoke que assegura que a aplicacao monta o router e a rota minima responde (status esperado sem efeitos colaterais de negocio).

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ingestao_externa_router.py`
- `cd backend && ruff check app/routers/ingestao_externa.py app/main.py`

## resultado_esperado

Router externo registado, visivel na app e testavel por smoke; ponto de extensao
para payloads (T2), idempotencia (T3) e orquestracao (T4).

## testes_ou_validacoes_obrigatorias

- `pytest` no ficheiro de teste do router com `TESTING=true`.
- Verificar na doc OpenAPI gerada (Swagger) que o prefixo e as tags aparecem
  *(detalhamento fino do contrato completo fica para US-7-04)*.

## stop_conditions

- Parar se o prefixo colidir com rotas publicas ou internas existentes sem ADR
  ou alinhamento com FEATURE-7.
- Parar se for necessario implementar logica de segredo/token nesta task —
  pertence a US-7-02.
