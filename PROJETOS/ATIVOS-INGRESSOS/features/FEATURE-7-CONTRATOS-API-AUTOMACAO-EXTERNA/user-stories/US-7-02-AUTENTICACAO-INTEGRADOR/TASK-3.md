---
doc_id: "TASK-3.md"
user_story_id: "US-7-02-AUTENTICACAO-INTEGRADOR"
task_id: "T3"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T2"
parallel_safe: false
write_scope:
  - "backend/app/core/integrador_auth.py"
  - "backend/app/models/models.py"
  - "backend/alembic/versions/"
tdd_aplicavel: false
---

# TASK-3 - Validacao de segredos e escopos por integrador

## objetivo

Completar a validacao da credencial (comparacao segura de segredo, verificacao de JWT, ou leitura de claim acordada) e associar **identidade do integrador** e **escopos** ao contexto do request, de forma auditavel (minimo: identificador estavel para logs e correlacao com idempotencia na US-7-03).

## precondicoes

- TASK-2 concluida (`done`): dependencia base e ramos 401/403 sem negocio.
- **Se** a decisao em T1 usar tabelas ou entidades introduzidas na [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md): US-7-01 deve estar `done` antes de implementar persistencia ou lookup no banco.
- **Se** a decisao em T1 for apenas env/config (lista de chaves ou mapa integrador->segredo): nenhuma dependencia da US-7-01 para esta task.

## orquestracao

- `depends_on`: `T2`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; incluir `alembic/versions/` **somente** se migrations forem estritamente necessarias **e** dentro do escopo aprovado da US-7-02 (evitar duplicar modelo da US-7-01).

## arquivos_a_ler_ou_tocar

- `DECISAO-AUTH-INTEGRADOR.md`
- `backend/app/core/integrador_auth.py`
- `backend/app/models/models.py` *(somente se lookup persistido e ja existir modelo da US-7-01 ou contrato partilhado)*
- `backend/.env` / documentacao de env *(sem commitar segredos)*
- [US-7-01](../US-7-01-MODELO-IDEMPOTENCIA-E-CHAVES-EXTERNAS/README.md) *(se credenciais no schema de idempotencia)*

## passos_atomicos

1. Implementar validacao de segredo conforme T1: comparacao em tempo constante para segredos, ou `decode_token`/assinatura para JWT de servico, ou confianca no header do edge documentada.
2. Mapear credencial valida para `integrador_id` (string ou UUID estavel) e conjunto de escopos permitidos; armazenar em `request.state` ou retornar dataclass tipada consumida pelos routers.
3. Retornar **403** quando a credencial e valida mas o escopo nao permite a operacao (se a US definir escopo fino nesta entrega); caso contrario manter apenas autenticacao e deixar autorizacao fina para US-7-03 com contrato explicito no documento T1.
4. Logging estrutural minimo: linha ou campo que permita correlacionar `integrador_id` a pedidos (sem logar segredo ou token completo).
5. Se precisar de nova tabela **apenas** para integradores e isso nao couber na US-7-01, parar e alinhar escopo (preferir env ate haver modelo canónico).

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_integrador_auth.py -q`
- `cd backend && ruff check app/core/integrador_auth.py app/models/models.py`
- `cd backend && alembic upgrade head` *(se migrations novas e ambiente local)*

## resultado_esperado

- Integrador autenticado com credencial valida tem identidade e escopos disponiveis no contexto do request conforme criterio de aceite da US.
- Credencial invalida ou integrador inactivo: 401/403 sem alteracao de estado de negocio.

## testes_ou_validacoes_obrigatorias

- Caso positivo: credencial valida popula contexto com `integrador_id` esperado.
- Caso negativo: segredo errado ou revogado resulta em 401/403.

## stop_conditions

- Parar com `BLOQUEADO` se o desenho exigir schema da US-7-01 e esta nao estiver `done`.
- Parar se o PRD exigir quotas/rate limit obrigatorio nesta US — registar follow-up para US-7-03 ou task futura sem bloquear o minimo da US-7-02.
