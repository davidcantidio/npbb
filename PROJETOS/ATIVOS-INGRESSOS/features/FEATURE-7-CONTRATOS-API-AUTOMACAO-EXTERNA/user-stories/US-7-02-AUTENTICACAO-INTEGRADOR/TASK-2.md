---
doc_id: "TASK-2.md"
user_story_id: "US-7-02-AUTENTICACAO-INTEGRADOR"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/app/core/integrador_auth.py"
  - "backend/app/main.py"
tdd_aplicavel: false
---

# TASK-2 - Dependencia FastAPI e respostas 401/403 sem efeitos colaterais

## objetivo

Implementar uma dependencia FastAPI reutilizavel (ex.: `get_integrador_autenticado` ou `require_integrador`) que, **sem credencial valida**, falhe com HTTP **401** ou **403** conforme `DECISAO-AUTH-INTEGRADOR.md`, **sem** executar logica de negocio nem tocar em dados de recebimento. Preencher `request.state` (ou tipo dedicado retornado pelo `Depends`) com placeholder de identidade quando a validacao completa for concluida na TASK-3, mantendo a assinatura estavel.

## precondicoes

- TASK-1 concluida (`done`): `DECISAO-AUTH-INTEGRADOR.md` disponivel com contrato de header/Bearer e codigos HTTP.
- Padroes de `HTTPException` e headers `WWW-Authenticate` alinhados a `backend/app/core/auth.py` onde aplicavel.

## orquestracao

- `depends_on`: `T1`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter.

## arquivos_a_ler_ou_tocar

- `DECISAO-AUTH-INTEGRADOR.md`
- `backend/app/core/auth.py`
- `backend/app/core/integrador_auth.py` *(criar)*
- `backend/app/main.py` *(registrar router de smoke apenas se necessario para validacao manual antes da TASK-4; preferir testes isolados na TASK-4)*
- [README.md](./README.md)

## passos_atomicos

1. Criar modulo `integrador_auth.py` com funcao/dependencia que: (a) extrai credencial conforme contrato T1; (b) se ausente ou malformada, levanta `HTTPException` 401 com detalhe seguro (sem vazar segredos); (c) nao abre sessao de banco nem chama use cases de dominio nesta camada minima.
2. Prever extensao na TASK-3 para validar segredo e escopo; nesta task pode-se usar stub que rejeita sempre exceto formato presente **ou** delegar imediatamente a validacao minima se T1 assim definir.
3. Garantir que handlers que usam apenas esta dependencia nao comitam transacoes de negocio em caso de falha (resposta imediata antes de qualquer servico).
4. Opcional e contido: registrar em `main.py` um router minimo prefixado (ex. `/api/integrador-internal`) com uma rota GET protegida **somente** se for necessario para smoke manual; caso contrario deixar a montagem para testes na TASK-4 para nao antecipar US-7-03.

## comandos_permitidos

- `cd backend && PYTHONPATH=<raiz>:<raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_integrador_auth.py -q` *(apos TASK-4 criar os testes; nesta task pode falhar ate T4)*
- `cd backend && ruff check app/core/integrador_auth.py app/main.py`

## resultado_esperado

- Dependencia importavel por routers futuros (US-7-03) que aplica 401/403 na ausencia de credencial valida, sem efeitos colaterais em dados de negocio.
- Contrato de `request.state` ou objeto retornado documentado na TASK-1 e refletido no codigo (campos podem ser preenchidos na TASK-3).

## testes_ou_validacoes_obrigatorias

- Validacao manual ou teste rapido: chamada sem header/credencial retorna 401 ou 403 conforme decisao, sem erro 500.

## stop_conditions

- Parar se `DECISAO-AUTH-INTEGRADOR.md` nao fechar formato exato da credencial.
- Parar se for necessario persistir integrador nesta task — redireccionar para TASK-3 e garantir US-7-01 `done` se o modelo exigir tabela nova.
