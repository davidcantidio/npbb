---
doc_id: "TASK-4.md"
user_story_id: "US-6-03-AJUSTES-PREVISAO-VS-REMANEJAMENTO"
task_id: "T4"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-27"
depends_on:
  - "T3"
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_distribuicao_leituras_api.py"
tdd_aplicavel: true
---

# TASK-4 - Testes automatizados e sobreposicao temporal

## objetivo

Adicionar **testes automatizados** que provem separacao de `aumentado`, `reduzido` e `remanejado` na resposta HTTP da TASK-3, incluindo cenario com **sobreposicao temporal** de operacoes (terceiro Given/When/Then da US), e regredir autenticacao/visibilidade.

## precondicoes

- [TASK-3.md](./TASK-3.md) concluida (`done`): rota e schemas disponiveis.
- `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md` e ADR US-4-05 disponiveis para asserts e comentarios de rastreio.

## orquestracao

- `depends_on`: `T3`.
- `parallel_safe`: `false`.
- `write_scope`: conforme frontmatter; fundir em `tests/test_ingressos_endpoints.py` apenas se o time preferir um unico ficheiro — atualizar entao o frontmatter na revisao.

## arquivos_a_ler_ou_tocar

- `docs/ativos-ingressos/CONTRATO-API-LEITURAS-DISTRIBUICAO-US-6-03.md`
- `backend/tests/test_ativos_distribuicao_leituras_api.py` *(criar)*
- `backend/tests/test_ingressos_endpoints.py` *(padrao de cliente, fixtures, seed)*
- [US-6-01 README](../US-6-01-DISTRIBUICAO-RESPEITANDO-SALDO-DISPONIVEL/README.md) *(consistencia com distribuicao disponivel, se relevante aos dados de teste)*

## testes_red

- testes_a_escrever_primeiro:
  - Teste de API: fixture com evento/recorte que inclua remanejamento e ajustes de previsao (aumento e reducao); resposta GET expoe **valores em campos distintos** e nenhum movimento e contado em dois buckets sem que o teste documente essa excecao (anti-duplicacao).
  - Teste de **sobreposicao temporal**: duas ou mais operacoes na mesma linha do tempo cujo resultado agregado ainda respeita as regras de separacao do contrato TASK-1.
  - Teste de regressao: autenticacao e visibilidade (401/403/404 conforme padrao do router de ingressos).
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<repo-raiz>:<repo-raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_distribuicao_leituras_api.py -q`
- criterio_red:
  - Os testes devem **falhar** antes da implementacao completa de fixtures/dados ou do endpoint; se passarem no primeiro run, parar e rever escopo do teste.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Ajustar fixtures/seeds e asserts ate refletirem o contrato TASK-3 e TASK-1; completar implementacao minima apenas se gap restar na aplicacao.
4. Rodar os testes e confirmar sucesso (green).
5. Refatorar fixtures partilhadas se necessario mantendo a suite green.

## comandos_permitidos

- `cd backend && PYTHONPATH=<repo-raiz>:<repo-raiz>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest tests/test_ativos_distribuicao_leituras_api.py -q`
- `cd backend && ruff check tests/test_ativos_distribuicao_leituras_api.py`

## resultado_esperado

- Suite pytest verde para o novo modulo de testes.
- Criterios Given/When/Then da US cobertos por asserts explicitos ou comentario `pytest.mark` com referencia ao criterio.

## testes_ou_validacoes_obrigatorias

- `pytest tests/test_ativos_distribuicao_leituras_api.py -q` sem falhas.
- Revisao manual: asserts alinhados ao contrato TASK-1 e sem contradicao com ADR US-4-05.

## stop_conditions

- Parar e reportar `BLOQUEADO` se nao for possivel construir dados de teste sem US-6-02/US-4-01 entregues — documentar dependencia; reduzir a smoke de contrato estatico apenas com aprovacao do gate.
- Parar se a rota TASK-3 nao estiver implementada — retornar dependencia a TASK-3.
