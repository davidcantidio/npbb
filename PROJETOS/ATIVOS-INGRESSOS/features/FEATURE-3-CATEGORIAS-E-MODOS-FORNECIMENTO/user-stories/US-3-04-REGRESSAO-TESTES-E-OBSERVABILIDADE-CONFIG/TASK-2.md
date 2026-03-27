---
doc_id: "TASK-2.md"
user_story_id: "US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG"
task_id: "T2"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on:
  - "T1"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_endpoints.py"
  - "backend/tests/test_ativos_categorias_modos.py"
  - "backend/tests/"
tdd_aplicavel: true
---

# TASK-2 - Testes API por modo canonico e subset de categorias

## objetivo

Exercitar **cenarios de API e/ou integracao** acordados na US-3-02 de forma que,
para cada **modo canonico** (**interno emitido com QR** vs **externo recebido**),
as **leituras observaveis** (payloads de listagem, detalhe ou contrato interno
exposto) **distinguem corretamente** os modos onde o contrato o prometer, e que
**subset parcial do trio** inicial (pista / pista premium / camarote) se
comporta conforme o manifesto FEATURE-3.

## precondicoes

- **TASK-1** (`T1`) em `done`.
- Endpoints e schemas entregues por [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md)
  disponiveis no codigo; sem isso, **BLOQUEADO**.
- Contrato de resposta (campos de modo/categoria) identificavel em
  `backend/app/schemas/` ou documentacao gerada pela OpenAPI.

## orquestracao

- `depends_on`: `T1` (regressao base verde antes de expandir cobertura fina).
- `parallel_safe`: `false`.
- `write_scope`: novos modulos de teste sob `backend/tests/` sem alterar
  regra de negocio fora de asserts/fixtures.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) desta US
- [US-3-02 README.md](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md)
- `backend/app/routers/ativos.py` *(e routers adicionais entregues pela US-3-02)*
- `backend/app/schemas/` *(schemas de ativos / configuracao por evento)*
- `backend/tests/test_ativos_endpoints.py` *(reutilizar fixtures quando possivel)*
- `backend/tests/test_ativos_categorias_modos.py` *(criar se nao existir)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste que cobre **dois modos canonicos** com expectativas distintas nos
    campos prometidos pelo contrato (falha se o backend devolver valores
    ambiguos ou iguais onde deveria haver distincao).
  - Teste que cobre **evento com apenas parte do trio** ativo e valida leitura
    coerente (lista de categorias disponiveis ou equivalente).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_categorias_modos.py`
- criterio_red:
  - Falha antes de dados/contrato completos; se passar sem implementacao na
    US-3-02, revisar se o teste esta acoplado ao comportamento errado.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar e confirmar red.
3. Completar seeds/fixtures (SQLite de teste) para representar modos e subset,
   alinhado aos enums/tabelas da US-3-01/3-02.
4. Rodar ate green sem mudar codigo de producao exceto se um bug bloqueante for
   descoberto (nesse caso, escopar correcao ou abrir follow-up fora desta task).
5. Documentar no corpo da task ou na revisao da US quais endpoints foram
   cobertos.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_categorias_modos.py`
- `ruff check` / `ruff format` nos ficheiros tocados

## resultado_esperado

O segundo criterio Given/When/Then da US-3-04 verificavel por testes automatizados;
ficheiro dedicado (ou modulo claro) para cenarios de modos + subset.

## testes_ou_validacoes_obrigatorias

- `pytest` no modulo alvo em verde.
- Conferencia com OpenAPI ou schema de que os campos assertados sao os do
  contrato publico acordado.

## stop_conditions

- Parar se o contrato da US-3-02 nao expuser distincao testavel entre modos.
- Parar se T1 nao estiver concluida ou se regressao base estiver vermelha.
