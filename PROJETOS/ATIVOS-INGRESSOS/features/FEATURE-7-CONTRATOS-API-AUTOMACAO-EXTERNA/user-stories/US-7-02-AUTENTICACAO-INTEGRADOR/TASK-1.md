---
doc_id: "TASK-1.md"
user_story_id: "US-7-02-AUTENTICACAO-INTEGRADOR"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on: []
parallel_safe: false
write_scope:
  - "PROJETOS/ATIVOS-INGRESSOS/features/FEATURE-7-CONTRATOS-API-AUTOMACAO-EXTERNA/user-stories/US-7-02-AUTENTICACAO-INTEGRADOR/DECISAO-AUTH-INTEGRADOR.md"
tdd_aplicavel: false
---

# TASK-1 - Decisao e contrato do mecanismo de autenticacao do integrador

## objetivo

Fechar o mecanismo de autenticacao para integradores externos (API key em header, Bearer/JWT de servico, ou mTLS terminado no edge com propagacao de claim), alinhado ao que ja existe no monolito (`HTTPBearer`, JWT em `app.utils.jwt`, `get_current_user`), e registar o contrato operacional: nomes de header ou esquema Bearer, formato do contexto exposto ao request (identificador do integrador, escopos), e criterios 401 vs 403.

## precondicoes

- [README.md](./README.md) da US e [FEATURE-7.md](../../FEATURE-7.md) lidos (sem alargar escopo alem da US-7-02).
- Leitura exploratoria de `backend/app/core/auth.py` e `backend/app/utils/jwt.py` para reutilizar padroes quando fizer sentido (integrador nao e `Usuario` interno).

## orquestracao

- `depends_on`: nenhuma task anterior na mesma US.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter (ficheiro de decisao na pasta desta US).

## arquivos_a_ler_ou_tocar

- `backend/app/core/auth.py`
- `backend/app/utils/jwt.py`
- `backend/app/platform/security/rbac.py` *(referencia de 403 estruturado)*
- [README.md](./README.md)
- [FEATURE-7.md](../../FEATURE-7.md)
- `DECISAO-AUTH-INTEGRADOR.md` *(criar nesta task com a decisao e o contrato)*

## passos_atomicos

1. Comparar opcoes: (a) API key estatica ou por integrador via env/config; (b) JWT de servico assinado com `SECRET_KEY` ou chave dedicada; (c) mTLS apenas no edge — documentar o que o backend valida (ex.: header confiavel vs cert client).
2. Escolher **uma** abordagem principal para a primeira entrega compativel com a US e com execucao antes ou depois da US-7-01 (env/config nao exige schema; persistencia de chaves por integrador exige US-7-01 `done`).
3. Redigir `DECISAO-AUTH-INTEGRADOR.md` com: mecanismo escolhido, mapeamento para monolito, lista de variaveis de ambiente ou configuracao, formato do objeto/contexto injectado no request (campos minimos para logs e idempotencia na US-7-03), e quando usar 401 vs 403.
4. Definir nomes estaveis para headers ou claims (ex.: prefixo `X-` ou `Authorization: Bearer <token>`) para as tasks seguintes implementarem sem renomeacao.

## comandos_permitidos

- Nenhum obrigatorio nesta task (documental). Opcional: `cd backend && ruff check app/core/auth.py` apos leitura, sem alteracoes obrigatorias.

## resultado_esperado

- Ficheiro `DECISAO-AUTH-INTEGRADOR.md` existente, com decisao unica e contrato suficiente para implementar `Depends` na TASK-2 e validacao na TASK-3.
- Nenhum codigo de aplicacao alterado obrigatoriamente nesta task.

## testes_ou_validacoes_obrigatorias

- Revisao interna: o contrato cobre os tres criterios Given/When/Then da US ao nivel de desenho (401/403 sem efeito de negocio, propagacao de identidade, base para testes automatizados).

## stop_conditions

- Parar e reportar `BLOQUEADO` se o produto exigir mTLS mutual no processo FastAPI sem terminacao no edge e isso nao estiver no PRD/US.
- Parar se a decisao depender de tabelas da US-7-01 mas a US-7-01 nao estiver `done` — nesse caso explicitar no documento o caminho **B**: apenas env/config ate a US-7-01 concluir.
