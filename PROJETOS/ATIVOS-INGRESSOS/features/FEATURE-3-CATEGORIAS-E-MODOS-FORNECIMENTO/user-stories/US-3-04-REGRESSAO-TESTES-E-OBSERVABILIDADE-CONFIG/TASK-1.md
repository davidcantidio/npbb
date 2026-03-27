---
doc_id: "TASK-1.md"
user_story_id: "US-3-04-REGRESSAO-TESTES-E-OBSERVABILIDADE-CONFIG"
task_id: "T1"
version: "1.0"
status: "todo"
owner: "PM"
last_updated: "2026-03-26"
depends_on: []
parallel_safe: false
write_scope:
  - "backend/tests/test_ativos_endpoints.py"
  - "backend/tests/conftest.py"
  - "backend/tests/"
tdd_aplicavel: true
---

# TASK-1 - Suite de regressao FEATURE-2 para ativos apos FEATURE-3

## objetivo

Garantir, via testes automatizados, que a **baseline de coexistencia e
comportamento legado** definida em FEATURE-2 se mantem apos as mudancas de
FEATURE-3: em especial, **evento sem configuracao explicita** de categorias/modos
nao quebra contratos nem respostas esperadas para leituras de ativos e
cenarios ja cobertos por testes existentes.

## precondicoes

- [US-3-02](../US-3-02-API-CONFIGURACAO-RBAC-E-CONTRATO-MODOS/README.md) e
  [US-3-03](../US-3-03-UI-CONFIGURACAO-CATEGORIAS-POR-EVENTO/README.md)
  concluidas (`status: done` no frontmatter) antes de executar codigo; caso
  contrario a US-3-04 fica **BLOQUEADA** para implementacao.
- **DRIFT_INDICE (markdown)**: ate 2026-03-26 o frontmatter de US-3-02 e US-3-03
  indicava `todo` enquanto este README da US-3-04 cita ambas como `done`;
  resolver alinhamento antes de tratar precondicoes como satisfeitas.
- Baseline de testes atuais em `backend/tests/test_ativos_endpoints.py` lida;
  PRD/FEATURE-3 apenas para nao inventar escopo alem do 1o criterio G/W/T.

## orquestracao

- `depends_on`: nenhuma task anterior nesta US.
- `parallel_safe`: `false` (base da suite de ativos).
- `write_scope`: ficheiros de teste e fixtures partilhadas sob `backend/tests/`.

## arquivos_a_ler_ou_tocar

- [README.md](./README.md) desta US
- [FEATURE-3.md](../../FEATURE-3.md) *(sec. 4 criterio nao regressao, sec. 6.4)*
- [PRD-ATIVOS-INGRESSOS.md](../../../../PRD-ATIVOS-INGRESSOS.md) *(2.6, coerencia legado)*
- `backend/tests/test_ativos_endpoints.py`
- Documentacao viva de FEATURE-2 / rollout se referenciada nos testes

## testes_red

- testes_a_escrever_primeiro:
  - Um ou mais testes que falhem ate existir assercao explicita de **comportamento
    para evento sem linha de configuracao** de categorias/modos (ou equivalente
    persistido entregue por US-3-01/3-02), alinhado ao default legado acordado;
    e/ou regressao de endpoint de listagem/atribuicao de ativos que hoje ja
    exista mas nao cubra o caso — o red deve provar lacuna antes do green.
- comando_para_rodar:
  - `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_endpoints.py`
  - *(substituir `<RAIZ_DO_REPO>` pelo caminho absoluto da raiz do repositorio)*
- criterio_red:
  - Os testes novos falham antes da correcao de cenarios/fixtures; se passarem
    sem mudanca, rever o criterio de aceite ou o teste.

## passos_atomicos

1. Escrever os testes listados em `testes_red`.
2. Rodar os testes e confirmar falha inicial (red).
3. Ajustar fixtures, dados de seed ou expectativas minimas para refletir o
   contrato legado + FEATURE-3 (sem alterar regra de negocio fora do escopo da
   US-3-04).
4. Rodar a suite focada e confirmar green.
5. Opcional: rodar subset mais largo `pytest tests/` se o tempo de CI
   permitir, para detectar regressoes adjacentes.

## comandos_permitidos

- `cd backend && PYTHONPATH=<RAIZ_DO_REPO>:<RAIZ_DO_REPO>/backend SECRET_KEY=ci-secret-key TESTING=true python -m pytest -q tests/test_ativos_endpoints.py`
- `ruff check` / `ruff format` nos ficheiros de teste tocados

## resultado_esperado

Testes novos ou estendidos documentam e protegem o primeiro criterio Given/When/Then
(regressao atribuivel a FEATURE-2 / eventos legados sem configuracao nova);
`pytest` no alvo acima passa.

## testes_ou_validacoes_obrigatorias

- `pytest` com os casos novos e regressao dos ficheiros tocados em verde.
- Revisao manual de que nenhum assert fixa comportamento nao descrito na US ou
  no manifesto FEATURE-3.

## stop_conditions

- Parar se US-3-02 ou US-3-03 nao estiverem `done` ou se o schema/API ainda nao
  existir para modelar “sem configuracao explicita” de forma testavel.
- Parar se for necessario alterar regra de produto nao coberta pela US-3-04.
